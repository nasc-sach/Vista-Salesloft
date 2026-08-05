"""
===============================================================================
AAVA - CodeBuild Stop Tool
===============================================================================

Tool Name:
    CodeBuild Stop Tool

Purpose:
    Safely stop one exact AWS CodeBuild execution.

Primary Consumer:
    CI Build Validation & Failure Handling Agent

Input:
    build_id

Example:
    {
        "build_id": "Salesloft:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }

Responsibilities:
    1. Validate the requested build ID.
    2. Query AWS CodeBuild for the exact current build state.
    3. Verify that the build is still IN_PROGRESS.
    4. Refuse to stop terminal builds.
    5. Invoke stop_build ONLY for the exact requested build.
    6. Capture AWS response evidence.
    7. Re-query CodeBuild after stop request.
    8. Report observed post-stop state.
    9. Preserve UNKNOWN when AWS cannot confirm the result.

Non-Responsibilities:
    - Does NOT retry builds.
    - Does NOT start builds.
    - Does NOT delete builds.
    - Does NOT modify CodeBuild projects.
    - Does NOT modify buildspec.
    - Does NOT stop arbitrary project builds.
    - Does NOT diagnose root cause.
    - Does NOT classify failures.
    - Does NOT declare CI success.
    - Does NOT perform deployment rollback.

Safety Principles:
    - Exact build ID required.
    - Fail closed.
    - Pre-stop state verification required.
    - Terminal builds are NEVER stopped.
    - AWS state is authoritative.
    - stop_build response != guaranteed completed stop.
    - Post-stop verification is required.
    - No project-wide stop behavior.
    - No wildcard behavior.

AWS Authentication:
    Credentials and region must come from AAVA runtime / IAM role /
    standard boto3 credential provider chain.
===============================================================================
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

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

TOOL_NAME = "CodeBuild Stop Tool"
TOOL_VERSION = "1.0.0"


# -----------------------------------------------------------------------------
# CodeBuild states
# -----------------------------------------------------------------------------

STOPPABLE_STATUS = "IN_PROGRESS"

TERMINAL_STATUSES = {
    "SUCCEEDED",
    "FAILED",
    "FAULT",
    "STOPPED",
    "TIMED_OUT",
}


# -----------------------------------------------------------------------------
# Post-stop verification
# -----------------------------------------------------------------------------

# We do NOT wait indefinitely.
#
# stop_build is a request to AWS. CodeBuild may need some time to transition
# from IN_PROGRESS to STOPPED.
#
# Therefore:
#
#     STOPPED      -> confirmed
#     IN_PROGRESS  -> stop requested but transition not yet confirmed
#     other state  -> preserve exact AWS observation
#
# Keep this bounded because AAVA tools should not block for long periods.

DEFAULT_VERIFICATION_ATTEMPTS = 3
DEFAULT_VERIFICATION_DELAY_SECONDS = 2

MAX_VERIFICATION_ATTEMPTS = 5
MAX_VERIFICATION_DELAY_SECONDS = 5


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("aava.codebuild_stop_tool")

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
# GENERAL UTILITIES
# =============================================================================

def utc_now_iso() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def datetime_to_iso(value: Any) -> Optional[str]:

    if value is None:
        return None

    if isinstance(value, datetime):

        try:
            return value.isoformat()

        except Exception:
            return str(value)

    return str(value)


def sanitize_error_message(
    value: Any,
    max_length: int = 4000,
) -> str:

    if value is None:
        return "Unknown error"

    text = str(value)

    if len(text) > max_length:

        return (
            text[:max_length]
            + "...[TRUNCATED]"
        )

    return text


def get_aws_error_code(
    error: ClientError,
) -> Optional[str]:

    try:

        return (
            error.response
            .get("Error", {})
            .get("Code")
        )

    except Exception:

        return None


def get_aws_error_message(
    error: ClientError,
) -> Optional[str]:

    try:

        return (
            error.response
            .get("Error", {})
            .get("Message")
        )

    except Exception:

        return None


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class CodeBuildStopToolSchema(BaseModel):
    """
    Input schema for CodeBuildStopTool.

    Only the exact CodeBuild build ID is required.

    The tool independently verifies current AWS state before performing
    the mutating stop operation.
    """

    build_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Exact AWS CodeBuild build identifier to stop. "
            "Example: "
            "'Salesloft:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'. "
            "The tool revalidates the build state before stopping it."
        ),
    )


# =============================================================================
# BUILD RETRIEVAL
# =============================================================================

def get_exact_build(
    client: Any,
    build_id: str,
) -> Dict[str, Any]:
    """
    Retrieve one exact CodeBuild execution.

    The function does not search by project name and does not choose
    the newest build.

    This prevents accidentally stopping a different build.
    """

    logger.info(
        "Querying exact CodeBuild execution | build_id=%s",
        build_id,
    )

    response = client.batch_get_builds(
        ids=[build_id]
    )

    builds = response.get(
        "builds",
        [],
    ) or []

    not_found = response.get(
        "buildsNotFound",
        [],
    ) or []

    if build_id in not_found:

        return {
            "found": False,
            "reason": "BUILD_NOT_FOUND",
            "build": None,
        }

    if not builds:

        return {
            "found": False,
            "reason": "BUILD_NOT_RETURNED",
            "build": None,
        }

    if len(builds) != 1:

        return {
            "found": False,
            "reason": "UNEXPECTED_BUILD_COUNT",
            "build": None,
        }

    build = builds[0]

    actual_id = build.get("id")

    if actual_id != build_id:

        logger.error(
            "Build identity mismatch | requested=%s | returned=%s",
            build_id,
            actual_id,
        )

        return {
            "found": False,
            "reason": "BUILD_ID_MISMATCH",
            "build": build,
        }

    return {
        "found": True,
        "reason": None,
        "build": build,
    }


# =============================================================================
# BUILD SUMMARY
# =============================================================================

def summarize_build(
    build: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Extract only useful build evidence for output.
    """

    if not build:
        return None

    return {

        "build_id": build.get(
            "id"
        ),

        "build_arn": build.get(
            "arn"
        ),

        "project_name": build.get(
            "projectName"
        ),

        "build_number": build.get(
            "buildNumber"
        ),

        "build_status": build.get(
            "buildStatus"
        ),

        "current_phase": build.get(
            "currentPhase"
        ),

        "source_version": build.get(
            "sourceVersion"
        ),

        "resolved_source_version": build.get(
            "resolvedSourceVersion"
        ),

        "start_time": datetime_to_iso(
            build.get("startTime")
        ),

        "end_time": datetime_to_iso(
            build.get("endTime")
        ),
    }


# =============================================================================
# ERROR RESPONSE
# =============================================================================

def build_error_response(
    *,
    build_id: Optional[str],
    error_type: str,
    error_code: str,
    message: str,
    aws_error_code: Optional[str] = None,
    retryable: Optional[bool] = None,
    pre_stop_build: Optional[Dict[str, Any]] = None,
) -> str:

    output = {

        "schema_version": "1.0",

        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "operation": "STOP_CODEBUILD_BUILD",
            "read_only": False,
        },

        "request": {
            "build_id": build_id,
        },

        "execution": {
            "status": "ERROR",
            "timestamp": utc_now_iso(),

            "stop_api_invoked": False,
            "stop_request_accepted": False,
            "stop_confirmed": False,
        },

        "pre_stop_state": (
            summarize_build(
                pre_stop_build
            )
        ),

        "post_stop_state": None,

        "error": {

            "type": error_type,

            "code": error_code,

            "aws_error_code": (
                aws_error_code
            ),

            "message": sanitize_error_message(
                message
            ),

            "retryable": retryable,
        },

        "safety": {

            "exact_build_identity_required": True,

            "pre_stop_state_verified": (
                pre_stop_build is not None
            ),

            "terminal_build_stop_prevented": True,

            "project_wide_stop_allowed": False,

            "wildcard_stop_allowed": False,
        },

        "decision_support": {

            "stop_confirmed": False,

            "recommended_next_action": (
                "PRESERVE_CURRENT_BUILD_STATE_AND_REVIEW_ERROR"
            ),
        },

        "unknown_areas": [
            "The requested stop operation was not authoritatively completed."
        ],
    }

    return json.dumps(
        output,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


# =============================================================================
# SAFE NO-OP RESPONSE
# =============================================================================

def build_noop_response(
    *,
    build_id: str,
    build: Dict[str, Any],
    reason_code: str,
    reason: str,
) -> str:
    """
    Return a successful safety decision where no AWS mutation was made.

    Example:
        Build already FAILED.

    That is NOT a tool failure.

    The tool correctly refused an unnecessary/unsafe mutation.
    """

    status = build.get(
        "buildStatus"
    )

    output = {

        "schema_version": "1.0",

        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "operation": "STOP_CODEBUILD_BUILD",
            "read_only": False,
        },

        "request": {
            "build_id": build_id,
        },

        "execution": {

            "status": "NO_ACTION",

            "timestamp": utc_now_iso(),

            "stop_api_invoked": False,

            "stop_request_accepted": False,

            "stop_confirmed": (
                status == "STOPPED"
            ),

            "reason_code": reason_code,

            "reason": reason,
        },

        "pre_stop_state": (
            summarize_build(build)
        ),

        "post_stop_state": (
            summarize_build(build)
        ),

        "safety": {

            "exact_build_identity_verified": True,

            "pre_stop_state_verified": True,

            "terminal_build_stop_prevented": True,

            "project_wide_stop_allowed": False,

            "wildcard_stop_allowed": False,
        },

        "decision_support": {

            "stop_required": False,

            "stop_confirmed": (
                status == "STOPPED"
            ),

            "authoritative_build_status": (
                status
            ),

            "recommended_next_action": (
                "CONTINUE_FAILURE_HANDLING"
                if status in {
                    "FAILED",
                    "FAULT",
                    "TIMED_OUT",
                }
                else
                "NO_STOP_ACTION_REQUIRED"
            ),
        },

        "unknown_areas": [],
    }

    return json.dumps(
        output,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


# =============================================================================
# POST-STOP VERIFICATION
# =============================================================================

def verify_stop_state(
    *,
    client: Any,
    build_id: str,
    attempts: int,
    delay_seconds: int,
) -> Dict[str, Any]:
    """
    Re-query CodeBuild after stop_build.

    IMPORTANT:

    stop_build returning successfully means AWS accepted/processed the API
    request. It does NOT necessarily mean the build has already transitioned
    to STOPPED.

    Therefore we verify state independently.
    """

    observations = []

    for attempt in range(
        1,
        attempts + 1,
    ):

        if attempt > 1:

            time.sleep(
                delay_seconds
            )

        logger.info(
            "Post-stop verification | build_id=%s | attempt=%s/%s",
            build_id,
            attempt,
            attempts,
        )

        result = get_exact_build(
            client,
            build_id,
        )

        if not result.get("found"):

            observations.append({

                "attempt": attempt,

                "timestamp": utc_now_iso(),

                "retrieval_status": "UNKNOWN",

                "reason": result.get(
                    "reason"
                ),

                "build_status": None,
            })

            continue

        build = result.get(
            "build"
        )

        status = build.get(
            "buildStatus"
        )

        observations.append({

            "attempt": attempt,

            "timestamp": utc_now_iso(),

            "retrieval_status": "SUCCESS",

            "build_status": status,

            "current_phase": build.get(
                "currentPhase"
            ),
        })

        if status == "STOPPED":

            return {

                "confirmed": True,

                "final_status": status,

                "final_build": build,

                "observations": observations,
            }

        # ---------------------------------------------------------------------
        # If AWS has transitioned to another terminal state before stop was
        # completed, preserve that authoritative state.
        # ---------------------------------------------------------------------

        if status in TERMINAL_STATUSES:

            return {

                "confirmed": False,

                "final_status": status,

                "final_build": build,

                "observations": observations,
            }

    # -------------------------------------------------------------------------
    # Verification window exhausted.
    # -------------------------------------------------------------------------

    final_build = None
    final_status = None

    if observations:

        final_status = observations[-1].get(
            "build_status"
        )

    try:

        final_lookup = get_exact_build(
            client,
            build_id,
        )

        if final_lookup.get("found"):

            final_build = final_lookup.get(
                "build"
            )

            final_status = final_build.get(
                "buildStatus"
            )

    except Exception:

        # Do not override the stop operation simply because final verification
        # itself failed.
        pass

    return {

        "confirmed": (
            final_status == "STOPPED"
        ),

        "final_status": final_status,

        "final_build": final_build,

        "observations": observations,
    }


# =============================================================================
# MAIN TOOL
# =============================================================================

class CodeBuildStopTool(BaseTool):
    """
    Guarded CodeBuild stop tool.

    The tool performs exactly one mutating operation:

        AWS CodeBuild stop_build(buildId=<exact build ID>)

    but only after independently verifying that the build is still
    IN_PROGRESS.
    """

    name: str = TOOL_NAME

    description: str = (
        "Safely stops one exact AWS CodeBuild execution. "
        "The tool independently retrieves the current build state before "
        "performing any mutation and invokes AWS stop_build only when the "
        "exact requested build is still IN_PROGRESS. Terminal builds are "
        "never stopped. After requesting the stop, the tool re-queries AWS "
        "to determine whether STOPPED was actually observed. It does not "
        "retry builds, start builds, modify projects, diagnose failures, "
        "or perform deployment rollback."
    )

    args_schema: Type[BaseModel] = (
        CodeBuildStopToolSchema
    )

    def _run(
        self,
        build_id: str,
        **kwargs: Any,
    ) -> str:

        started = time.monotonic()

        # =====================================================================
        # 1. VALIDATE INPUT
        # =====================================================================

        normalized_build_id = (
            build_id.strip()
            if isinstance(
                build_id,
                str,
            )
            else ""
        )

        if not normalized_build_id:

            return build_error_response(

                build_id=None,

                error_type="INPUT_ERROR",

                error_code="INVALID_BUILD_ID",

                message=(
                    "build_id must be a non-empty exact "
                    "AWS CodeBuild build identifier."
                ),

                retryable=False,
            )

        logger.info(
            "Starting guarded CodeBuild stop operation | build_id=%s",
            normalized_build_id,
        )

        # =====================================================================
        # 2. CREATE AWS CLIENT
        # =====================================================================

        try:

            session = boto3.session.Session()

            region = session.region_name

            client = session.client(
                "codebuild"
            )

        except NoCredentialsError:

            logger.exception(
                "AWS credentials unavailable."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_CREDENTIAL_ERROR",

                error_code="NO_AWS_CREDENTIALS",

                message=(
                    "AWS credentials were not available "
                    "to the AAVA runtime."
                ),

                retryable=False,
            )

        except PartialCredentialsError as exc:

            logger.exception(
                "Partial AWS credentials."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_CREDENTIAL_ERROR",

                error_code="PARTIAL_AWS_CREDENTIALS",

                message=str(exc),

                retryable=False,
            )

        except Exception as exc:

            logger.exception(
                "AWS client initialization failed."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_CLIENT_ERROR",

                error_code=(
                    "AWS_CLIENT_INITIALIZATION_FAILED"
                ),

                message=str(exc),

                retryable=None,
            )

        # =====================================================================
        # 3. PRE-STOP AUTHORITATIVE STATE CHECK
        # =====================================================================

        try:

            pre_result = get_exact_build(
                client,
                normalized_build_id,
            )

        except EndpointConnectionError as exc:

            logger.exception(
                "CodeBuild endpoint connection failed "
                "during pre-stop verification."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_CONNECTION_ERROR",

                error_code=(
                    "CODEBUILD_ENDPOINT_CONNECTION_FAILED"
                ),

                message=str(exc),

                retryable=True,
            )

        except ClientError as exc:

            code = get_aws_error_code(
                exc
            )

            message = get_aws_error_message(
                exc
            )

            logger.exception(
                "CodeBuild pre-stop API error | code=%s",
                code,
            )

            retryable = None

            if code in {
                "AccessDenied",
                "AccessDeniedException",
                "UnrecognizedClientException",
                "InvalidClientTokenId",
            }:

                retryable = False

            elif code in {
                "ThrottlingException",
                "TooManyRequestsException",
                "ServiceUnavailableException",
                "InternalServerException",
            }:

                retryable = True

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_API_ERROR",

                error_code=(
                    "PRE_STOP_BUILD_VERIFICATION_FAILED"
                ),

                aws_error_code=code,

                message=(
                    message
                    or str(exc)
                ),

                retryable=retryable,
            )

        except BotoCoreError as exc:

            logger.exception(
                "AWS SDK error during pre-stop verification."
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
                "Unexpected pre-stop verification error."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="UNEXPECTED_ERROR",

                error_code=(
                    "PRE_STOP_VERIFICATION_ERROR"
                ),

                message=str(exc),

                retryable=None,
            )

        # =====================================================================
        # 4. VERIFY BUILD EXISTS
        # =====================================================================

        if not pre_result.get(
            "found"
        ):

            reason = pre_result.get(
                "reason"
            )

            logger.warning(
                "Requested build not safely retrievable | "
                "build_id=%s | reason=%s",
                normalized_build_id,
                reason,
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="BUILD_VALIDATION_ERROR",

                error_code=(
                    reason
                    or "BUILD_NOT_FOUND"
                ),

                message=(
                    "The requested build could not be "
                    "authoritatively verified. "
                    "No stop operation was performed."
                ),

                retryable=False,
            )

        pre_build = pre_result[
            "build"
        ]

        pre_status = pre_build.get(
            "buildStatus"
        )

        logger.info(
            "Pre-stop state verified | "
            "build_id=%s | status=%s | phase=%s",
            normalized_build_id,
            pre_status,
            pre_build.get(
                "currentPhase"
            ),
        )

        # =====================================================================
        # 5. TERMINAL BUILD GUARD
        # =====================================================================

        if pre_status in TERMINAL_STATUSES:

            logger.info(
                "Stop prevented because build is terminal | "
                "build_id=%s | status=%s",
                normalized_build_id,
                pre_status,
            )

            if pre_status == "STOPPED":

                reason_code = (
                    "BUILD_ALREADY_STOPPED"
                )

                reason = (
                    "The requested build is already STOPPED. "
                    "No additional stop operation is required."
                )

            else:

                reason_code = (
                    "BUILD_ALREADY_TERMINAL"
                )

                reason = (
                    f"The requested build is already in "
                    f"terminal state '{pre_status}'. "
                    f"Calling stop_build would be unnecessary "
                    f"and is therefore blocked."
                )

            return build_noop_response(

                build_id=normalized_build_id,

                build=pre_build,

                reason_code=reason_code,

                reason=reason,
            )

        # =====================================================================
        # 6. UNKNOWN / UNSUPPORTED STATE GUARD
        # =====================================================================

        if pre_status != STOPPABLE_STATUS:

            logger.warning(
                "Stop blocked because build status is not explicitly "
                "stoppable | build_id=%s | status=%s",
                normalized_build_id,
                pre_status,
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="STATE_GUARD",

                error_code=(
                    "BUILD_STATE_NOT_STOPPABLE"
                ),

                message=(
                    f"Build status '{pre_status}' is not "
                    f"explicitly approved for stopping. "
                    f"Only '{STOPPABLE_STATUS}' builds may "
                    f"be stopped by this tool."
                ),

                retryable=False,

                pre_stop_build=pre_build,
            )

        # =====================================================================
        # 7. EXECUTE EXACT STOP
        # =====================================================================

        stop_requested_at = (
            utc_now_iso()
        )

        logger.warning(
            "Invoking AWS stop_build | build_id=%s",
            normalized_build_id,
        )

        try:

            stop_response = client.stop_build(
                id=normalized_build_id
            )

        except EndpointConnectionError as exc:

            logger.exception(
                "CodeBuild endpoint connection failed "
                "during stop operation."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_CONNECTION_ERROR",

                error_code=(
                    "STOP_BUILD_ENDPOINT_CONNECTION_FAILED"
                ),

                message=str(exc),

                retryable=True,

                pre_stop_build=pre_build,
            )

        except ClientError as exc:

            code = get_aws_error_code(
                exc
            )

            message = get_aws_error_message(
                exc
            )

            logger.exception(
                "AWS stop_build failed | "
                "build_id=%s | code=%s",
                normalized_build_id,
                code,
            )

            retryable = None

            if code in {
                "AccessDenied",
                "AccessDeniedException",
                "UnrecognizedClientException",
                "InvalidClientTokenId",
            }:

                retryable = False

            elif code in {
                "ThrottlingException",
                "TooManyRequestsException",
                "ServiceUnavailableException",
                "InternalServerException",
            }:

                retryable = True

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_API_ERROR",

                error_code=(
                    "STOP_BUILD_REQUEST_FAILED"
                ),

                aws_error_code=code,

                message=(
                    message
                    or str(exc)
                ),

                retryable=retryable,

                pre_stop_build=pre_build,
            )

        except BotoCoreError as exc:

            logger.exception(
                "AWS SDK error during stop_build."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="AWS_SDK_ERROR",

                error_code=(
                    "STOP_BUILD_BOTOCORE_ERROR"
                ),

                message=str(exc),

                retryable=None,

                pre_stop_build=pre_build,
            )

        except Exception as exc:

            logger.exception(
                "Unexpected stop_build error."
            )

            return build_error_response(

                build_id=normalized_build_id,

                error_type="UNEXPECTED_ERROR",

                error_code=(
                    "STOP_BUILD_UNEXPECTED_ERROR"
                ),

                message=str(exc),

                retryable=None,

                pre_stop_build=pre_build,
            )

        # =====================================================================
        # 8. VALIDATE STOP RESPONSE IDENTITY
        # =====================================================================

        stop_build_object = (
            stop_response.get(
                "build",
                {}
            )
            or {}
        )

        returned_build_id = (
            stop_build_object.get(
                "id"
            )
        )

        identity_verified = (
            returned_build_id
            == normalized_build_id
        )

        if not identity_verified:

            logger.error(
                "stop_build response identity mismatch | "
                "requested=%s | returned=%s",
                normalized_build_id,
                returned_build_id,
            )

        # =====================================================================
        # 9. POST-STOP VERIFICATION
        # =====================================================================

        try:

            verification = verify_stop_state(

                client=client,

                build_id=normalized_build_id,

                attempts=(
                    DEFAULT_VERIFICATION_ATTEMPTS
                ),

                delay_seconds=(
                    DEFAULT_VERIFICATION_DELAY_SECONDS
                ),
            )

        except Exception as exc:

            logger.exception(
                "Post-stop verification failed."
            )

            verification = {

                "confirmed": False,

                "final_status": None,

                "final_build": None,

                "observations": [],

                "verification_error": (
                    sanitize_error_message(
                        exc
                    )
                ),
            }

        # =====================================================================
        # 10. CLASSIFY STOP RESULT
        # =====================================================================

        stop_confirmed = (
            verification.get(
                "confirmed",
                False,
            )
        )

        final_status = (
            verification.get(
                "final_status"
            )
        )

        final_build = (
            verification.get(
                "final_build"
            )
        )

        if stop_confirmed:

            execution_status = (
                "STOP_CONFIRMED"
            )

            recommended_next_action = (
                "CONTINUE_FAILURE_ANALYSIS_WITH_STOPPED_BUILD"
            )

            result_reason = (
                "AWS accepted the stop request and subsequent "
                "CodeBuild verification observed status STOPPED."
            )

            unknown_areas = []

        elif final_status in {
            "SUCCEEDED",
            "FAILED",
            "FAULT",
            "TIMED_OUT",
        }:

            execution_status = (
                "TERMINAL_STATE_OBSERVED"
            )

            recommended_next_action = (
                "CONTINUE_FAILURE_HANDLING_USING_AUTHORITATIVE_FINAL_STATE"
            )

            result_reason = (
                "The stop request was issued, but subsequent "
                f"verification observed terminal status '{final_status}' "
                "rather than STOPPED. Preserve the AWS state exactly."
            )

            unknown_areas = []

        elif final_status == "IN_PROGRESS":

            execution_status = (
                "STOP_REQUESTED_NOT_YET_CONFIRMED"
            )

            recommended_next_action = (
                "RECHECK_BUILD_STATUS"
            )

            result_reason = (
                "AWS stop_build was invoked successfully, but the "
                "bounded verification window did not yet observe STOPPED."
            )

            unknown_areas = [
                (
                    "The final completion of the stop transition "
                    "was not confirmed within the bounded verification window."
                )
            ]

        else:

            execution_status = (
                "STOP_RESULT_UNKNOWN"
            )

            recommended_next_action = (
                "RECHECK_BUILD_STATUS_BEFORE_ANY_FURTHER_MUTATION"
            )

            result_reason = (
                "AWS accepted the stop request, but the final build "
                "state could not be authoritatively determined."
            )

            unknown_areas = [
                (
                    "The authoritative post-stop build state "
                    "could not be confirmed."
                )
            ]

        # =====================================================================
        # 11. FINAL OUTPUT
        # =====================================================================

        elapsed_ms = round(
            (
                time.monotonic()
                - started
            )
            * 1000,
            3,
        )

        output = {

            "schema_version": "1.0",

            "tool": {

                "name": TOOL_NAME,

                "version": TOOL_VERSION,

                "operation": (
                    "STOP_CODEBUILD_BUILD"
                ),

                "read_only": False,
            },

            "request": {

                "build_id": (
                    normalized_build_id
                ),
            },

            "execution": {

                "status": (
                    execution_status
                ),

                "started_at": (
                    stop_requested_at
                ),

                "completed_at": (
                    utc_now_iso()
                ),

                "duration_ms": (
                    elapsed_ms
                ),

                "aws_region": (
                    region
                ),

                "stop_api_invoked": True,

                "stop_request_accepted": True,

                "stop_confirmed": (
                    stop_confirmed
                ),

                "reason": (
                    result_reason
                ),
            },

            "pre_stop_state": (
                summarize_build(
                    pre_build
                )
            ),

            "stop_response": {

                "returned_build_id": (
                    returned_build_id
                ),

                "requested_build_id": (
                    normalized_build_id
                ),

                "identity_verified": (
                    identity_verified
                ),

                "returned_build_status": (
                    stop_build_object.get(
                        "buildStatus"
                    )
                ),

                "returned_current_phase": (
                    stop_build_object.get(
                        "currentPhase"
                    )
                ),
            },

            "post_stop_verification": {

                "verification_attempts": (
                    verification.get(
                        "observations",
                        []
                    )
                ),

                "stop_confirmed": (
                    stop_confirmed
                ),

                "final_observed_status": (
                    final_status
                ),
            },

            "post_stop_state": (
                summarize_build(
                    final_build
                )
            ),

            "safety": {

                "exact_build_identity_required": True,

                "exact_build_identity_verified_before_stop": True,

                "pre_stop_state_verified": True,

                "required_pre_stop_status": (
                    STOPPABLE_STATUS
                ),

                "observed_pre_stop_status": (
                    pre_status
                ),

                "terminal_build_stop_prevented": True,

                "project_wide_stop_allowed": False,

                "wildcard_stop_allowed": False,

                "retry_build_allowed": False,

                "start_build_allowed": False,

                "project_modification_allowed": False,

                "deployment_rollback_performed": False,
            },

            "decision_support": {

                "stop_requested": True,

                "stop_confirmed": (
                    stop_confirmed
                ),

                "authoritative_final_status": (
                    final_status
                ),

                "recommended_next_action": (
                    recommended_next_action
                ),
            },

            "unknown_areas": (
                unknown_areas
            ),
        }

        logger.info(
            "CodeBuild stop operation completed | "
            "build_id=%s | pre_status=%s | "
            "stop_confirmed=%s | final_status=%s",
            normalized_build_id,
            pre_status,
            stop_confirmed,
            final_status,
        )

        return json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


# =============================================================================
# END
# =============================================================================