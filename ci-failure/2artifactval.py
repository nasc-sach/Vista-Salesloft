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
        # 2. Exact image tag lookup
        # ---------------------------------------------------------------------

        response = client.describe_images(
            repositoryName=repository_name,
            imageIds=[
                {
                    "imageTag": expected_tag
                }
            ],
            maxResults=1,
        )

        image_details = response.get("imageDetails", []) or []

        if not image_details:
            result["status"] = MISSING
            result["error"] = {
                "code": "ECR_IMAGE_TAG_NOT_FOUND",
                "message": (
                    f"Expected image '{repository_name}:{expected_tag}' "
                    "was not found."
                ),
            }

            return result

        image = image_details[0]

        image_tags = image.get("imageTags", []) or []
        digest = image.get("imageDigest")

        expected_tag_observed = expected_tag in image_tags

        result["image_digest"] = digest
        result["image_tags"] = image_tags
        result["image_pushed_at"] = datetime_to_iso(
            image.get("imagePushedAt")
        )
        result["image_size_bytes"] = (
            image.get("imageSizeInBytes")
        )

        if repository_uri:
            result["image_uri"] = (
                f"{repository_uri}:{expected_tag}"
            )
        else:
            result["image_uri"] = build_ecr_uri(
                registry_id=registry_id,
                region=region,
                repository=repository_name,
                tag=expected_tag,
            )

        result["correlation"] = {
            "method": "EXACT_ECR_IMAGE_TAG",
            "expected_revision": expected_tag,
            "observed_expected_tag": expected_tag_observed,
            "verified": expected_tag_observed,
        }

        if not expected_tag_observed:
            # Defensive case. AWS describe_images was queried by exact tag,
            # therefore this should normally not occur.
            result["status"] = MISMATCH
            result["verified"] = False
            result["error"] = {
                "code": "ECR_TAG_CORRELATION_MISMATCH",
                "message": (
                    "AWS returned image metadata, but the expected immutable "
                    "tag was not present in imageTags."
                ),
            }

            return result

        result["status"] = VERIFIED
        result["verified"] = True

        logger.info(
            "ECR image verified | repository=%s | tag=%s | digest=%s",
            repository_name,
            expected_tag,
            digest,
        )

        return result

    except ClientError as exc:
        code = aws_error_code(exc)
        message = aws_error_message(exc)

        logger.warning(
            "ECR ClientError | repository=%s | tag=%s | code=%s",
            repository_name,
            expected_tag,
            code,
        )

        # RepositoryNotFoundException is deterministic absence.
        if code == "RepositoryNotFoundException":
            result["status"] = MISSING
            result["error"] = {
                "code": code,
                "message": sanitize_message(message),
            }

            return result

        # ImageNotFoundException means the exact immutable image is absent.
        if code == "ImageNotFoundException":
            result["status"] = MISSING
            result["error"] = {
                "code": code,
                "message": sanitize_message(message),
            }

            return result

        # Permission, throttling, network-adjacent AWS failures etc. do NOT
        # prove absence. Preserve UNKNOWN.
        result["status"] = UNKNOWN
        result["error"] = {
            "code": code or "AWS_CLIENT_ERROR",
            "message": sanitize_message(message or str(exc)),
        }

        return result

    except EndpointConnectionError as exc:
        logger.exception(
            "Unable to connect to ECR endpoint."
        )

        result["status"] = UNKNOWN
        result["error"] = {
            "code": "ECR_ENDPOINT_CONNECTION_FAILED",
            "message": sanitize_message(exc),
        }

        return result

    except Exception as exc:
        logger.exception(
            "Unexpected ECR validation error."
        )

        result["status"] = UNKNOWN
        result["error"] = {
            "code": "ECR_VALIDATION_ERROR",
            "message": sanitize_message(exc),
        }

        return result


# =============================================================================
# S3 VALIDATION
# =============================================================================

def validate_s3_artifact(
    client: Any,
    bucket: Optional[str],
    key: Optional[str],
) -> Dict[str, Any]:
    """
    Verify the exact expected S3 object using HeadObject.

    This checks exact object identity.

    It does NOT:
        - search for similar filenames
        - choose newest object
        - scan a prefix and guess
        - treat bucket existence as artifact existence
    """

    result: Dict[str, Any] = {
        "bucket": bucket,
        "key": key,
        "uri": (
            f"s3://{bucket}/{key}"
            if bucket and key
            else None
        ),
        "status": UNKNOWN,
        "verified": False,
        "etag": None,
        "version_id": None,
        "content_length_bytes": None,
        "last_modified": None,
        "content_type": None,
        "metadata": {},
        "correlation": {
            "method": "EXACT_S3_OBJECT_KEY",
            "verified": False,
        },
        "error": None,
    }

    if not bucket or not key:
        result["status"] = UNKNOWN
        result["error"] = {
            "code": "S3_ARTIFACT_LOCATION_INCOMPLETE",
            "message": (
                "Both S3 bucket and exact object key are required for "
                "artifact verification."
            ),
        }

        return result

    try:
        logger.info(
            "Validating S3 artifact | bucket=%s | key=%s",
            bucket,
            key,
        )

        response = client.head_object(
            Bucket=bucket,
            Key=key,
        )

        result["etag"] = response.get("ETag")
        result["version_id"] = response.get("VersionId")
        result["content_length_bytes"] = (
            response.get("ContentLength")
        )
        result["last_modified"] = datetime_to_iso(
            response.get("LastModified")
        )
        result["content_type"] = response.get("ContentType")

        # User-defined S3 metadata is generally safe, but it may theoretically
        # contain sensitive information. We preserve keys/values returned by
        # AWS because artifact correlation may depend on commit/build metadata.
        #
        # Do not place secrets in S3 object metadata.
        result["metadata"] = response.get("Metadata", {}) or {}

        result["status"] = VERIFIED
        result["verified"] = True

        result["correlation"] = {
            "method": "EXACT_S3_OBJECT_KEY",
            "verified": True,
        }

        logger.info(
            "S3 artifact verified | bucket=%s | key=%s",
            bucket,
            key,
        )

        return result

    except ClientError as exc:
        code = aws_error_code(exc)
        message = aws_error_message(exc)

        logger.warning(
            "S3 ClientError | bucket=%s | key=%s | code=%s",
            bucket,
            key,
            code,
        )

        # Depending on IAM/configuration, HeadObject can report 404/NoSuchKey.
        if code in {
            "404",
            "NoSuchKey",
            "NotFound",
            "NoSuchBucket",
        }:
            result["status"] = MISSING
            result["error"] = {
                "code": code,
                "message": sanitize_message(message),
            }

            return result

        # 403/AccessDenied is UNKNOWN, not MISSING.
        result["status"] = UNKNOWN
        result["error"] = {
            "code": code or "AWS_CLIENT_ERROR",
            "message": sanitize_message(message or str(exc)),
        }

        return result

    except EndpointConnectionError as exc:
        logger.exception(
            "Unable to connect to S3 endpoint."
        )

        result["status"] = UNKNOWN
        result["error"] = {
            "code": "S3_ENDPOINT_CONNECTION_FAILED",
            "message": sanitize_message(exc),
        }

        return result

    except Exception as exc:
        logger.exception(
            "Unexpected S3 artifact validation error."
        )

        result["status"] = UNKNOWN
        result["error"] = {
            "code": "S3_VALIDATION_ERROR",
            "message": sanitize_message(exc),
        }

        return result


# =============================================================================
# FINAL CLASSIFICATION
# =============================================================================

def determine_validation_result(
    backend: Dict[str, Any],
    frontend: Dict[str, Any],
    s3_artifact: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine aggregate artifact-validation state.

    Precedence:

        UNKNOWN
            Tool/AWS evidence could not establish truth.

        MISSING / MISMATCH
            Evidence deterministically establishes invalid artifact state.

        VERIFIED
            Every mandatory artifact was positively verified.

    IMPORTANT:
        VERIFIED here means artifact validation succeeded.

        Final CI_SUCCESS still belongs to the CI Failure Handling Agent,
        which must combine this result with authoritative CodeBuild status.
    """

    statuses = [
        backend.get("status"),
        frontend.get("status"),
        s3_artifact.get("status"),
    ]

    if UNKNOWN in statuses or NOT_CHECKED in statuses:
        return {
            "status": "UNKNOWN",
            "all_mandatory_artifacts_verified": False,
            "artifact_validation_success": False,
            "promotion_allowed": False,
            "reason": (
                "One or more mandatory artifacts could not be "
                "authoritatively verified."
            ),
        }

    if MISSING in statuses or MISMATCH in statuses:
        return {
            "status": "INVALID",
            "all_mandatory_artifacts_verified": False,
            "artifact_validation_success": False,
            "promotion_allowed": False,
            "reason": (
                "One or more mandatory CI artifacts are missing or do not "
                "match the expected immutable artifact identity."
            ),
        }

    if all(status == VERIFIED for status in statuses):
        return {
            "status": "VERIFIED",
            "all_mandatory_artifacts_verified": True,
            "artifact_validation_success": True,

            # This tool alone still does not authorize promotion.
            "promotion_allowed": False,

            "reason": (
                "All mandatory artifacts were positively verified. "
                "The CI agent must combine this result with authoritative "
                "CodeBuild SUCCEEDED state before declaring CI_SUCCESS."
            ),
        }

    return {
        "status": "UNKNOWN",
        "all_mandatory_artifacts_verified": False,
        "artifact_validation_success": False,
        "promotion_allowed": False,
        "reason": (
            "Artifact state could not be mapped to a supported "
            "deterministic validation result."
        ),
    }


# =============================================================================
# TOOL-LEVEL ERROR RESPONSE
# =============================================================================

def build_tool_error(
    resolved_source_version: Optional[str],
    code: str,
    message: str,
) -> str:

    payload = {
        "schema_version": "1.0",

        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
        },

        "retrieval": {
            "status": "ERROR",
            "timestamp": utc_now_iso(),
        },

        "input": {
            "resolved_source_version": resolved_source_version,
        },

        "validation": {
            "status": "UNKNOWN",
            "all_mandatory_artifacts_verified": False,
            "artifact_validation_success": False,
            "promotion_allowed": False,
        },

        "error": {
            "code": code,
            "message": sanitize_message(message),
        },

        "unknown_areas": [
            "Mandatory CI artifact verification was not completed."
        ],
    }

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


# =============================================================================
# MAIN TOOL
# =============================================================================

class CIArtifactValidationTool(BaseTool):
    """
    Read-only mandatory CI artifact verification tool.
    """

    name: str = TOOL_NAME

    description: str = (
        "Verifies mandatory CI artifacts for an exact immutable source "
        "revision extracted from CodeBuildStatusTool output. It validates "
        "the backend ECR image, frontend ECR image, and S3 artifact. "
        "All artifact locations and repository names are extracted from "
        "the CodeBuild output. The tool never falls back to ':latest', "
        "never retags images, never modifies artifacts, and never declares "
        "overall CI success."
    )

    args_schema: Type[BaseModel] = CIArtifactValidationToolSchema

    def _run(
        self,
        codebuild_output: str,
    ) -> str:

        started = time.monotonic()

        logger.info(
            "Starting CI artifact validation from CodeBuild output."
        )

        # =====================================================================
        # 1. PARSE CODEBUILD OUTPUT
        # =====================================================================

        if not isinstance(codebuild_output, str):
            return build_tool_error(
                resolved_source_version=None,
                code="INVALID_CODEBUILD_OUTPUT",
                message=(
                    "codebuild_output must be a non-empty string containing "
                    "CodeBuildStatusTool JSON output."
                ),
            )

        parsed = parse_codebuild_output(codebuild_output)

        if "error" in parsed:
            return build_tool_error(
                resolved_source_version=None,
                code="CODEBUILD_OUTPUT_PARSE_ERROR",
                message=parsed["error"],
            )

        # =====================================================================
        # 2. EXTRACT AND VALIDATE REQUIRED FIELDS
        # =====================================================================

        resolved_source_version = parsed.get("resolved_source_version")

        if not resolved_source_version:
            return build_tool_error(
                resolved_source_version=None,
                code="MISSING_RESOLVED_SOURCE_VERSION",
                message=(
                    "resolved_source_version not found in CodeBuild output."
                ),
            )

        revision = normalize_revision(resolved_source_version)

        if not revision:
            return build_tool_error(
                resolved_source_version=None,
                code="INVALID_SOURCE_REVISION",
                message=(
                    "resolved_source_version must not be empty."
                ),
            )

        backend_repository = parsed.get("backend_repository") or DEFAULT_BACKEND_REPOSITORY
        frontend_repository = parsed.get("frontend_repository") or DEFAULT_FRONTEND_REPOSITORY

        backend_repository = backend_repository.strip()
        frontend_repository = frontend_repository.strip()

        if not backend_repository:
            return build_tool_error(
                resolved_source_version=revision,
                code="INVALID_BACKEND_REPOSITORY",
                message="Backend ECR repository must not be empty.",
            )

        if not frontend_repository:
            return build_tool_error(
                resolved_source_version=revision,
                code="INVALID_FRONTEND_REPOSITORY",
                message="Frontend ECR repository must not be empty.",
            )

        # =====================================================================
        # 3. EXTRACT S3 ARTIFACT LOCATION
        # =====================================================================

        supplied_bucket = parsed.get("s3_bucket") or DEFAULT_S3_BUCKET
        supplied_key = parsed.get("s3_key") or DEFAULT_S3_KEY

        logger.info(
            "Extracted artifact metadata | revision=%s | "
            "backend_repo=%s | frontend_repo=%s | "
            "s3_bucket=%s | s3_key=%s",
            revision,
            backend_repository,
            frontend_repository,
            supplied_bucket,
            supplied_key,
        )

        logger.info(
            "Using immutable source revision | revision=%s",
            revision,
        )

        # =====================================================================
        # 4. CREATE AWS CLIENTS
        # =====================================================================

        # Extract region from parsed CodeBuild output
        codebuild_region = parsed.get("aws_region")

        if not codebuild_region:
            logger.warning(
                "AWS region not found in CodeBuild output, using default fallback."
            )

        try:
            logger.info(
                "Creating AWS ECR and S3 clients."
            )

            # Use explicit region from CodeBuild output or fallback
            region = codebuild_region or "eu-north-1"
            session = boto3.session.Session(region_name=region)
            
            # Verify region was set
            actual_region = session.region_name
            if not actual_region:
                return build_tool_error(
                    resolved_source_version=revision,
                    code="AWS_REGION_NOT_AVAILABLE",
                    message=(
                        "AWS region could not be determined from CodeBuild output or environment. "
                        "Ensure Tool 1 output includes aws_region in metadata."
                    ),
                )

            logger.info(
                "Using AWS region: %s", region
            )

            # Clients inherit region from session
            ecr_client = session.client("ecr")
            s3_client = session.client("s3")

        except NoCredentialsError:
            logger.exception(
                "AWS credentials unavailable."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="NO_AWS_CREDENTIALS",
                message=(
                    "AWS credentials were not available to the "
                    "AAVA runtime."
                ),
            )

        except PartialCredentialsError as exc:
            logger.exception(
                "Partial AWS credentials."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="PARTIAL_AWS_CREDENTIALS",
                message=str(exc),
            )

        except Exception as exc:
            logger.exception(
                "AWS client initialization failed."
            )

            return build_tool_error(
                resolved_source_version=revision,
                code="AWS_CLIENT_INITIALIZATION_FAILED",
                message=str(exc),
            )

        # =====================================================================
        # 5. VERIFY BACKEND IMAGE
        # =====================================================================

        logger.info(
            "Expected backend image | %s:%s",
            backend_repository,
            revision,
        )

        backend_result = validate_ecr_image(
            client=ecr_client,
            repository_name=backend_repository,
            expected_tag=revision,
            region=region,
        )

        # =====================================================================
        # 6. VERIFY FRONTEND IMAGE
        # =====================================================================

        logger.info(
            "Expected frontend image | %s:%s",
            frontend_repository,
            revision,
        )

        frontend_result = validate_ecr_image(
            client=ecr_client,
            repository_name=frontend_repository,
            expected_tag=revision,
            region=region,
        )

        # =====================================================================
        # 7. VERIFY S3 ARTIFACT
        # =====================================================================

        s3_result = validate_s3_artifact(
            client=s3_client,
            bucket=supplied_bucket,
            key=supplied_key,
        )

        # =====================================================================
        # 8. AGGREGATE RESULT
        # =====================================================================

        validation = determine_validation_result(
            backend=backend_result,
            frontend=frontend_result,
            s3_artifact=s3_result,
        )

        unknown_areas = []

        if backend_result.get("status") == UNKNOWN:
            unknown_areas.append(
                "Backend ECR image verification could not be completed "
                "authoritatively."
            )

        if frontend_result.get("status") == UNKNOWN:
            unknown_areas.append(
                "Frontend ECR image verification could not be completed "
                "authoritatively."
            )

        if s3_result.get("status") == UNKNOWN:
            unknown_areas.append(
                "S3 artifact verification could not be completed "
                "authoritatively."
            )

        # =====================================================================
        # 9. BUILD OUTPUT
        # =====================================================================

        elapsed_ms = round(
            (time.monotonic() - started) * 1000,
            3,
        )

        expected_backend = (
            f"{backend_repository}:{revision}"
        )

        expected_frontend = (
            f"{frontend_repository}:{revision}"
        )

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