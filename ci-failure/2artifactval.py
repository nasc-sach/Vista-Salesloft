"""
===============================================================================
AAVA - CI Artifact Validation Tool
===============================================================================

Tool Name:
    CI Artifact Validation Tool

Purpose:
    Verify mandatory CI artifacts produced for an exact source revision.

Validates:
    1. Backend ECR image
    2. Frontend ECR image
    3. Required S3 artifact
    4. Source-revision correlation

Primary Consumer:
    CI Build Validation & Failure Handling Agent

Expected image convention:
    salesloft-backend:<resolved_source_version>
    salesloft-frontend:<resolved_source_version>

Example:
    salesloft-backend:abc123def456
    salesloft-frontend:abc123def456

Design Principles:
    - READ ONLY
    - No artifact mutation
    - No ECR retagging
    - No S3 modification
    - Never uses :latest as fallback
    - Never guesses source revision
    - Missing != Unknown
    - CodeBuild success alone != CI success
    - Fail closed when mandatory verification cannot be completed

AWS credentials and region must come from the AAVA runtime/IAM environment.
===============================================================================
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type
from urllib.parse import urlparse

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

TOOL_NAME = "CI Artifact Validation Tool"
TOOL_VERSION = "1.0.0"

DEFAULT_BACKEND_REPOSITORY = "salesloft-backend"
DEFAULT_FRONTEND_REPOSITORY = "salesloft-frontend"

# Hardcoded S3 artifact location
DEFAULT_S3_BUCKET = "salesloft-codedeploy-artifacts"
DEFAULT_S3_KEY = "builds/latest/salesloft.zip"

# Hardcoded AWS configuration
DEFAULT_AWS_REGION = "eu-north-1"
DEFAULT_AWS_REGISTRY_ID = "231733667519"

# WARNING: Hardcoded credentials are a security risk in production.
# Consider using IAM roles, environment variables, or AWS credential files instead.
DEFAULT_AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID"
DEFAULT_AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY"

VERIFIED = "VERIFIED"
MISSING = "MISSING"
MISMATCH = "MISMATCH"
UNKNOWN = "UNKNOWN"
NOT_CHECKED = "NOT_CHECKED"


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("aava.ci_artifact_validation")

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


def sanitize_message(value: Any, max_length: int = 3000) -> str:
    if value is None:
        return "Unknown error"

    text = str(value)

    if len(text) > max_length:
        return text[:max_length] + "...[TRUNCATED]"

    return text


def aws_error_code(error: ClientError) -> Optional[str]:
    try:
        return error.response.get("Error", {}).get("Code")
    except Exception:
        return None


def aws_error_message(error: ClientError) -> Optional[str]:
    try:
        return error.response.get("Error", {}).get("Message")
    except Exception:
        return None


def normalize_revision(value: str) -> str:
    """
    Normalize source revision without transforming its identity.

    IMPORTANT:
        This tool does NOT shorten a commit SHA.

        If your build pipeline uses a shortened SHA as the ECR tag,
        CodeBuildStatusTool/upstream build metadata must provide the exact
        revision/tag expected by this tool.
    """
    return value.strip()


def build_ecr_uri(
    registry_id: Optional[str],
    region: Optional[str],
    repository: str,
    tag: str,
) -> Optional[str]:

    if not registry_id or not region:
        return None

    return (
        f"{registry_id}.dkr.ecr.{region}.amazonaws.com/"
        f"{repository}:{tag}"
    )


# =============================================================================
# CODEBUILD OUTPUT PARSING
# =============================================================================

def parse_s3_arn(arn: str) -> Dict[str, Optional[str]]:
    """
    Parse S3 ARN format:

        arn:aws:s3:::bucket/key/path

    into:

        {
            "bucket": "bucket",
            "key": "key/path"
        }
    """

    if not arn:
        return {
            "bucket": None,
            "key": None,
        }

    # ARN format: arn:aws:s3:::bucket/key
    if not arn.startswith("arn:aws:s3:::"):
        return {
            "bucket": None,
            "key": None,
        }

    # Remove the ARN prefix
    path = arn[len("arn:aws:s3:::"):]

    # Split on first slash to separate bucket from key
    parts = path.split("/", 1)

    bucket = parts[0] if parts else None
    key = parts[1] if len(parts) > 1 else None

    return {
        "bucket": bucket,
        "key": key,
    }


def parse_ecr_repository_from_uri(ecr_uri: str) -> Optional[str]:
    """
    Parse ECR URI format:

        registry.dkr.ecr.region.amazonaws.com/repository:tag

    and extract just the repository name.

    Example:
        Input: "231733667519.dkr.ecr.eu-north-1.amazonaws.com/salesloft-backend:latest"
        Output: "salesloft-backend"
    """

    if not ecr_uri:
        return None

    # Split on "/" to separate registry from repository:tag
    if "/" not in ecr_uri:
        return None

    # Get the repository:tag part
    repo_with_tag = ecr_uri.split("/", 1)[1]

    # Remove the :tag suffix if present
    repository = repo_with_tag.split(":")[0]

    return repository if repository else None


def parse_codebuild_output(codebuild_json: str) -> Dict[str, Any]:
    """
    Parse CodeBuildStatusTool JSON output with fallback paths.
    Handles both new metadata structure and legacy build structure.
    
    Extracts:
    - resolved_source_version
    - S3 artifact bucket and key (from ARN)
    - Backend and frontend ECR repository names (from environment variables)
    - AWS region

    Returns dict with extracted values or error information.
    """

    try:
        data = json.loads(codebuild_json)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON: {exc}"}

    # Try metadata path first (new structure from fixed Tool 1)
    metadata = data.get("metadata", {})
    
    # Fallback to build/source/artifacts paths (old structure)
    if not metadata:
        build_data = data.get("build", {})
        source_data = data.get("source", {})
        artifacts_data = data.get("artifacts", {})
        env_data = data.get("environment", {})
    else:
        build_data = metadata
        source_data = metadata
        artifacts_data = metadata.get("artifacts", {})
        env_data = metadata.get("environment", {})

    # Extract resolved_source_version with fallbacks
    resolved_source_version = (
        metadata.get("resolved_source_version") or
        source_data.get("resolved_source_version") or
        build_data.get("resolved_source_version")
    )

    # Parse S3 artifact with fallbacks
    s3_location = (
        artifacts_data.get("location") or
        artifacts_data.get("primary_artifact", {}).get("location") or
        ""
    )
    s3_parsed = parse_s3_arn(s3_location)

    # Extract region from multiple possible locations
    region = (
        metadata.get("aws_region") or
        data.get("retrieval_metadata", {}).get("aws_region") or
        # Extract from build ARN as last resort
        (build_data.get("build_arn", "").split(":")[3] if ":" in build_data.get("build_arn", "") and len(build_data.get("build_arn", "").split(":")) > 3 else None)
    )
    
    # If all extraction paths failed, use hardcoded default region
    if not region:
        logger.info(
            "AWS region not found in CodeBuild output, will use hardcoded default: %s",
            DEFAULT_AWS_REGION
        )
        region = DEFAULT_AWS_REGION

    # Parse ECR repositories from environment variables
    env_vars = env_data.get("environmentVariables", []) or []
    backend_repo = None
    frontend_repo = None

    for var in env_vars:
        var_name = var.get("name", "")
        var_value = var.get("value", "")

        if var_name == "BACKEND_IMAGE":
            backend_repo = parse_ecr_repository_from_uri(var_value)
        elif var_name == "FRONTEND_IMAGE":
            frontend_repo = parse_ecr_repository_from_uri(var_value)

    return {
        "resolved_source_version": resolved_source_version,
        "s3_bucket": s3_parsed.get("bucket"),
        "s3_key": s3_parsed.get("key"),
        "backend_repository": backend_repo,
        "frontend_repository": frontend_repo,
        "aws_region": region,
    }


# =============================================================================
# S3 LOCATION PARSING
# =============================================================================

def parse_s3_uri(uri: str) -> Dict[str, Optional[str]]:
    """
    Parse:

        s3://bucket/key/path/file.zip

    into:

        {
            "bucket": "bucket",
            "key": "key/path/file.zip"
        }
    """

    if not uri:
        return {
            "bucket": None,
            "key": None,
        }

    parsed = urlparse(uri)

    if parsed.scheme.lower() != "s3":
        return {
            "bucket": None,
            "key": None,
        }

    bucket = parsed.netloc or None
    key = parsed.path.lstrip("/") or None

    return {
        "bucket": bucket,
        "key": key,
    }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class CIArtifactValidationToolSchema(BaseModel):
    """
    Input schema for CIArtifactValidationTool that accepts CodeBuildStatusTool output.

    The tool parses the complete CodeBuild JSON output to extract:
    - resolved_source_version
    - S3 artifact location
    - ECR repository names from environment variables
    """

    codebuild_output: str = Field(
        ...,
        description=(
            "Complete JSON output from CodeBuildStatusTool containing "
            "resolved_source_version, artifact location, and environment variables."
        ),
    )


# =============================================================================
# ECR VALIDATION
# =============================================================================

def validate_ecr_image(
    client: Any,
    repository_name: str,
    expected_tag: str,
    region: Optional[str],
) -> Dict[str, Any]:
    """
    Validate the existence of an exact ECR repository:tag.

    This performs no fallback lookup.

    In particular:

        expected tag missing -> MISSING

    It NEVER checks :latest instead.
    """

    result: Dict[str, Any] = {
        "repository": repository_name,
        "expected_tag": expected_tag,
        "status": UNKNOWN,
        "verified": False,
        "image_uri": None,
        "image_digest": None,
        "image_tags": [],
        "image_pushed_at": None,
        "image_size_bytes": None,
        "registry_id": None,
        "repository_uri": None,
        "correlation": {
            "method": "EXACT_ECR_IMAGE_TAG",
            "expected_revision": expected_tag,
            "observed_expected_tag": False,
            "verified": False,
        },
        "error": None,
    }

    try:
        logger.info(
            "Validating ECR image | repository=%s | tag=%s",
            repository_name,
            expected_tag,
        )

        # ---------------------------------------------------------------------
        # 1. Get repository metadata
        # ---------------------------------------------------------------------

        repository_response = client.describe_repositories(
            repositoryNames=[repository_name]
        )

        repositories = repository_response.get("repositories", []) or []

        if not repositories:
            result["status"] = MISSING
            result["error"] = {
                "code": "ECR_REPOSITORY_NOT_FOUND",
                "message": (
                    f"ECR repository '{repository_name}' was not returned."
                ),
            }

            return result

        repository = repositories[0]

        registry_id = repository.get("registryId")
        repository_uri = repository.get("repositoryUri")

        result["registry_id"] = registry_id
        result["repository_uri"] = repository_uri

        # ---------------------------------------------------------------------
        # 2. List images with the expected tag
        # ---------------------------------------------------------------------

        response = client.describe_images(
            repositoryName=repository_name,
            imageIds=[
                {"imageTag": expected_tag}
            ],
        )

        image_details = response.get("imageDetails", []) or []

        if not image_details:
            result["status"] = MISSING
            result["error"] = {
                "code": "ECR_IMAGE_NOT_FOUND",
                "message": (
                    f"ECR image tag '{expected_tag}' not found in '{repository_name}'."
                ),
            }

            return result

        image = image_details[0]

        image_tags = image.get("imageTags", []) or []
        digest = image.get("imageDigest")

        expected_tag_observed = expected_tag in image_tags

        result["image_tags"] = image_tags
        result["image_digest"] = digest
        result["image_pushed_at"] = datetime_to_iso(
            image.get("imagePushedAt")
        )
        result["image_size_bytes"] = image.get("imageSizeInBytes")

        # ---------------------------------------------------------------------
        # 3. Build complete image URI
        # ---------------------------------------------------------------------

        if registry_id and region:
            result["image_uri"] = build_ecr_uri(
                registry_id=registry_id,
                region=region,
                repository=repository_name,
                tag=expected_tag,
            )

        # ---------------------------------------------------------------------
        # 4. Determine verification result
        # ---------------------------------------------------------------------

        if expected_tag_observed:
            result["status"] = VERIFIED
            result["verified"] = True
            result["correlation"]["observed_expected_tag"] = True
            result["correlation"]["verified"] = True

            logger.info(
                "ECR image VERIFIED | repository=%s | tag=%s | digest=%s",
                repository_name,
                expected_tag,
                digest,
            )
        else:
            # Should not happen: we requested the tag specifically
            result["status"] = UNKNOWN
            result["error"] = {
                "code": "ECR_TAG_MISMATCH",
                "message": (
                    f"Tag '{expected_tag}' returned by API but not in image metadata."
                ),
            }

            logger.warning(
                "ECR image UNKNOWN | repository=%s | tag=%s | digest=%s",
                repository_name,
                expected_tag,
                digest,
            )

        return result

    except ClientError as exc:
        code = aws_error_code(exc)
        message = sanitize_message(aws_error_message(exc))

        if code == "RepositoryNotFoundException":
            result["status"] = MISSING
            result["error"] = {
                "code": "ECR_REPOSITORY_NOT_FOUND",
                "message": (
                    f"ECR repository '{repository_name}' does not exist."
                ),
            }

            logger.warning(
                "ECR repository NOT FOUND | repository=%s",
                repository_name,
            )

        elif code == "ImageNotFoundException":
            result["status"] = MISSING
            result["error"] = {
                "code": "ECR_IMAGE_NOT_FOUND",
                "message": (
                    f"ECR image tag '{expected_tag}' not found in '{repository_name}'."
                ),
            }

            logger.warning(
                "ECR image NOT FOUND | repository=%s | tag=%s",
                repository_name,
                expected_tag,
            )

        else:
            result["status"] = UNKNOWN
            result["error"] = {
                "code": code or "ECR_CLIENT_ERROR",
                "message": message,
            }

            logger.exception(
                "ECR validation ClientError | code=%s",
                code,
            )

        return result

    except NoCredentialsError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_NO_CREDENTIALS",
            "message": "AWS credentials not configured.",
        }

        logger.exception("AWS credentials missing")
        return result

    except PartialCredentialsError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_PARTIAL_CREDENTIALS",
            "message": "AWS credentials incomplete.",
        }

        logger.exception("AWS credentials incomplete")
        return result

    except EndpointConnectionError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_ENDPOINT_CONNECTION_ERROR",
            "message": "Cannot connect to AWS ECR endpoint.",
        }

        logger.exception("AWS endpoint connection failed")
        return result

    except Exception:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "UNEXPECTED_ERROR",
            "message": "Unexpected error during ECR validation.",
        }

        logger.exception("Unexpected ECR validation error")
        return result


# =============================================================================
# S3 VALIDATION
# =============================================================================

def validate_s3_artifact(
    client: Any,
    bucket: str,
    key: str,
) -> Dict[str, Any]:
    """
    Validate the existence of an S3 object.

    Returns VERIFIED, MISSING, or UNKNOWN.
    """

    result: Dict[str, Any] = {
        "bucket": bucket,
        "key": key,
        "status": UNKNOWN,
        "verified": False,
        "s3_uri": f"s3://{bucket}/{key}",
        "etag": None,
        "size_bytes": None,
        "last_modified": None,
        "error": None,
    }

    try:
        logger.info(
            "Validating S3 artifact | bucket=%s | key=%s",
            bucket,
            key,
        )

        # ---------------------------------------------------------------------
        # HEAD object to check existence
        # ---------------------------------------------------------------------

        response = client.head_object(
            Bucket=bucket,
            Key=key,
        )

        result["etag"] = response.get("ETag")
        result["size_bytes"] = response.get("ContentLength")
        result["last_modified"] = datetime_to_iso(
            response.get("LastModified")
        )

        result["status"] = VERIFIED
        result["verified"] = True

        logger.info(
            "S3 artifact VERIFIED | bucket=%s | key=%s | etag=%s | size=%s",
            bucket,
            key,
            result["etag"],
            result["size_bytes"],
        )

        return result

    except ClientError as exc:
        code = aws_error_code(exc)
        message = sanitize_message(aws_error_message(exc))

        if code == "404" or code == "NoSuchKey":
            result["status"] = MISSING
            result["error"] = {
                "code": "S3_OBJECT_NOT_FOUND",
                "message": (
                    f"S3 object not found: s3://{bucket}/{key}"
                ),
            }

            logger.warning(
                "S3 artifact NOT FOUND | bucket=%s | key=%s",
                bucket,
                key,
            )

        elif code == "403" or code == "AccessDenied":
            result["status"] = UNKNOWN
            result["error"] = {
                "code": "S3_ACCESS_DENIED",
                "message": (
                    f"Access denied to S3 object: s3://{bucket}/{key}"
                ),
            }

            logger.warning(
                "S3 artifact ACCESS DENIED | bucket=%s | key=%s",
                bucket,
                key,
            )

        else:
            result["status"] = UNKNOWN
            result["error"] = {
                "code": code or "S3_CLIENT_ERROR",
                "message": message,
            }

            logger.exception(
                "S3 validation ClientError | code=%s",
                code,
            )

        return result

    except NoCredentialsError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_NO_CREDENTIALS",
            "message": "AWS credentials not configured.",
        }

        logger.exception("AWS credentials missing")
        return result

    except PartialCredentialsError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_PARTIAL_CREDENTIALS",
            "message": "AWS credentials incomplete.",
        }

        logger.exception("AWS credentials incomplete")
        return result

    except EndpointConnectionError:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "AWS_ENDPOINT_CONNECTION_ERROR",
            "message": "Cannot connect to AWS S3 endpoint.",
        }

        logger.exception("AWS endpoint connection failed")
        return result

    except Exception:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "UNEXPECTED_ERROR",
            "message": "Unexpected error during S3 validation.",
        }

        logger.exception("Unexpected S3 validation error")
        return result


# =============================================================================
# VALIDATION LOGIC
# =============================================================================

def determine_validation_result(
    backend: Dict[str, Any],
    frontend: Dict[str, Any],
    s3_artifact: Dict[str, Any],
) -> str:
    """
    Determine overall validation result based on individual artifact checks.

    VERIFIED:
        All three artifacts verified.

    MISSING:
        At least one artifact is missing (and none are unknown).

    UNKNOWN:
        At least one artifact is unknown (could not be confirmed).

    This implements a fail-closed policy:
        Uncertainty prevents approval.
    """

    statuses = {backend["status"], frontend["status"], s3_artifact["status"]}

    if statuses == {VERIFIED}:
        logger.info("All artifacts VERIFIED.")
        return VERIFIED

    if UNKNOWN in statuses:
        logger.warning(
            "At least one artifact status is UNKNOWN, validation cannot be confirmed."
        )
        return UNKNOWN

    if MISSING in statuses:
        logger.warning("At least one artifact is MISSING.")
        return MISSING

    # Fallback: should not reach here
    logger.error("Unexpected artifact validation state: %s", statuses)
    return UNKNOWN


# =============================================================================
# ERROR HANDLING
# =============================================================================

def build_tool_error(
    resolved_source_version: Optional[str],
    code: str,
    message: str,
) -> str:
    """Build structured error JSON response."""

    payload = {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "timestamp": utc_now_iso(),
        "resolved_source_version": resolved_source_version,
        "validation": {
            "status": UNKNOWN,
            "verified": False,
            "backend_image": NOT_CHECKED,
            "frontend_image": NOT_CHECKED,
            "s3_artifact": NOT_CHECKED,
        },
        "error": {
            "code": code,
            "message": message,
        },
    }

    return json.dumps(payload, indent=2, default=str)


# =============================================================================
# TOOL
# =============================================================================

class CIArtifactValidationTool(BaseTool):
    """
    Validates CI artifacts for a specific source revision using CodeBuild metadata.

    Accepts CodeBuildStatusTool JSON output and validates:
    - Backend ECR image
    - Frontend ECR image
    - S3 deployment artifact
    """

    name: str = "ci_artifact_validation_tool"

    description: str = (
        "Validate mandatory CI artifacts (backend image, frontend image, S3 artifact) "
        "for an exact source revision using CodeBuild metadata from CodeBuildStatusTool. "
        "Returns VERIFIED only when all artifacts exist. Never uses fallback tags. "
        "Fail closed: missing or uncertain artifacts prevent validation approval."
    )

    args_schema: Type[BaseModel] = CIArtifactValidationToolSchema

    def _run(
        self,
        codebuild_output: str,
    ) -> str:

        started = time.time()

        # =====================================================================
        # 1. PARSE CODEBUILD OUTPUT
        # =====================================================================

        logger.info(
            "==================== CI ARTIFACT VALIDATION START ====================\n"
            "%s | %s | Starting validation",
            TOOL_NAME,
            TOOL_VERSION,
        )

        logger.info(
            "Parsing CodeBuild output JSON to extract artifact metadata."
        )

        parsed = parse_codebuild_output(codebuild_output)

        if "error" in parsed:
            return build_tool_error(
                resolved_source_version=None,
                code="CODEBUILD_OUTPUT_PARSE_ERROR",
                message=parsed["error"],
            )

        # Extract resolved source version
        resolved_source_version = parsed.get("resolved_source_version")

        if not resolved_source_version:
            return build_tool_error(
                resolved_source_version=None,
                code="MISSING_RESOLVED_SOURCE_VERSION",
                message=(
                    "resolved_source_version not found in CodeBuild output. "
                    "Cannot validate artifacts without knowing the exact source revision."
                ),
            )

        revision = normalize_revision(resolved_source_version)

        logger.info(
            "Extracted resolved_source_version: %s",
            revision,
        )

        # =====================================================================
        # 2. DETERMINE REPOSITORY NAMES
        # =====================================================================

        backend_repository = parsed.get("backend_repository") or DEFAULT_BACKEND_REPOSITORY
        frontend_repository = parsed.get("frontend_repository") or DEFAULT_FRONTEND_REPOSITORY

        if parsed.get("backend_repository"):
            logger.info(
                "Using backend repository from CodeBuild environment: %s",
                backend_repository,
            )
        else:
            logger.info(
                "Using hardcoded default backend repository: %s",
                backend_repository,
            )

        if parsed.get("frontend_repository"):
            logger.info(
                "Using frontend repository from CodeBuild environment: %s",
                frontend_repository,
            )
        else:
            logger.info(
                "Using hardcoded default frontend repository: %s",
                frontend_repository,
            )

        # =====================================================================
        # 3. DETERMINE S3 ARTIFACT LOCATION
        # =====================================================================

        supplied_bucket = parsed.get("s3_bucket")
        supplied_key = parsed.get("s3_key")

        if supplied_bucket and supplied_key:
            logger.info(
                "Using S3 artifact location from CodeBuild output: s3://%s/%s",
                supplied_bucket,
                supplied_key,
            )
        else:
            logger.info(
                "S3 artifact location not found in CodeBuild output, using hardcoded defaults: s3://%s/%s",
                DEFAULT_S3_BUCKET,
                DEFAULT_S3_KEY,
            )

            supplied_bucket = DEFAULT_S3_BUCKET
            supplied_key = DEFAULT_S3_KEY

        # =====================================================================
        # 4. CREATE AWS CLIENTS
        # =====================================================================

        # Extract region from parsed CodeBuild output
        codebuild_region = parsed.get("aws_region")

        try:
            logger.info(
                "Creating AWS ECR and S3 clients."
            )

            # Use explicit region from CodeBuild output or hardcoded default
            region = codebuild_region or DEFAULT_AWS_REGION
            session = boto3.session.Session(
                aws_access_key_id=DEFAULT_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=DEFAULT_AWS_SECRET_ACCESS_KEY,
                region_name=region
            )
            
            # Log whether region came from CodeBuild output or hardcoded default
            if codebuild_region:
                logger.info(
                    "Using AWS region from CodeBuild output: %s", region
                )
            else:
                logger.info(
                    "Using hardcoded default AWS region: %s", region
                )

            # Clients inherit region from session
            ecr_client = session.client("ecr")
            s3_client = session.client("s3")

        except NoCredentialsError:
            logger.exception(
                "AWS credentials not configured."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="AWS_NO_CREDENTIALS",
                message="AWS credentials not configured in the environment.",
            )

        except PartialCredentialsError:
            logger.exception(
                "AWS credentials incomplete."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="AWS_PARTIAL_CREDENTIALS",
                message="AWS credentials incomplete in the environment.",
            )

        except Exception:
            logger.exception(
                "Unexpected error creating AWS clients."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="AWS_CLIENT_INIT_ERROR",
                message="Failed to create AWS clients.",
            )

        # =====================================================================
        # 5. VALIDATE BACKEND IMAGE
        # =====================================================================

        backend_result = validate_ecr_image(
            client=ecr_client,
            repository_name=backend_repository,
            expected_tag=revision,
            region=region,
        )

        # =====================================================================
        # 6. VALIDATE FRONTEND IMAGE
        # =====================================================================

        frontend_result = validate_ecr_image(
            client=ecr_client,
            repository_name=frontend_repository,
            expected_tag=revision,
            region=region,
        )

        # =====================================================================
        # 7. VALIDATE S3 ARTIFACT
        # =====================================================================

        s3_result = validate_s3_artifact(
            client=s3_client,
            bucket=supplied_bucket,
            key=supplied_key,
        )

        # =====================================================================
        # 8. DETERMINE OVERALL VALIDATION RESULT
        # =====================================================================

        validation = determine_validation_result(
            backend=backend_result,
            frontend=frontend_result,
            s3_artifact=s3_result,
        )

        unknown_areas = []

        if backend_result["status"] == UNKNOWN:
            unknown_areas.append("backend_ecr_image")

        if frontend_result["status"] == UNKNOWN:
            unknown_areas.append("frontend_ecr_image")

        if s3_result["status"] == UNKNOWN:
            unknown_areas.append("s3_artifact")

        if unknown_areas:
            logger.warning(
                "Validation incomplete due to UNKNOWN status in: %s",
                ", ".join(unknown_areas),
            )

        # =====================================================================
        # 9. BUILD OUTPUT
        # =====================================================================

        elapsed_ms = int((time.time() - started) * 1000)

        # Build expected image URIs
        expected_backend = build_ecr_uri(
            DEFAULT_AWS_REGISTRY_ID, region, backend_repository, revision
        )
        expected_frontend = build_ecr_uri(
            DEFAULT_AWS_REGISTRY_ID, region, frontend_repository, revision
        )

        output = {
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "timestamp": utc_now_iso(),
            "resolved_source_version": revision,
            "validation": {
                "status": validation,
                "verified": validation == VERIFIED,
                "backend_image": {
                    "expected_image_uri": expected_backend,
                    "status": backend_result["status"],
                    "verified": backend_result["verified"],
                    "image_uri": backend_result["image_uri"],
                    "image_digest": backend_result["image_digest"],
                    "image_tags": backend_result["image_tags"],
                    "image_pushed_at": backend_result["image_pushed_at"],
                    "image_size_bytes": backend_result["image_size_bytes"],
                    "registry_id": backend_result["registry_id"],
                    "repository": backend_result["repository"],
                    "repository_uri": backend_result["repository_uri"],
                    "expected_tag": backend_result["expected_tag"],
                    "correlation": backend_result["correlation"],
                    "error": backend_result["error"],
                },
                "frontend_image": {
                    "expected_image_uri": expected_frontend,
                    "status": frontend_result["status"],
                    "verified": frontend_result["verified"],
                    "image_uri": frontend_result["image_uri"],
                    "image_digest": frontend_result["image_digest"],
                    "image_tags": frontend_result["image_tags"],
                    "image_pushed_at": frontend_result["image_pushed_at"],
                    "image_size_bytes": frontend_result["image_size_bytes"],
                    "registry_id": frontend_result["registry_id"],
                    "repository": frontend_result["repository"],
                    "repository_uri": frontend_result["repository_uri"],
                    "expected_tag": frontend_result["expected_tag"],
                    "correlation": frontend_result["correlation"],
                    "error": frontend_result["error"],
                },
                "s3_artifact": {
                    "expected_s3_uri": f"s3://{supplied_bucket}/{supplied_key}",
                    "status": s3_result["status"],
                    "verified": s3_result["verified"],
                    "bucket": s3_result["bucket"],
                    "key": s3_result["key"],
                    "s3_uri": s3_result["s3_uri"],
                    "etag": s3_result["etag"],
                    "size_bytes": s3_result["size_bytes"],
                    "last_modified": s3_result["last_modified"],
                    "error": s3_result["error"],
                },
            },
            "metadata": {
                "elapsed_ms": elapsed_ms,
                "aws_region": region,
            },
        }

        logger.info(
            "==================== CI ARTIFACT VALIDATION COMPLETE ====================\n"
            "Overall Status: %s | Verified: %s | Elapsed: %d ms",
            validation,
            validation == VERIFIED,
            elapsed_ms,
        )

        return json.dumps(output, indent=2, default=str)

        output = {
            "schema_version": "1.0",

            "tool": {
                "name": TOOL_NAME,
                "version": TOOL_VERSION,
                "operation": "VALIDATE_CI_ARTIFACTS",
                "read_only": True,
            },

            "retrieval": {
                "status": "SUCCESS",
                "timestamp": utc_now_iso(),
                "duration_ms": elapsed_ms,
                "aws_region": region,
            },

            "source_correlation": {
                "resolved_source_version": revision,

                "tag_policy": (
                    "<repository>:<resolved_source_version>"
                ),

                "backend_expected_identity": (
                    expected_backend
                ),

                "frontend_expected_identity": (
                    expected_frontend
                ),

                "mutable_latest_fallback_allowed": False,
            },

            "expected_artifacts": {
                "backend": {
                    "repository": backend_repository,
                    "tag": revision,
                    "identity": expected_backend,
                },

                "frontend": {
                    "repository": frontend_repository,
                    "tag": revision,
                    "identity": expected_frontend,
                },

                "s3": {
                    "bucket": supplied_bucket,
                    "key": supplied_key,
                    "uri": (
                        f"s3://{supplied_bucket}/{supplied_key}"
                    ),
                },
            },

            "artifact_results": {
                "backend": backend_result,
                "frontend": frontend_result,
                "s3_artifact": s3_result,
            },

            "validation": validation,

            "decision_support": {
                "backend_verified": (
                    backend_result.get("verified", False)
                ),

                "frontend_verified": (
                    frontend_result.get("verified", False)
                ),

                "s3_artifact_verified": (
                    s3_result.get("verified", False)
                ),

                "ecr_revision_correlation_verified": (
                    backend_result
                    .get("correlation", {})
                    .get("verified", False)
                    and
                    frontend_result
                    .get("correlation", {})
                    .get("verified", False)
                ),

                "all_mandatory_artifacts_verified": (
                    validation.get(
                        "all_mandatory_artifacts_verified",
                        False,
                    )
                ),

                # Critical architectural boundary:
                #
                # Artifact validation alone cannot promote.
                "overall_ci_success_determined": False,
                "promotion_allowed": False,

                "recommended_next_action": (
                    "COMBINE_WITH_CODEBUILD_STATUS"
                    if validation.get("status") == "VERIFIED"
                    else
                    "BLOCK_CI_AND_ANALYZE_ARTIFACT_FAILURE"
                    if validation.get("status") == "INVALID"
                    else
                    "BLOCK_CI_DUE_TO_UNKNOWN_ARTIFACT_STATE"
                ),
            },

            "unknown_areas": unknown_areas,
        }

        logger.info(
            "CI artifact validation completed | "
            "revision=%s | backend=%s | frontend=%s | "
            "s3=%s | aggregate=%s",
            revision,
            backend_result.get("status"),
            frontend_result.get("status"),
            s3_result.get("status"),
            validation.get("status"),
        )

        return json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


# =============================================================================
# END
# =============================================================================
# END
# =============================================================================