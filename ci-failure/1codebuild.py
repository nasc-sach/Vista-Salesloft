"""
===============================================================================
AAVA - CodeBuild Status Tool
===============================================================================

Tool Name:
    CodeBuild Status Tool

Purpose:
    Retrieve authoritative AWS CodeBuild execution status and metadata for a
    specific build execution.

Primary Consumer:
    CI Build Validation & Failure Handling Agent

Design Principles:
    - READ ONLY.
    - Never modifies/stops/retries a build.
    - Never diagnoses root cause.
    - Never declares overall CI success.
    - Never fabricates missing AWS information.
    - Preserves UNKNOWN/null values.
    - Returns structured JSON suitable for downstream AAVA agents/tools.
    - Uses AWS CodeBuild as the authoritative source for build state.
    - Exposes resolved_source_version for immutable artifact correlation.

Expected Input:
    {
        "build_id": "Salesloft:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }

Important:
    AWS credentials/region should be supplied through the AAVA/AWS runtime
    environment, IAM role, or supported secret mechanism. Do not hard-code
    credentials in this file.
===============================================================================
"""

import json
import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
)
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# =============================================================================
# CONSTANTS
# =============================================================================

TOOL_NAME = "CodeBuild Status Tool"
TOOL_VERSION = "1.0.0"

# CodeBuild terminal states.
TERMINAL_SUCCESS_STATUSES = {
    "SUCCEEDED"
}

TERMINAL_FAILURE_STATUSES = {
    "FAILED",
    "FAULT",
    "STOPPED",
    "TIMED_OUT",
}

KNOWN_BUILD_STATUSES = {
    "IN_PROGRESS",
    "SUCCEEDED",
    "FAILED",
    "FAULT",
    "STOPPED",
    "TIMED_OUT",
}

KNOWN_PHASE_TYPES = {
    "SUBMITTED",
    "QUEUED",
    "PROVISIONING",
    "DOWNLOAD_SOURCE",
    "INSTALL",
    "PRE_BUILD",
    "BUILD",
    "POST_BUILD",
    "UPLOAD_ARTIFACTS",
    "FINALIZING",
    "COMPLETED",
}


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("aava.codebuild_status_tool")

if not logger.handlers:
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def datetime_to_iso(value: Any) -> Optional[str]:
    """
    Safely convert datetime-like AWS values to ISO-8601 strings.

    Returns None when no usable value exists.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        try:
            return value.isoformat()
        except Exception:
            return str(value)

    return str(value)


def calculate_duration_seconds(
    start_time: Any,
    end_time: Any
) -> Optional[float]:
    """
    Calculate build duration from AWS timestamps.

    If the build is still running, duration is calculated from start time
    until the current UTC time.

    Returns None if duration cannot be determined.
    """
    if not isinstance(start_time, datetime):
        return None

    try:
        effective_end = end_time

        if not isinstance(effective_end, datetime):
            effective_end = datetime.now(timezone.utc)

        # Normalize naive timestamps if ever encountered.
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        if effective_end.tzinfo is None:
            effective_end = effective_end.replace(tzinfo=timezone.utc)

        duration = (effective_end - start_time).total_seconds()

        if duration < 0:
            return None

        return round(duration, 3)

    except Exception:
        return None


def safe_string(value: Any) -> Optional[str]:
    """
    Convert a value to string without inventing defaults.
    """
    if value is None:
        return None

    try:
        return str(value)
    except Exception:
        return None


def sanitize_error_message(message: Any) -> str:
    """
    Basic defensive sanitization for error messages.

    This tool intentionally does not return AWS credentials, authorization
    tokens, or secret environment variables.

    AWS SDK exception messages normally do not contain credentials, but this
    method limits unexpectedly large output.
    """
    if message is None:
        return "Unknown error"

    text = str(message)

    # Prevent enormous exception payloads from entering the agent context.
    max_length = 4000

    if len(text) > max_length:
        text = text[:max_length] + "...[TRUNCATED]"

    return text


def get_error_code(error: ClientError) -> Optional[str]:
    """Safely extract AWS ClientError code."""
    try:
        return error.response.get("Error", {}).get("Code")
    except Exception:
        return None


def get_error_message(error: ClientError) -> Optional[str]:
    """Safely extract AWS ClientError message."""
    try:
        return error.response.get("Error", {}).get("Message")
    except Exception:
        return None


# =============================================================================
# PHASE PROCESSING
# =============================================================================

def process_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a raw AWS CodeBuild phase into a stable machine-readable object.

    No root-cause inference is performed.
    """

    phase_type = phase.get("phaseType")
    phase_status = phase.get("phaseStatus")

    contexts: List[Dict[str, Any]] = []

    for context in phase.get("contexts", []) or []:
        contexts.append({
            "status_code": context.get("statusCode"),
            "message": context.get("message"),
        })

    start_time = phase.get("startTime")
    end_time = phase.get("endTime")

    duration = phase.get("durationInSeconds")

    # AWS normally supplies durationInSeconds for completed phases.
    # Calculate it only when AWS didn't supply it.
    if duration is None:
        duration = calculate_duration_seconds(start_time, end_time)

    return {
        "phase_type": phase_type,
        "phase_status": phase_status,
        "start_time": datetime_to_iso(start_time),
        "end_time": datetime_to_iso(end_time),
        "duration_seconds": duration,
        "contexts": contexts,
        "phase_type_recognized": (
            phase_type in KNOWN_PHASE_TYPES
            if phase_type is not None
            else False
        ),
    }


def extract_current_phase(
    build: Dict[str, Any],
    phases: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Determine the current/most relevant phase using AWS-provided information.

    Priority:
        1. build.currentPhase
        2. Last IN_PROGRESS phase
        3. Last phase returned by AWS

    This is structural derivation, not failure diagnosis.
    """

    aws_current_phase = build.get("currentPhase")

    if aws_current_phase:
        return aws_current_phase

    for phase in reversed(phases):
        if phase.get("phase_status") == "IN_PROGRESS":
            return phase.get("phase_type")

    if phases:
        return phases[-1].get("phase_type")

    return None


def extract_failed_phases(
    phases: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Return phases that AWS explicitly reports as failed/faulted/timed out/stopped.

    This does not infer root cause.
    """

    failure_states = {
        "FAILED",
        "FAULT",
        "TIMED_OUT",
        "STOPPED",
    }

    failed: List[Dict[str, Any]] = []

    for phase in phases:
        if phase.get("phase_status") in failure_states:
            failed.append({
                "phase_type": phase.get("phase_type"),
                "phase_status": phase.get("phase_status"),
                "contexts": phase.get("contexts", []),
            })

    return failed


# =============================================================================
# SOURCE PROCESSING
# =============================================================================

def extract_source_information(build: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract source metadata from CodeBuild.

    resolved_source_version is particularly important because downstream
    artifact validation should use it for immutable ECR tagging.
    """

    source = build.get("source", {}) or {}

    secondary_sources = []

    for secondary in build.get("secondarySources", []) or []:
        secondary_sources.append({
            "source_identifier": secondary.get("sourceIdentifier"),
            "type": secondary.get("type"),
            "location": secondary.get("location"),
        })

    secondary_source_versions = []

    for version in build.get("secondarySourceVersions", []) or []:
        secondary_source_versions.append({
            "source_identifier": version.get("sourceIdentifier"),
            "source_version": version.get("sourceVersion"),
        })

    return {
        "source_version": build.get("sourceVersion"),
        "resolved_source_version": build.get("resolvedSourceVersion"),

        "primary_source": {
            "type": source.get("type"),
            "location": source.get("location"),
            "git_clone_depth": source.get("gitCloneDepth"),
            "report_build_status": source.get("reportBuildStatus"),
        },

        "secondary_sources": secondary_sources,
        "secondary_source_versions": secondary_source_versions,
    }


# =============================================================================
# LOG PROCESSING
# =============================================================================

def extract_log_information(build: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract CloudWatch/CodeBuild log references.

    This tool does NOT retrieve log contents. That responsibility belongs to
    CodeBuildLogsTool.
    """

    logs = build.get("logs", {}) or {}

    return {
        "group_name": logs.get("groupName"),
        "stream_name": logs.get("streamName"),
        "deep_link": logs.get("deepLink"),
        "cloudwatch_logs_status": logs.get("cloudWatchLogs", {}).get("status"),
        "cloudwatch_group_name": (
            logs.get("cloudWatchLogs", {}).get("groupName")
        ),
        "cloudwatch_stream_name": (
            logs.get("cloudWatchLogs", {}).get("streamName")
        ),
        "s3_logs_status": logs.get("s3Logs", {}).get("status"),
        "s3_logs_location": logs.get("s3Logs", {}).get("location"),
    }


# =============================================================================
# ARTIFACT METADATA PROCESSING
# =============================================================================

def extract_artifact_information(build: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract artifact metadata exposed by CodeBuild.

    IMPORTANT:
        This does NOT verify artifact existence in S3/ECR.

        Verification belongs to CIArtifactValidationTool.
    """

    artifacts = build.get("artifacts", {}) or {}

    secondary_artifacts: List[Dict[str, Any]] = []

    for artifact in build.get("secondaryArtifacts", []) or []:
        secondary_artifacts.append({
            "artifact_identifier": artifact.get("artifactIdentifier"),
            "location": artifact.get("location"),
            "sha256sum": artifact.get("sha256sum"),
            "md5sum": artifact.get("md5sum"),
        })

    return {
        "primary_artifact": {
            "location": artifacts.get("location"),
            "sha256sum": artifacts.get("sha256sum"),
            "md5sum": artifacts.get("md5sum"),
            "artifact_identifier": artifacts.get("artifactIdentifier"),
        },
        "secondary_artifacts": secondary_artifacts,
        "verification_performed": False,
        "verification_note": (
            "Artifact metadata is reported by CodeBuild only. "
            "Existence and source-revision correlation must be verified by "
            "CIArtifactValidationTool."
        ),
    }


# =============================================================================
# ENVIRONMENT PROCESSING
# =============================================================================

def extract_environment_information(build: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract non-secret CodeBuild environment metadata.

    Environment variables are intentionally NOT returned because they may
    contain credentials, tokens, passwords, or other secrets.
    """

    environment = build.get("environment", {}) or {}

    return {
        "type": environment.get("type"),
        "image": environment.get("image"),
        "compute_type": environment.get("computeType"),
        "privileged_mode": environment.get("privilegedMode"),
        "image_pull_credentials_type": (
            environment.get("imagePullCredentialsType")
        ),
        "environment_variables_exposed": False,
        "environment_variables_note": (
            "Environment variables intentionally omitted to prevent "
            "accidental secret exposure."
        ),
    }


# =============================================================================
# STATUS CLASSIFICATION
# =============================================================================

def classify_build_status(status: Optional[str]) -> Dict[str, Any]:
    """
    Deterministically classify CodeBuild status.

    This classification concerns CodeBuild execution only.
    It does NOT represent overall CI success.
    """

    if status == "SUCCEEDED":
        return {
            "status_recognized": True,
            "is_terminal": True,
            "is_codebuild_success": True,
            "is_codebuild_failure": False,
            "requires_artifact_validation": True,
            "requires_failure_log_analysis": False,
        }

    if status in TERMINAL_FAILURE_STATUSES:
        return {
            "status_recognized": True,
            "is_terminal": True,
            "is_codebuild_success": False,
            "is_codebuild_failure": True,
            "requires_artifact_validation": False,
            "requires_failure_log_analysis": True,
        }

    if status == "IN_PROGRESS":
        return {
            "status_recognized": True,
            "is_terminal": False,
            "is_codebuild_success": False,
            "is_codebuild_failure": False,
            "requires_artifact_validation": False,
            "requires_failure_log_analysis": False,
        }

    return {
        "status_recognized": False,
        "is_terminal": False,
        "is_codebuild_success": False,
        "is_codebuild_failure": False,
        "requires_artifact_validation": False,
        "requires_failure_log_analysis": False,
    }


# =============================================================================
# ERROR RESPONSE FACTORY
# =============================================================================

def build_error_response(
    *,
    build_id: Optional[str],
    error_type: str,
    error_code: str,
    message: str,
    aws_error_code: Optional[str] = None,
    retryable: Optional[bool] = None,
) -> str:
    """
    Produce a stable JSON error contract.

    Tool errors are deliberately kept distinct from CodeBuild failures.
    """

    payload = {
        "schema_version": "1.0",
        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
        },
        "query": {
            "build_id": build_id,
        },
        "retrieval": {
            "status": "ERROR",
            "timestamp": utc_now_iso(),
        },
        "error": {
            "type": error_type,
            "code": error_code,
            "aws_error_code": aws_error_code,
            "message": sanitize_error_message(message),
            "retryable": retryable,
        },
        "build": None,
        "decision_support": {
            "authoritative_build_status_available": False,
            "overall_ci_success_determined": False,
            "promotion_allowed": False,
            "reason": (
                "Authoritative CodeBuild state could not be retrieved. "
                "The CI pipeline must fail closed."
            ),
        },
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


# =============================================================================
# PYDANTIC INPUT SCHEMA
# =============================================================================

class CodeBuildStatusToolSchema(BaseModel):
    """
    Input schema for CodeBuildStatusTool.
    """

    build_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Exact AWS CodeBuild build identifier to inspect. "
            "Example: 'Salesloft:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'. "
            "Do not provide only the project name."
        ),
    )


# =============================================================================
# TOOL IMPLEMENTATION
# =============================================================================

class CodeBuildStatusTool(BaseTool):
    """
    Read-only AWS CodeBuild status and metadata inspection tool.

    This tool intentionally does not decide whether the complete CI process
    succeeded. A successful CodeBuild execution must still undergo immutable
    artifact verification by CIArtifactValidationTool.
    """

    name: str = TOOL_NAME

    description: str = (
        "Retrieves authoritative AWS CodeBuild execution status, phase details, "
        "source revision, resolved source revision, timestamps, logs metadata, "
        "environment metadata, and CodeBuild artifact metadata for an exact "
        "build ID. This is a read-only evidence tool. It does not diagnose "
        "root causes, stop builds, verify ECR/S3 artifacts, or declare overall "
        "CI success."
    )

    args_schema: Type[BaseModel] = CodeBuildStatusToolSchema

    def _run(
        self,
        build_id: str,
        **kwargs: Any,
    ) -> str:
        """
        Execute CodeBuild status retrieval.
        """

        request_started = time.monotonic()

        logger.info(
            "Starting CodeBuild status retrieval | build_id=%s",
            build_id,
        )

        # ---------------------------------------------------------------------
        # 1. Input validation
        # ---------------------------------------------------------------------

        normalized_build_id = (
            build_id.strip()
            if isinstance(build_id, str)
            else ""
        )

        if not normalized_build_id:
            logger.error("Invalid build_id supplied.")

            return build_error_response(
                build_id=None,
                error_type="INPUT_ERROR",
                error_code="INVALID_BUILD_ID",
                message="build_id must be a non-empty string.",
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 2. Create AWS client
        # ---------------------------------------------------------------------

        try:
            logger.info("Creating AWS CodeBuild client.")

            # Region/credentials are resolved through boto3's normal credential
            # provider chain:
            # IAM role -> environment -> shared config -> supported runtime.
            client = boto3.client("codebuild")

        except NoCredentialsError:
            logger.exception("AWS credentials were not available.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CREDENTIAL_ERROR",
                error_code="NO_AWS_CREDENTIALS",
                message=(
                    "AWS credentials were not available to the tool runtime."
                ),
                retryable=False,
            )

        except PartialCredentialsError as exc:
            logger.exception("Incomplete AWS credentials.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CREDENTIAL_ERROR",
                error_code="PARTIAL_AWS_CREDENTIALS",
                message=str(exc),
                retryable=False,
            )

        except Exception as exc:
            logger.exception("Unable to create CodeBuild client.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CLIENT_ERROR",
                error_code="CODEBUILD_CLIENT_CREATION_FAILED",
                message=str(exc),
                retryable=None,
            )

        # ---------------------------------------------------------------------
        # 3. Query AWS
        # ---------------------------------------------------------------------

        try:
            logger.info(
                "Calling CodeBuild batch_get_builds | build_id=%s",
                normalized_build_id,
            )

            response = client.batch_get_builds(
                ids=[normalized_build_id]
            )

            logger.info(
                "CodeBuild batch_get_builds completed | build_id=%s",
                normalized_build_id,
            )

        except NoCredentialsError:
            logger.exception(
                "AWS credentials unavailable during CodeBuild request."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CREDENTIAL_ERROR",
                error_code="NO_AWS_CREDENTIALS",
                message=(
                    "AWS credentials were not available during "
                    "CodeBuild status retrieval."
                ),
                retryable=False,
            )

        except PartialCredentialsError as exc:
            logger.exception(
                "Partial AWS credentials during CodeBuild request."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CREDENTIAL_ERROR",
                error_code="PARTIAL_AWS_CREDENTIALS",
                message=str(exc),
                retryable=False,
            )

        except EndpointConnectionError as exc:
            logger.exception(
                "Unable to connect to AWS CodeBuild endpoint."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CONNECTION_ERROR",
                error_code="CODEBUILD_ENDPOINT_CONNECTION_FAILED",
                message=str(exc),
                retryable=True,
            )

        except ClientError as exc:
            aws_code = get_error_code(exc)
            aws_message = get_error_message(exc)

            logger.exception(
                "AWS ClientError retrieving build | "
                "build_id=%s | aws_error=%s",
                normalized_build_id,
                aws_code,
            )

            # AccessDenied should not be interpreted as a failed build.
            retryable = None

            if aws_code in {
                "AccessDenied",
                "AccessDeniedException",
                "UnrecognizedClientException",
                "InvalidClientTokenId",
            }:
                retryable = False

            elif aws_code in {
                "ThrottlingException",
                "TooManyRequestsException",
                "ServiceUnavailableException",
                "InternalServerException",
            }:
                retryable = True

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_API_ERROR",
                error_code="CODEBUILD_STATUS_REQUEST_FAILED",
                aws_error_code=aws_code,
                message=aws_message or str(exc),
                retryable=retryable,
            )

        except BotoCoreError as exc:
            logger.exception(
                "BotoCore error retrieving CodeBuild status."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_SDK_ERROR",
                error_code="BOTOCORE_ERROR",
                message=str(exc),
                retryable=None,
            )

        except Exception as exc:
            logger.exception(
                "Unexpected error retrieving CodeBuild status."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="UNEXPECTED_ERROR",
                error_code="UNEXPECTED_STATUS_TOOL_ERROR",
                message=str(exc),
                retryable=None,
            )

        # ---------------------------------------------------------------------
        # 4. Validate AWS response
        # ---------------------------------------------------------------------

        try:
            builds = response.get("builds", []) or []
            builds_not_found = response.get("buildsNotFound", []) or []

            if normalized_build_id in builds_not_found:
                logger.warning(
                    "AWS explicitly reported build as not found | build_id=%s",
                    normalized_build_id,
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="NOT_FOUND",
                    error_code="BUILD_NOT_FOUND",
                    message=(
                        "AWS CodeBuild reported that the supplied build ID "
                        "was not found."
                    ),
                    retryable=False,
                )

            if not builds:
                logger.warning(
                    "No build returned by AWS | build_id=%s",
                    normalized_build_id,
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="NOT_FOUND",
                    error_code="BUILD_NOT_RETURNED",
                    message=(
                        "AWS CodeBuild returned no build information for the "
                        "supplied build ID."
                    ),
                    retryable=False,
                )

            # We query exactly one ID. Do not silently process multiple builds.
            if len(builds) != 1:
                logger.error(
                    "Unexpected number of builds returned | count=%s",
                    len(builds),
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="RESPONSE_VALIDATION_ERROR",
                    error_code="UNEXPECTED_BUILD_COUNT",
                    message=(
                        "Expected exactly one build from CodeBuild but "
                        f"received {len(builds)}."
                    ),
                    retryable=False,
                )

            build = builds[0]

        except Exception as exc:
            logger.exception(
                "Failed while validating CodeBuild response."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="RESPONSE_PROCESSING_ERROR",
                error_code="INVALID_CODEBUILD_RESPONSE",
                message=str(exc),
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 5. Process authoritative build evidence
        # ---------------------------------------------------------------------

        try:
            actual_build_id = build.get("id")
            build_status = build.get("buildStatus")

            logger.info(
                "Processing build | build_id=%s | status=%s",
                actual_build_id,
                build_status,
            )

            # Ensure AWS did not unexpectedly return another build.
            if (
                actual_build_id
                and actual_build_id != normalized_build_id
            ):
                logger.error(
                    "Build ID mismatch | requested=%s | returned=%s",
                    normalized_build_id,
                    actual_build_id,
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="RESPONSE_VALIDATION_ERROR",
                    error_code="BUILD_ID_MISMATCH",
                    message=(
                        "The build ID returned by AWS does not match the "
                        "requested build ID."
                    ),
                    retryable=False,
                )

            processed_phases = [
                process_phase(phase)
                for phase in (build.get("phases", []) or [])
            ]

            current_phase = extract_current_phase(
                build,
                processed_phases,
            )

            failed_phases = extract_failed_phases(
                processed_phases
            )

            status_classification = classify_build_status(
                build_status
            )

            start_time = build.get("startTime")
            end_time = build.get("endTime")

            duration_seconds = calculate_duration_seconds(
                start_time,
                end_time,
            )

            source_info = extract_source_information(build)
            logs_info = extract_log_information(build)
            artifact_info = extract_artifact_information(build)
            environment_info = extract_environment_information(build)

            build_arn = build.get("arn")
            project_name = build.get("projectName")

            # -----------------------------------------------------------------
            # Important:
            #
            # This is only decision SUPPORT.
            #
            # The tool intentionally refuses to declare overall CI success.
            # -----------------------------------------------------------------

            if build_status == "SUCCEEDED":
                recommended_next_action = (
                    "VALIDATE_IMMUTABLE_CI_ARTIFACTS"
                )

                decision_reason = (
                    "CodeBuild execution succeeded. Overall CI success has "
                    "not been established because backend ECR image, frontend "
                    "ECR image, S3 artifact, and source-revision correlation "
                    "must still be verified."
                )

            elif build_status in TERMINAL_FAILURE_STATUSES:
                recommended_next_action = (
                    "RETRIEVE_CODEBUILD_FAILURE_LOGS"
                )

                decision_reason = (
                    "CodeBuild reached a terminal non-success state. "
                    "Retrieve authoritative build logs before diagnosing "
                    "the failure."
                )

            elif build_status == "IN_PROGRESS":
                recommended_next_action = (
                    "WAIT_OR_EVALUATE_TIMEOUT_POLICY"
                )

                decision_reason = (
                    "CodeBuild execution is still non-terminal. "
                    "Do not forward the build downstream."
                )

            else:
                recommended_next_action = (
                    "BLOCK_AND_REVIEW_UNKNOWN_BUILD_STATUS"
                )

                decision_reason = (
                    "CodeBuild returned an unrecognized or unavailable "
                    "status. Fail closed and do not forward downstream."
                )

            request_duration_ms = round(
                (time.monotonic() - request_started) * 1000,
                3,
            )

            output = {
                "schema_version": "1.0",

                "tool": {
                    "name": TOOL_NAME,
                    "version": TOOL_VERSION,
                    "operation": "GET_CODEBUILD_STATUS",
                    "read_only": True,
                },

                "query": {
                    "requested_build_id": normalized_build_id,
                },

                "retrieval": {
                    "status": "SUCCESS",
                    "timestamp": utc_now_iso(),
                    "request_duration_ms": request_duration_ms,
                    "authoritative_source": "AWS CodeBuild",
                },

                "build": {
                    "build_id": actual_build_id,
                    "build_arn": build_arn,
                    "project_name": project_name,

                    "build_status": build_status,

                    "status_recognized": (
                        status_classification[
                            "status_recognized"
                        ]
                    ),

                    "is_terminal": (
                        status_classification["is_terminal"]
                    ),

                    "is_codebuild_success": (
                        status_classification[
                            "is_codebuild_success"
                        ]
                    ),

                    "is_codebuild_failure": (
                        status_classification[
                            "is_codebuild_failure"
                        ]
                    ),

                    "current_phase": current_phase,

                    "start_time": datetime_to_iso(start_time),
                    "end_time": datetime_to_iso(end_time),
                    "duration_seconds": duration_seconds,

                    "initiator": build.get("initiator"),

                    "build_complete": build.get("buildComplete"),

                    "queued_timeout_in_minutes": (
                        build.get("queuedTimeoutInMinutes")
                    ),

                    "build_timeout_in_minutes": (
                        build.get("timeoutInMinutes")
                    ),
                },

                "source": source_info,

                "phases": {
                    "current_phase": current_phase,
                    "all_phases": processed_phases,
                    "failed_phases": failed_phases,
                    "total_phases_observed": len(processed_phases),
                },

                "logs": logs_info,

                "codebuild_artifact_metadata": artifact_info,

                "environment": environment_info,

                "decision_support": {
                    "authoritative_build_status_available": (
                        build_status is not None
                    ),

                    "requires_artifact_validation": (
                        status_classification[
                            "requires_artifact_validation"
                        ]
                    ),

                    "requires_failure_log_analysis": (
                        status_classification[
                            "requires_failure_log_analysis"
                        ]
                    ),

                    # Deliberately false here.
                    # Only CIArtifactValidationTool + CI gate may establish it.
                    "overall_ci_success_determined": False,

                    # Status tool alone NEVER authorizes promotion.
                    "promotion_allowed": False,

                    "recommended_next_action": (
                        recommended_next_action
                    ),

                    "reason": decision_reason,
                },

                "unknown_areas": [],
            }

            # -----------------------------------------------------------------
            # 6. Explicit unknown preservation
            # -----------------------------------------------------------------

            if build_status is None:
                output["unknown_areas"].append(
                    "AWS CodeBuild did not provide buildStatus."
                )

            elif build_status not in KNOWN_BUILD_STATUSES:
                output["unknown_areas"].append(
                    "AWS CodeBuild returned an unrecognized build status: "
                    f"{build_status}"
                )

            if source_info.get("resolved_source_version") is None:
                output["unknown_areas"].append(
                    "resolved_source_version was not provided by CodeBuild. "
                    "Immutable artifact correlation cannot yet be established."
                )

            if current_phase is None:
                output["unknown_areas"].append(
                    "Current CodeBuild phase could not be determined."
                )

            if logs_info.get("group_name") is None:
                output["unknown_areas"].append(
                    "Primary CloudWatch log group was not available in "
                    "CodeBuild metadata."
                )

            if logs_info.get("stream_name") is None:
                output["unknown_areas"].append(
                    "Primary CloudWatch log stream was not available in "
                    "CodeBuild metadata."
                )

            logger.info(
                "CodeBuild status retrieval successful | "
                "build_id=%s | status=%s | phase=%s | "
                "resolved_source_version=%s | next_action=%s",
                actual_build_id,
                build_status,
                current_phase,
                source_info.get("resolved_source_version"),
                recommended_next_action,
            )

            return json.dumps(
                output,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        except Exception as exc:
            logger.error(
                "Unexpected processing error | build_id=%s | error=%s",
                normalized_build_id,
                str(exc),
            )

            logger.debug(
                "Traceback:\n%s",
                traceback.format_exc(),
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="PROCESSING_ERROR",
                error_code="CODEBUILD_RESPONSE_PROCESSING_FAILED",
                message=str(exc),
                retryable=False,
            )