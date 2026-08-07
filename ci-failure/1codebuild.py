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
    This tool uses hardcoded AWS credentials. These should be replaced with
    secure credential management in production environments.
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

# AWS Credentials (hardcoded - security risk acknowledged)
# WARNING: These credentials are stored in plaintext. In production environments,
# use AWS IAM roles, environment variables, or secure secret management systems.
AWS_ACCESS_KEY_ID = "PLACEHOLDER_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "PLACEHOLDER_SECRET_ACCESS_KEY"
AWS_REGION = "eu-north-1"

# Note: Replace the PLACEHOLDER values above with actual AWS credentials.
# This approach is NOT recommended for production use due to security risks:
# - Credentials exposed in source code
# - No automatic rotation
# - Risk of accidental commits to version control


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
    Extract CodeBuild environment metadata including environment variables.

    Environment variables (name, value, type) are included for artifact
    tagging and verification purposes.
    """

    environment = build.get("environment", {}) or {}
    
    env_vars = []
    for var in environment.get("environmentVariables", []) or []:
        env_vars.append({
            "name": var.get("name"),
            "value": var.get("value"),
            "type": var.get("type"),
        })

    return {
        "compute_type": environment.get("type"),
        "image": environment.get("image"),
        "privileged_mode": environment.get("privilegedMode"),
        "image_pull_credentials_type": environment.get("imagePullCredentialsType"),
        "environmentVariables": env_vars,
    }


# =============================================================================
# STATUS CLASSIFICATION
# =============================================================================

def classify_build_status(status: Optional[str]) -> Dict[str, Any]:
    """
    Classify CodeBuild status into semantic flags.

    This is purely status classification, not root-cause inference.
    """

    if status is None:
        return {
            "is_terminal": False,
            "is_success": False,
            "is_failure": False,
            "is_in_progress": False,
            "is_recognized": False,
        }

    is_recognized = status in KNOWN_BUILD_STATUSES

    is_terminal = (
        status in TERMINAL_SUCCESS_STATUSES or
        status in TERMINAL_FAILURE_STATUSES
    )

    is_success = status in TERMINAL_SUCCESS_STATUSES
    is_failure = status in TERMINAL_FAILURE_STATUSES
    is_in_progress = status == "IN_PROGRESS"

    return {
        "is_terminal": is_terminal,
        "is_success": is_success,
        "is_failure": is_failure,
        "is_in_progress": is_in_progress,
        "is_recognized": is_recognized,
    }


# =============================================================================
# STRUCTURED ERROR RESPONSES
# =============================================================================

def build_error_response(
    *,
    build_id: str,
    error_type: str,
    error_code: str,
    message: str,
    aws_error_code: Optional[str] = None,
    retryable: bool = False
) -> str:
    """
    Generate a consistent JSON error payload.
    """

    payload = {
        "status": "ERROR",
        "build_id": build_id,
        "error": {
            "error_type": error_type,
            "error_code": error_code,
            "message": message,
            "aws_error_code": aws_error_code,
            "retryable": retryable,
        },
        "timestamp": utc_now_iso(),
        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
        },
    }

    try:
        return json.dumps(payload, indent=2, default=str)

    except Exception:
        # Absolute fallback.
        return json.dumps({
            "status": "ERROR",
            "error": "Could not serialize error response",
        })


# =============================================================================
# PYDANTIC SCHEMA
# =============================================================================

class CodeBuildStatusToolSchema(BaseModel):
    """
    Input schema for CodeBuildStatusTool.
    """

    build_id: str = Field(
        ...,
        description=(
            "AWS CodeBuild execution ID (e.g., 'Salesloft:<UUID>')."
        )
    )


# =============================================================================
# CREWAI TOOL IMPLEMENTATION
# =============================================================================

class CodeBuildStatusTool(BaseTool):
    """
    Tool for retrieving authoritative AWS CodeBuild build status.

    See module-level docstring for detailed behavior, design principles, and
    consumer responsibilities.
    """

    name: str = "CodeBuild Status Tool"

    description: str = (
        "Retrieve authoritative AWS CodeBuild execution status and metadata. "
        "This tool is READ ONLY. It never modifies or retries builds. "
        "It preserves AWS state exactly as reported. "
        "Use this for validating build completion status before proceeding "
        "with artifact validation or deployment decisions."
    )

    args_schema: Type[BaseModel] = CodeBuildStatusToolSchema

    def _run(
        self,
        build_id: str,
        **kwargs
    ) -> str:
        """
        Retrieve and return authoritative CodeBuild status metadata.

        Returns:
            JSON string containing build status or structured error.
        """

        request_started = time.perf_counter()

        # ---------------------------------------------------------------------
        # 1. Validate input
        # ---------------------------------------------------------------------

        normalized_build_id = (build_id or "").strip()

        if not normalized_build_id:
            return build_error_response(
                build_id=normalized_build_id,
                error_type="INVALID_REQUEST",
                error_code="MISSING_BUILD_ID",
                message="build_id was not provided or was empty.",
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 2. Create AWS client
        # ---------------------------------------------------------------------

        try:
            logger.info("Creating AWS CodeBuild client with hardcoded credentials.")

            # Using hardcoded credentials (security risk acknowledged).
            # Replace PLACEHOLDER values with actual credentials.
            client = boto3.client(
                "codebuild",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )

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
                error_code="CLIENT_CREATION_FAILURE",
                message=sanitize_error_message(exc),
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 3. Retrieve build information
        # ---------------------------------------------------------------------

        try:
            logger.info(
                f"Requesting build information for build_id={normalized_build_id}"
            )

            response = client.batch_get_builds(ids=[normalized_build_id])

        except EndpointConnectionError:
            logger.exception("Unable to connect to AWS CodeBuild endpoint.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CONNECTIVITY_ERROR",
                error_code="ENDPOINT_CONNECTION_ERROR",
                message=(
                    "Could not establish connection to AWS CodeBuild. "
                    "Verify network connectivity and region configuration."
                ),
                retryable=True,
            )

        except ClientError as error:
            logger.exception(
                f"AWS ClientError while retrieving build: {normalized_build_id}"
            )

            aws_code = get_error_code(error)
            aws_message = get_error_message(error)

            # Classify common retryable conditions.
            retryable_codes = {
                "RequestTimeout",
                "ServiceUnavailable",
                "ThrottlingException",
                "TooManyRequestsException",
                "RequestLimitExceeded",
            }

            retryable = aws_code in retryable_codes if aws_code else False

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_API_ERROR",
                error_code="CLIENT_ERROR",
                message=sanitize_error_message(aws_message or str(error)),
                aws_error_code=aws_code,
                retryable=retryable,
            )

        except BotoCoreError as error:
            logger.exception("BotoCoreError while calling batch_get_builds.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_BOTOCORE_ERROR",
                error_code="BOTOCORE_ERROR",
                message=sanitize_error_message(error),
                retryable=True,
            )

        except Exception as error:
            logger.exception("Unexpected error calling batch_get_builds.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="UNEXPECTED_ERROR",
                error_code="BATCH_GET_BUILDS_EXCEPTION",
                message=sanitize_error_message(error),
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 4. Parse and validate AWS response
        # ---------------------------------------------------------------------

        try:
            builds = response.get("builds", [])
            builds_not_found = response.get("buildsNotFound", [])

            if normalized_build_id in builds_not_found:
                logger.warning(
                    f"Build not found: {normalized_build_id}"
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="BUILD_NOT_FOUND",
                    error_code="BUILD_NOT_FOUND",
                    message=(
                        f"AWS CodeBuild returned no build with ID: "
                        f"{normalized_build_id}"
                    ),
                    retryable=False,
                )

            if not builds:
                logger.warning(
                    f"Response contained zero builds for {normalized_build_id}"
                )

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="BUILD_NOT_FOUND",
                    error_code="EMPTY_BUILD_RESPONSE",
                    message=(
                        "AWS CodeBuild returned zero builds. "
                        "Verify the build ID is correct."
                    ),
                    retryable=False,
                )

            if len(builds) > 1:
                logger.warning(
                    f"AWS returned multiple builds for {normalized_build_id}. "
                    "Using first result."
                )

        except Exception as error:
            logger.exception("Error parsing batch_get_builds response structure.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="RESPONSE_PARSE_ERROR",
                error_code="RESPONSE_PARSE_FAILURE",
                message=sanitize_error_message(error),
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 5. Extract build metadata
        # ---------------------------------------------------------------------

        try:
            build = builds[0]

            # -----------------------------------------------------------------
            # 5a. Basic identification
            # -----------------------------------------------------------------

            actual_build_id = build.get("id")
            build_status = build.get("buildStatus")

            if actual_build_id is None:
                logger.error("AWS returned build with no 'id' field.")

                return build_error_response(
                    build_id=normalized_build_id,
                    error_type="INVALID_AWS_RESPONSE",
                    error_code="MISSING_BUILD_ID",
                    message="AWS returned a build with no ID field.",
                    retryable=False,
                )

            if build_status is None:
                logger.warning(
                    f"Build {actual_build_id} has no buildStatus. "
                    "Proceeding with status=UNKNOWN."
                )

            logger.info(
                f"Retrieved build: id={actual_build_id}, status={build_status}"
            )

            # -----------------------------------------------------------------
            # 5b. Phases
            # -----------------------------------------------------------------

            processed_phases = [
                process_phase(p) for p in build.get("phases", []) or []
            ]

            current_phase = extract_current_phase(build, processed_phases)

            # Identify phases AWS explicitly reported as failed.
            failed_phases = extract_failed_phases(processed_phases)

            # Classify status without inventing conclusions.
            status_classification = classify_build_status(build_status)

            # Timestamps
            start_time = build.get("startTime")
            end_time = build.get("endTime")

            duration_seconds = calculate_duration_seconds(start_time, end_time)

            # Source information (including resolved_source_version for ECR tagging).
            source_info = extract_source_information(build)
            logs_info = extract_log_information(build)
            artifact_info = extract_artifact_information(build)
            environment_info = extract_environment_information(build)

            build_arn = build.get("arn")
            project_name = build.get("projectName")

            # -----------------------------------------------------------------
            # 5c. Recommended next action (structural, not inferential)
            # -----------------------------------------------------------------

            recommended_next_action = "UNKNOWN"

            decision_reason = (
                "The tool cannot recommend next actions without "
                "consulting broader CI orchestration."
            )

            if status_classification["is_success"]:
                recommended_next_action = "PROCEED_TO_ARTIFACT_VALIDATION"

                decision_reason = (
                    "Build succeeded. Verify artifact presence/tagging "
                    "with CIArtifactValidationTool."
                )

            elif status_classification["is_failure"]:
                recommended_next_action = "RETRIEVE_LOGS_FOR_FAILURE_ANALYSIS"

                decision_reason = (
                    "Build failed. Retrieve logs using CodeBuildLogsTool. "
                    "Do not proceed to artifact validation."
                )

            elif status_classification["is_in_progress"]:
                recommended_next_action = "WAIT"

                decision_reason = (
                    "Build is still running. Poll again later."
                )

            else:
                recommended_next_action = "UNKNOWN"

                decision_reason = (
                    "Build status is not recognized or is ambiguous. "
                    "Consult CI orchestration."
                )

        except Exception as error:
            logger.exception("Failed to extract build metadata.")

            return build_error_response(
                build_id=normalized_build_id,
                error_type="METADATA_EXTRACTION_ERROR",
                error_code="METADATA_EXTRACTION_FAILURE",
                message=sanitize_error_message(error),
                retryable=False,
            )

        # ---------------------------------------------------------------------
        # 6. Assemble final output
        # ---------------------------------------------------------------------

        request_duration_ms = round(
            (time.perf_counter() - request_started) * 1000, 3
        )

        try:
            output = {
                "status": "SUCCESS",
                
                # Top-level metadata for Tool 2 compatibility
                "metadata": {
                    "build_id": actual_build_id,
                    "build_arn": build_arn,
                    "project_name": project_name,
                    "build_status": build_status,
                    "build_number": build.get("buildNumber"),
                    "resolved_source_version": source_info.get("resolved_source_version"),
                    "source_version": source_info.get("source_version"),
                    "current_phase": current_phase,
                    "start_time": datetime_to_iso(start_time),
                    "end_time": datetime_to_iso(end_time),
                    "duration_seconds": duration_seconds,
                    "aws_region": AWS_REGION,
                    
                    "artifacts": {
                        "location": artifact_info["primary_artifact"]["location"],
                        "sha256sum": artifact_info["primary_artifact"]["sha256sum"],
                        "md5sum": artifact_info["primary_artifact"]["md5sum"],
                    },
                    
                    "environment": {
                        "type": environment_info.get("compute_type"),
                        "image": environment_info.get("image"),
                        "privileged_mode": environment_info.get("privileged_mode"),
                        "environmentVariables": environment_info.get("environmentVariables", []),
                    },
                },

                "build": {
                    "build_id": actual_build_id,
                    "build_arn": build_arn,
                    "project_name": project_name,

                    "build_status": build_status,
                    "status_classification": status_classification,

                    "current_phase": current_phase,
                    "failed_phases": failed_phases,

                    "start_time": datetime_to_iso(start_time),
                    "end_time": datetime_to_iso(end_time),
                    "duration_seconds": duration_seconds,

                    "phases": processed_phases,
                },

                "source": source_info,
                "logs": logs_info,
                "artifacts": artifact_info,
                "environment": environment_info,

                "recommended_next_action": recommended_next_action,
                "decision_reason": decision_reason,

                "retrieval_metadata": {
                    "request_duration_ms": request_duration_ms,
                    "timestamp": utc_now_iso(),
                    "aws_region": AWS_REGION,
                },

                "tool": {
                    "name": TOOL_NAME,
                    "version": TOOL_VERSION,
                },
            }

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