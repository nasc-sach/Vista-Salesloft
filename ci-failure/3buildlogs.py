"""
===============================================================================
AAVA - CodeBuild Logs Tool
===============================================================================

Tool Name:
    CodeBuild Logs Tool

Purpose:
    Retrieve authoritative AWS CodeBuild / CloudWatch log evidence for an
    exact CodeBuild execution.

Primary Consumer:
    CI Build Validation & Failure Handling Agent

Input:
    build_id only

Example:
    {
        "build_id": "Salesloft:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }

Responsibilities:
    1. Query CodeBuild for authoritative build metadata.
    2. Discover CloudWatch log group and stream from the build itself.
    3. Retrieve log events from CloudWatch.
    4. Preserve timestamps and ordering.
    5. Extract useful error/warning evidence without fabricating diagnosis.
    6. Bound output size to protect agent context.
    7. Report truncation explicitly.
    8. Preserve unknown states.
    9. Never expose AWS credentials or environment secrets intentionally.

Non-Responsibilities:
    - Does NOT diagnose root cause.
    - Does NOT classify CI failure.
    - Does NOT retry builds.
    - Does NOT stop builds.
    - Does NOT modify logs.
    - Does NOT declare CI success/failure.
    - Does NOT fabricate missing log evidence.

AWS Authentication:
    Credentials and region must come from the AAVA runtime, IAM role,
    environment, or standard boto3 credential provider chain.
===============================================================================
"""

import json
import logging
import time
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

TOOL_NAME = "CodeBuild Logs Tool"
TOOL_VERSION = "1.0.0"

DEFAULT_MAX_LOG_EVENTS = 1000

# Protect AAVA/LLM context from enormous logs.
ABSOLUTE_MAX_LOG_EVENTS = 5000

# Individual log messages can occasionally become enormous.
MAX_SINGLE_MESSAGE_LENGTH = 8000

# Limit number of extracted signal lines.
MAX_ERROR_SIGNALS = 100
MAX_WARNING_SIGNALS = 100


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("aava.codebuild_logs_tool")

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
# SIGNAL TERMS
# =============================================================================

# These terms are used ONLY for evidence extraction.
#
# Finding one of these strings does NOT establish a root cause.

ERROR_SIGNAL_TERMS = [
    "error",
    "failed",
    "failure",
    "fatal",
    "exception",
    "traceback",
    "accessdenied",
    "access denied",
    "not authorized",
    "unauthorized",
    "forbidden",
    "permission denied",
    "cannot find",
    "could not resolve",
    "module not found",
    "command not found",
    "no such file",
    "no such directory",
    "out of memory",
    "oom",
    "killed",
    "timed out",
    "timeout",
    "connection refused",
    "connection reset",
    "network unreachable",
    "no basic auth credentials",
    "authentication required",
    "non-zero exit",
    "exit status",
    "exited with",
]

WARNING_SIGNAL_TERMS = [
    "warning",
    "warn:",
    "deprecated",
    "deprecation",
]


# =============================================================================
# SENSITIVE VALUE SIGNALS
# =============================================================================

# Conservative list used for log redaction.
#
# We do NOT attempt sophisticated secret discovery because aggressive regex
# logic can corrupt useful evidence. Instead, obvious key=value style secret
# lines are masked.

SENSITIVE_KEYWORDS = [
    "aws_secret_access_key",
    "aws_access_key_id",
    "aws_session_token",
    "authorization:",
    "password=",
    "password:",
    "passwd=",
    "passwd:",
    "token=",
    "token:",
    "secret=",
    "secret:",
    "api_key=",
    "apikey=",
    "private_key",
]


# =============================================================================
# GENERAL UTILITIES
# =============================================================================

def utc_now_iso() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def epoch_ms_to_iso(value: Any) -> Optional[str]:
    """
    Convert CloudWatch epoch milliseconds to ISO-8601 UTC.
    """

    if value is None:
        return None

    try:
        timestamp = float(value) / 1000.0

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).isoformat()

    except Exception:
        return None


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
    """
    Bound exception output.
    """

    if value is None:
        return "Unknown error"

    text = str(value)

    if len(text) > max_length:
        return text[:max_length] + "...[TRUNCATED]"

    return text


def get_aws_error_code(
    error: ClientError,
) -> Optional[str]:

    try:
        return error.response.get(
            "Error",
            {},
        ).get("Code")

    except Exception:
        return None


def get_aws_error_message(
    error: ClientError,
) -> Optional[str]:

    try:
        return error.response.get(
            "Error",
            {},
        ).get("Message")

    except Exception:
        return None


# =============================================================================
# LOG MESSAGE SAFETY
# =============================================================================

def truncate_message(
    message: str,
) -> Dict[str, Any]:
    """
    Bound an individual log event.

    Returns both the message and whether truncation occurred.
    """

    if message is None:
        return {
            "message": "",
            "truncated": False,
        }

    text = str(message)

    if len(text) <= MAX_SINGLE_MESSAGE_LENGTH:
        return {
            "message": text,
            "truncated": False,
        }

    return {
        "message": (
            text[:MAX_SINGLE_MESSAGE_LENGTH]
            + "...[MESSAGE_TRUNCATED]"
        ),
        "truncated": True,
    }


def redact_sensitive_log_line(
    message: str,
) -> Dict[str, Any]:
    """
    Perform conservative secret redaction.

    This intentionally avoids rewriting normal error messages.

    If a line appears to contain an obvious secret-bearing key, the value
    portion is masked.

    Example:

        AWS_SECRET_ACCESS_KEY=abcdef

    becomes:

        AWS_SECRET_ACCESS_KEY=[REDACTED]

    Evidence that redaction occurred is explicitly returned.
    """

    if not message:
        return {
            "message": message or "",
            "redacted": False,
        }

    original = str(message)
    lowered = original.lower()

    for keyword in SENSITIVE_KEYWORDS:

        keyword_lower = keyword.lower()

        if keyword_lower not in lowered:
            continue

        # -------------------------------------------------------------
        # Try "=" redaction
        # -------------------------------------------------------------

        if "=" in original:
            key, _, _ = original.partition("=")

            return {
                "message": f"{key}=[REDACTED]",
                "redacted": True,
            }

        # -------------------------------------------------------------
        # Try ":" redaction
        # -------------------------------------------------------------

        if ":" in original:
            key, _, _ = original.partition(":")

            return {
                "message": f"{key}: [REDACTED]",
                "redacted": True,
            }

        # -------------------------------------------------------------
        # Conservative fallback
        # -------------------------------------------------------------

        return {
            "message": "[POTENTIALLY_SENSITIVE_LOG_LINE_REDACTED]",
            "redacted": True,
        }

    return {
        "message": original,
        "redacted": False,
    }


# =============================================================================
# LOG SIGNAL DETECTION
# =============================================================================

def detect_signal_type(
    message: str,
) -> Optional[str]:
    """
    Detect whether a log line contains an error/warning signal.

    IMPORTANT:
        This is NOT root-cause classification.

    It simply helps the downstream agent find potentially relevant evidence.
    """

    if not message:
        return None

    lowered = message.lower()

    for term in ERROR_SIGNAL_TERMS:
        if term in lowered:
            return "ERROR_SIGNAL"

    for term in WARNING_SIGNAL_TERMS:
        if term in lowered:
            return "WARNING_SIGNAL"

    return None


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class CodeBuildLogsToolSchema(BaseModel):
    """
    Input schema for CodeBuildLogsTool.
    """

    build_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Exact AWS CodeBuild build identifier. "
            "The tool discovers the authoritative CloudWatch log group "
            "and stream directly from CodeBuild."
        ),
    )

    max_log_events: int = Field(
        DEFAULT_MAX_LOG_EVENTS,
        ge=1,
        le=ABSOLUTE_MAX_LOG_EVENTS,
        description=(
            "Maximum number of CloudWatch log events to return. "
            f"Default: {DEFAULT_MAX_LOG_EVENTS}. "
            f"Maximum: {ABSOLUTE_MAX_LOG_EVENTS}."
        ),
    )


# =============================================================================
# TOOL ERROR RESPONSE
# =============================================================================

def build_error_response(
    *,
    build_id: Optional[str],
    error_type: str,
    error_code: str,
    message: str,
    aws_error_code: Optional[str] = None,
    retryable: Optional[bool] = None,
    log_group: Optional[str] = None,
    log_stream: Optional[str] = None,
) -> str:

    output = {
        "schema_version": "1.0",

        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "operation": "GET_CODEBUILD_LOGS",
            "read_only": True,
        },

        "query": {
            "build_id": build_id,
        },

        "retrieval": {
            "status": "ERROR",
            "timestamp": utc_now_iso(),
        },

        "log_location": {
            "group_name": log_group,
            "stream_name": log_stream,
        },

        "error": {
            "type": error_type,
            "code": error_code,
            "aws_error_code": aws_error_code,
            "message": sanitize_error_message(message),
            "retryable": retryable,
        },

        "evidence": {
            "logs_retrieved": False,
            "events": [],
            "error_signals": [],
            "warning_signals": [],
        },

        "decision_support": {
            "root_cause_determined": False,
            "failure_classification_performed": False,
            "recommended_next_action": (
                "PRESERVE_UNKNOWN_AND_BLOCK_AUTOMATIC_DIAGNOSIS"
            ),
        },

        "unknown_areas": [
            "Authoritative CodeBuild log evidence could not be fully retrieved."
        ],
    }

    return json.dumps(
        output,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


# =============================================================================
# CODEBUILD METADATA RETRIEVAL
# =============================================================================

def get_build_metadata(
    codebuild_client: Any,
    build_id: str,
) -> Dict[str, Any]:
    """
    Retrieve the exact build and discover its authoritative CloudWatch
    log location.

    Raises controlled exceptions to the caller.
    """

    logger.info(
        "Retrieving CodeBuild metadata | build_id=%s",
        build_id,
    )

    response = codebuild_client.batch_get_builds(
        ids=[build_id]
    )

    builds = response.get("builds", []) or []
    not_found = response.get("buildsNotFound", []) or []

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

    actual_build_id = build.get("id")

    if actual_build_id and actual_build_id != build_id:
        return {
            "found": False,
            "reason": "BUILD_ID_MISMATCH",
            "build": None,
        }

    return {
        "found": True,
        "reason": None,
        "build": build,
    }


# =============================================================================
# CLOUDWATCH RETRIEVAL
# =============================================================================

def retrieve_cloudwatch_events(
    logs_client: Any,
    log_group: str,
    log_stream: str,
    max_events: int,
) -> Dict[str, Any]:
    """
    Retrieve CloudWatch events using pagination.

    We explicitly stop at max_events to protect AAVA/LLM context.

    The result clearly indicates if output was truncated.
    """

    events: List[Dict[str, Any]] = []

    next_token: Optional[str] = None

    pages_read = 0
    truncated = False
    redacted_event_count = 0
    truncated_message_count = 0

    logger.info(
        "Retrieving CloudWatch logs | group=%s | stream=%s | max=%s",
        log_group,
        log_stream,
        max_events,
    )

    while len(events) < max_events:

        remaining = max_events - len(events)

        request_limit = min(
            remaining,
            10000,
        )

        params: Dict[str, Any] = {
            "logGroupName": log_group,
            "logStreamName": log_stream,
            "startFromHead": True,
            "limit": request_limit,
        }

        if next_token:
            params["nextToken"] = next_token

        response = logs_client.get_log_events(
            **params
        )

        pages_read += 1

        raw_events = response.get(
            "events",
            [],
        ) or []

        for raw_event in raw_events:

            if len(events) >= max_events:
                truncated = True
                break

            raw_message = raw_event.get(
                "message",
                "",
            )

            # ---------------------------------------------------------
            # Secret redaction
            # ---------------------------------------------------------

            redaction = redact_sensitive_log_line(
                raw_message
            )

            if redaction["redacted"]:
                redacted_event_count += 1

            # ---------------------------------------------------------
            # Message-size protection
            # ---------------------------------------------------------

            truncation = truncate_message(
                redaction["message"]
            )

            if truncation["truncated"]:
                truncated_message_count += 1

            message = truncation["message"]

            signal_type = detect_signal_type(
                message
            )

            events.append({
                "timestamp_ms": raw_event.get(
                    "timestamp"
                ),

                "timestamp": epoch_ms_to_iso(
                    raw_event.get("timestamp")
                ),

                "ingestion_time_ms": raw_event.get(
                    "ingestionTime"
                ),

                "ingestion_time": epoch_ms_to_iso(
                    raw_event.get("ingestionTime")
                ),

                "message": message,

                "signal_type": signal_type,

                "redacted": redaction["redacted"],

                "message_truncated": (
                    truncation["truncated"]
                ),
            })

        new_forward_token = response.get(
            "nextForwardToken"
        )

        # CloudWatch returns the same token when the end of the stream
        # has been reached.
        if (
            not new_forward_token
            or new_forward_token == next_token
        ):
            break

        next_token = new_forward_token

        if len(events) >= max_events:
            truncated = True
            break

    return {
        "events": events,
        "pages_read": pages_read,
        "event_count": len(events),
        "truncated": truncated,
        "redacted_event_count": redacted_event_count,
        "truncated_message_count": truncated_message_count,
        "next_forward_token_available": bool(
            next_token
        ),
    }


# =============================================================================
# SIGNAL EXTRACTION
# =============================================================================

def extract_signals(
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Extract error/warning signal events.

    These remain observations, NOT diagnoses.
    """

    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    for event in events:

        signal_type = event.get(
            "signal_type"
        )

        evidence = {
            "timestamp": event.get(
                "timestamp"
            ),
            "message": event.get(
                "message"
            ),
        }

        if (
            signal_type == "ERROR_SIGNAL"
            and len(errors) < MAX_ERROR_SIGNALS
        ):
            errors.append(evidence)

        elif (
            signal_type == "WARNING_SIGNAL"
            and len(warnings) < MAX_WARNING_SIGNALS
        ):
            warnings.append(evidence)

    return {
        "error_signals": errors,
        "warning_signals": warnings,
        "error_signal_count_returned": len(errors),
        "warning_signal_count_returned": len(warnings),
    }


# =============================================================================
# PHASE CONTEXT EXTRACTION
# =============================================================================

def extract_failed_phase_contexts(
    build: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extract AWS-provided failure contexts from CodeBuild phases.

    This is direct AWS evidence and is useful alongside CloudWatch logs.
    """

    failure_statuses = {
        "FAILED",
        "FAULT",
        "TIMED_OUT",
        "STOPPED",
    }

    output: List[Dict[str, Any]] = []

    for phase in build.get(
        "phases",
        [],
    ) or []:

        phase_status = phase.get(
            "phaseStatus"
        )

        if phase_status not in failure_statuses:
            continue

        contexts = []

        for context in phase.get(
            "contexts",
            [],
        ) or []:

            contexts.append({
                "status_code": context.get(
                    "statusCode"
                ),

                "message": context.get(
                    "message"
                ),
            })

        output.append({
            "phase_type": phase.get(
                "phaseType"
            ),

            "phase_status": phase_status,

            "start_time": datetime_to_iso(
                phase.get("startTime")
            ),

            "end_time": datetime_to_iso(
                phase.get("endTime")
            ),

            "duration_seconds": phase.get(
                "durationInSeconds"
            ),

            "contexts": contexts,
        })

    return output


# =============================================================================
# MAIN TOOL
# =============================================================================

class CodeBuildLogsTool(BaseTool):
    """
    Read-only CodeBuild/CloudWatch evidence retrieval tool.
    """

    name: str = TOOL_NAME

    description: str = (
        "Retrieves authoritative AWS CodeBuild and CloudWatch log evidence "
        "for an exact CodeBuild build ID. The tool discovers the CloudWatch "
        "log group and stream directly from CodeBuild, retrieves bounded "
        "paginated log events, preserves timestamps, extracts potential "
        "error/warning signal lines, reports truncation, and performs "
        "conservative secret redaction. It does not diagnose root cause, "
        "classify failures, stop builds, retry builds, or declare CI status."
    )

    args_schema: Type[BaseModel] = CodeBuildLogsToolSchema

    def _run(
        self,
        build_id: str,
        max_log_events: int = DEFAULT_MAX_LOG_EVENTS,
        **kwargs: Any,
    ) -> str:

        started = time.monotonic()

        # =====================================================================
        # 1. INPUT VALIDATION
        # =====================================================================

        normalized_build_id = (
            build_id.strip()
            if isinstance(build_id, str)
            else ""
        )

        if not normalized_build_id:

            return build_error_response(
                build_id=None,
                error_type="INPUT_ERROR",
                error_code="INVALID_BUILD_ID",
                message=(
                    "build_id must be a non-empty string."
                ),
                retryable=False,
            )

        try:
            max_log_events = int(
                max_log_events
            )

        except Exception:

            return build_error_response(
                build_id=normalized_build_id,
                error_type="INPUT_ERROR",
                error_code="INVALID_MAX_LOG_EVENTS",
                message=(
                    "max_log_events must be an integer."
                ),
                retryable=False,
            )

        if (
            max_log_events < 1
            or max_log_events > ABSOLUTE_MAX_LOG_EVENTS
        ):

            return build_error_response(
                build_id=normalized_build_id,
                error_type="INPUT_ERROR",
                error_code="INVALID_MAX_LOG_EVENTS",
                message=(
                    f"max_log_events must be between 1 and "
                    f"{ABSOLUTE_MAX_LOG_EVENTS}."
                ),
                retryable=False,
            )

        logger.info(
            "Starting CodeBuild log retrieval | build_id=%s",
            normalized_build_id,
        )

        # =====================================================================
        # 2. CREATE AWS CLIENTS
        # =====================================================================

        try:

            session = boto3.session.Session()

            region = session.region_name

            codebuild_client = session.client(
                "codebuild"
            )

            logs_client = session.client(
                "logs"
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
                    "AWS credentials were not available to the AAVA runtime."
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
                error_code="AWS_CLIENT_INITIALIZATION_FAILED",
                message=str(exc),
                retryable=None,
            )

        # =====================================================================
        # 3. GET AUTHORITATIVE BUILD METADATA
        # =====================================================================

        try:

            metadata_result = get_build_metadata(
                codebuild_client,
                normalized_build_id,
            )

        except EndpointConnectionError as exc:

            logger.exception(
                "CodeBuild endpoint connection failed."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CONNECTION_ERROR",
                error_code="CODEBUILD_ENDPOINT_CONNECTION_FAILED",
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
                "CodeBuild API error | code=%s",
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
                error_code="CODEBUILD_METADATA_REQUEST_FAILED",
                aws_error_code=code,
                message=message or str(exc),
                retryable=retryable,
            )

        except BotoCoreError as exc:

            logger.exception(
                "BotoCore error retrieving CodeBuild metadata."
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
                "Unexpected CodeBuild metadata error."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="UNEXPECTED_ERROR",
                error_code="CODEBUILD_METADATA_ERROR",
                message=str(exc),
                retryable=None,
            )

        # =====================================================================
        # 4. VALIDATE BUILD RESULT
        # =====================================================================

        if not metadata_result.get(
            "found"
        ):

            reason = metadata_result.get(
                "reason"
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="NOT_FOUND",
                error_code=reason or "BUILD_NOT_FOUND",
                message=(
                    "The requested CodeBuild execution could not be "
                    "authoritatively retrieved."
                ),
                retryable=False,
            )

        build = metadata_result[
            "build"
        ]

        build_status = build.get(
            "buildStatus"
        )

        current_phase = build.get(
            "currentPhase"
        )

        resolved_source_version = build.get(
            "resolvedSourceVersion"
        )

        logs_metadata = build.get(
            "logs",
            {},
        ) or {}

        log_group = logs_metadata.get(
            "groupName"
        )

        log_stream = logs_metadata.get(
            "streamName"
        )

        deep_link = logs_metadata.get(
            "deepLink"
        )

        # =====================================================================
        # 5. PRESERVE MISSING LOG LOCATION AS UNKNOWN
        # =====================================================================

        if not log_group or not log_stream:

            logger.warning(
                "CloudWatch log location unavailable | build_id=%s",
                normalized_build_id,
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="LOG_LOCATION_UNKNOWN",
                error_code="CLOUDWATCH_LOG_LOCATION_UNAVAILABLE",
                message=(
                    "CodeBuild did not provide both the CloudWatch log "
                    "group and log stream required for log retrieval."
                ),
                retryable=False,
                log_group=log_group,
                log_stream=log_stream,
            )

        # =====================================================================
        # 6. RETRIEVE CLOUDWATCH EVENTS
        # =====================================================================

        try:

            cloudwatch_result = retrieve_cloudwatch_events(
                logs_client=logs_client,
                log_group=log_group,
                log_stream=log_stream,
                max_events=max_log_events,
            )

        except EndpointConnectionError as exc:

            logger.exception(
                "CloudWatch Logs endpoint connection failed."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_CONNECTION_ERROR",
                error_code="CLOUDWATCH_ENDPOINT_CONNECTION_FAILED",
                message=str(exc),
                retryable=True,
                log_group=log_group,
                log_stream=log_stream,
            )

        except ClientError as exc:

            code = get_aws_error_code(
                exc
            )

            message = get_aws_error_message(
                exc
            )

            logger.exception(
                "CloudWatch API error | code=%s",
                code,
            )

            retryable = None

            if code in {
                "AccessDenied",
                "AccessDeniedException",
                "UnrecognizedClientException",
            }:
                retryable = False

            elif code in {
                "ThrottlingException",
                "ServiceUnavailableException",
                "InternalServerException",
            }:
                retryable = True

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_API_ERROR",
                error_code="CLOUDWATCH_LOG_RETRIEVAL_FAILED",
                aws_error_code=code,
                message=message or str(exc),
                retryable=retryable,
                log_group=log_group,
                log_stream=log_stream,
            )

        except BotoCoreError as exc:

            logger.exception(
                "BotoCore error retrieving CloudWatch logs."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="AWS_SDK_ERROR",
                error_code="CLOUDWATCH_BOTOCORE_ERROR",
                message=str(exc),
                retryable=None,
                log_group=log_group,
                log_stream=log_stream,
            )

        except Exception as exc:

            logger.exception(
                "Unexpected CloudWatch retrieval error."
            )

            return build_error_response(
                build_id=normalized_build_id,
                error_type="UNEXPECTED_ERROR",
                error_code="CLOUDWATCH_RETRIEVAL_ERROR",
                message=str(exc),
                retryable=None,
                log_group=log_group,
                log_stream=log_stream,
            )

        # =====================================================================
        # 7. EXTRACT OBSERVABLE SIGNALS
        # =====================================================================

        events = cloudwatch_result.get(
            "events",
            [],
        )

        signals = extract_signals(
            events
        )

        failed_phase_contexts = (
            extract_failed_phase_contexts(
                build
            )
        )

        # =====================================================================
        # 8. UNKNOWN AREAS
        # =====================================================================

        unknown_areas: List[str] = []

        if not events:
            unknown_areas.append(
                "CloudWatch log stream was retrieved but contained no "
                "returned log events."
            )

        if cloudwatch_result.get(
            "truncated"
        ):
            unknown_areas.append(
                "Log output was truncated at the configured maximum event "
                "limit. Additional CloudWatch log evidence may exist."
            )

        if not failed_phase_contexts and build_status in {
            "FAILED",
            "FAULT",
            "TIMED_OUT",
            "STOPPED",
        }:
            unknown_areas.append(
                "CodeBuild is in a terminal non-success state, but no "
                "failed phase context was returned by CodeBuild."
            )

        # =====================================================================
        # 9. DETERMINE NEXT ACTION
        # =====================================================================

        if build_status in {
            "FAILED",
            "FAULT",
            "TIMED_OUT",
            "STOPPED",
        }:

            recommended_next_action = (
                "CLASSIFY_FAILURE_FROM_OBSERVED_EVIDENCE"
            )

            reason = (
                "Authoritative CodeBuild/CloudWatch evidence has been "
                "retrieved. The CI Failure Handling Agent may now classify "
                "the failure using the approved failure taxonomy while "
                "keeping evidence separate from inference."
            )

        elif build_status == "SUCCEEDED":

            recommended_next_action = (
                "DO_NOT_INFER_FAILURE_FROM_LOG_SIGNALS"
            )

            reason = (
                "CodeBuild reports SUCCEEDED. Error-like text in logs must "
                "not override the authoritative build state. Continue using "
                "the CI artifact-validation path unless artifact validation "
                "requires additional investigation."
            )

        elif build_status == "IN_PROGRESS":

            recommended_next_action = (
                "WAIT_FOR_TERMINAL_STATE_OR_APPLY_TIMEOUT_POLICY"
            )

            reason = (
                "CodeBuild remains non-terminal. Retrieved logs are "
                "observations only and must not be used to prematurely "
                "declare build failure."
            )

        else:

            recommended_next_action = (
                "PRESERVE_UNKNOWN_BUILD_STATE"
            )

            reason = (
                "The authoritative build status is unavailable or "
                "unrecognized. Do not infer a terminal CI result."
            )

        # =====================================================================
        # 10. FINAL OUTPUT
        # =====================================================================

        elapsed_ms = round(
            (time.monotonic() - started) * 1000,
            3,
        )

        output = {
            "schema_version": "1.0",

            "tool": {
                "name": TOOL_NAME,
                "version": TOOL_VERSION,
                "operation": "GET_CODEBUILD_LOGS",
                "read_only": True,
            },

            "query": {
                "build_id": normalized_build_id,
                "max_log_events": max_log_events,
            },

            "retrieval": {
                "status": "SUCCESS",
                "timestamp": utc_now_iso(),
                "duration_ms": elapsed_ms,
                "aws_region": region,
                "authoritative_sources": [
                    "AWS CodeBuild",
                    "Amazon CloudWatch Logs",
                ],
            },

            "build_context": {
                "build_id": build.get(
                    "id"
                ),

                "project_name": build.get(
                    "projectName"
                ),

                "build_status": build_status,

                "current_phase": current_phase,

                "source_version": build.get(
                    "sourceVersion"
                ),

                "resolved_source_version": (
                    resolved_source_version
                ),

                "start_time": datetime_to_iso(
                    build.get("startTime")
                ),

                "end_time": datetime_to_iso(
                    build.get("endTime")
                ),
            },

            "log_location": {
                "group_name": log_group,
                "stream_name": log_stream,
                "deep_link": deep_link,
            },

            "codebuild_phase_evidence": {
                "failed_phase_contexts": (
                    failed_phase_contexts
                ),

                "failed_phase_count": len(
                    failed_phase_contexts
                ),
            },

            "cloudwatch_log_evidence": {
                "logs_retrieved": True,

                "events": events,

                "event_count_returned": (
                    cloudwatch_result.get(
                        "event_count",
                        0,
                    )
                ),

                "pages_read": (
                    cloudwatch_result.get(
                        "pages_read",
                        0,
                    )
                ),

                "truncated": (
                    cloudwatch_result.get(
                        "truncated",
                        False,
                    )
                ),

                "redacted_event_count": (
                    cloudwatch_result.get(
                        "redacted_event_count",
                        0,
                    )
                ),

                "truncated_message_count": (
                    cloudwatch_result.get(
                        "truncated_message_count",
                        0,
                    )
                ),
            },

            "observed_signals": {
                "error_signals": (
                    signals[
                        "error_signals"
                    ]
                ),

                "warning_signals": (
                    signals[
                        "warning_signals"
                    ]
                ),

                "error_signal_count_returned": (
                    signals[
                        "error_signal_count_returned"
                    ]
                ),

                "warning_signal_count_returned": (
                    signals[
                        "warning_signal_count_returned"
                    ]
                ),

                "interpretation_note": (
                    "Signal extraction is lexical evidence filtering only. "
                    "An error/warning signal is not automatically the root "
                    "cause and must not override authoritative AWS state."
                ),
            },

            "evidence_integrity": {
                "root_cause_determined_by_tool": False,
                "failure_classification_performed_by_tool": False,
                "log_messages_modified_for_diagnosis": False,
                "secret_redaction_enabled": True,
                "output_bounded": True,
            },

            "decision_support": {
                "root_cause_determined": False,
                "failure_classification_performed": False,

                "recommended_next_action": (
                    recommended_next_action
                ),

                "reason": reason,
            },

            "unknown_areas": unknown_areas,
        }

        logger.info(
            "CodeBuild log retrieval completed | "
            "build_id=%s | status=%s | events=%s | "
            "errors=%s | warnings=%s | truncated=%s",
            normalized_build_id,
            build_status,
            len(events),
            signals[
                "error_signal_count_returned"
            ],
            signals[
                "warning_signal_count_returned"
            ],
            cloudwatch_result.get(
                "truncated"
            ),
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