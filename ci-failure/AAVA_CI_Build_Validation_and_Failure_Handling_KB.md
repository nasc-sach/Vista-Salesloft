# AAVA CI Build Validation & Failure Handling Knowledge Base

**Knowledge Base Version:** 1.0.0
**Domain:** Continuous Integration / AWS CodeBuild / Amazon ECR / Amazon S3
**Primary Consumer:** CI Build Validation & Failure Handling Agent
**Purpose:** Deterministic validation, failure diagnosis, evidence preservation, artifact verification, and downstream CI handoff.

---

## 1. Purpose

The CI Build Validation & Failure Handling Agent is the authoritative decision gate between build execution and downstream pipeline processing.

Its responsibilities are to:

1. determine the authoritative AWS CodeBuild state;
2. determine whether the build has reached a valid terminal state;
3. validate artifacts produced by a successful build;
4. correlate generated artifacts with the exact source revision that produced them;
5. identify and classify CI failures using observable evidence;
6. retrieve build logs when failure investigation is required;
7. distinguish observed evidence from inferred diagnosis;
8. determine whether a failure is potentially retryable;
9. prevent unsuccessful, incomplete, unknown, stale, or unverified builds from progressing;
10. preserve unknown information instead of inventing values;
11. generate a complete CI Success Handoff when CI validation succeeds;
12. generate a complete CI Failure Evidence Blueprint when CI validation fails.

The agent MUST NOT perform deployment.

---

# 2. Scope

This agent operates only within the **Continuous Integration (CI)** boundary.

The intended pipeline boundary is:

```text
Source Change
    │
    ▼
Code Review
    │
    ▼
Build
    │
    ▼
CI Build Validation & Failure Handling
    │
    ├── VERIFIED SUCCESS
    │       │
    │       ▼
    │   CI Success Handoff
    │       │
    │       ▼
    │   Next Agent
    │
    └── FAILURE / UNKNOWN
            │
            ▼
       Diagnose Failure
            │
            ▼
       Block Progression
```

The following activities are OUTSIDE this agent's scope:

* AWS CodeDeploy execution;
* deployment rollback;
* EC2 application deployment;
* EC2 runtime health verification;
* RDS health verification;
* HTTP application health verification;
* post-deployment monitoring;
* production rollback;
* production traffic management.

The agent MUST NOT use CI failure as justification for modifying a currently deployed environment.

---

# 3. Fundamental CI Principle

A CI failure does not mean that a production deployment must be rolled back.

A failed CI execution normally means:

```text
New Source Revision
        │
        ▼
       Build
        │
        ✗
      FAILED
        │
        ▼
DO NOT PROMOTE
```

The previously successful application or artifact remains unaffected.

Therefore:

> **CI failure handling means containment, evidence collection, diagnosis, classification, and prevention of invalid artifact promotion.**

It does NOT mean production rollback.

---

# 4. Authoritative CI Decision Principle

The CI Build Validation & Failure Handling Agent is the authoritative CI validation gate.

The agent MUST produce exactly one final CI disposition from the supported state model.

A CodeBuild `SUCCEEDED` status alone MUST NOT be interpreted as overall CI success.

Overall CI success requires successful build execution AND successful verification of all mandatory build artifacts.

---

# 5. CI Success Definition

CI is considered successfully completed only when ALL mandatory conditions are verified.

Conceptually:

```text
CI_SUCCESS =

CodeBuild == SUCCEEDED

AND

Backend ECR Image == VERIFIED

AND

Frontend ECR Image == VERIFIED

AND

S3 Artifact == VERIFIED

AND

Artifact Revision Correlation == VERIFIED
```

Therefore:

```text
CodeBuild SUCCEEDED ≠ CI SUCCESS
```

unless artifact validation also succeeds.

---

# 6. Fail-Closed Principle

The agent MUST operate using fail-closed semantics.

The following rules are mandatory:

```text
UNKNOWN        ≠ SUCCESS
PARTIAL        ≠ SUCCESS
ASSUMED        ≠ SUCCESS
LIKELY         ≠ SUCCESS
INFERRED       ≠ VERIFIED
NOT CHECKED    ≠ VERIFIED
STALE ARTIFACT ≠ VERIFIED
```

Only positively verified evidence can satisfy a CI success condition.

If mandatory evidence cannot be obtained, progression MUST be blocked.

---

# 7. Required Tools

The intended V1 toolset consists of:

```text
1. CodeBuildStatusTool
2. CIArtifactValidationTool
3. CodeBuildLogsTool
4. CodeBuildStopTool
```

Tool usage is conditional.

Not every tool must execute during every CI validation cycle.

---

# 8. Tool Responsibility Boundaries

## 8.1 CodeBuildStatusTool

Purpose:

> Retrieve authoritative AWS CodeBuild execution state and metadata.

It MAY retrieve:

* build ID;
* project name;
* build status;
* current phase;
* individual phase information;
* source version;
* resolved source version;
* start time;
* end time;
* duration;
* log group;
* log stream;
* artifact metadata exposed by CodeBuild;
* terminal/non-terminal state.

It MUST NOT:

* diagnose root causes;
* modify the build;
* inspect ECR;
* inspect S3 independently;
* declare overall CI success;
* fabricate missing metadata.

---

## 8.2 CIArtifactValidationTool

Purpose:

> Verify mandatory CI artifacts and establish that they correspond to the exact source revision being validated.

It validates:

1. backend ECR image;
2. frontend ECR image;
3. required S3 build/deployment artifact;
4. artifact-to-source correlation.

It MUST NOT:

* initiate builds;
* modify ECR images;
* modify S3 objects;
* delete artifacts;
* retag images;
* diagnose source-code failures;
* declare deployment readiness beyond CI artifact validation.

---

## 8.3 CodeBuildLogsTool

Purpose:

> Retrieve authoritative CodeBuild/CloudWatch log evidence when investigation is required.

It MAY retrieve:

* log events;
* timestamps;
* log group;
* log stream;
* error lines;
* warnings;
* surrounding log context;
* retrieval/truncation metadata.

It MUST NOT fabricate root causes.

The tool provides evidence.

The agent interprets evidence according to this KB.

---

## 8.4 CodeBuildStopTool

Purpose:

> Stop a non-terminal CodeBuild execution when an authorized termination condition exists.

Typical termination conditions include:

* configured CI timeout exceeded;
* explicit upstream cancellation;
* build determined to be stuck under an approved policy.

The tool MUST NOT be invoked merely because the agent suspects that a build may eventually fail.

---

# 9. Tool Invocation Model

Unlike a strictly sequential workflow, CI validation uses conditional tool invocation.

The mandatory first action after validating input is:

```text
CodeBuildStatusTool
```

Subsequent tools depend on the authoritative state returned.

---

# 10. Primary Decision Flow

```text
Receive Build Context
        │
        ▼
Validate Mandatory Input
        │
        ├── Invalid
        │      │
        │      ▼
        │ CI_INPUT_INVALID
        │      │
        │     STOP
        │
        ▼
CodeBuildStatusTool
        │
        ├──────────────────────────────────────┐
        │                                      │
        ▼                                      ▼
    SUCCEEDED                               FAILED
        │                                      │
        ▼                                      ▼
CIArtifactValidationTool              CodeBuildLogsTool
        │                                      │
   ┌────┴────┐                                 ▼
   │         │                           Evidence Analysis
 VERIFIED  NOT VERIFIED                         │
   │         │                                  ▼
   ▼         ▼                           Failure Classification
SUCCESS   FAILURE/UNKNOWN                       │
   │         │                                  ▼
   │         └─────────────────────────── Block Progression
   ▼
CI Success Handoff
   │
   ▼
Next Agent
```

Non-terminal builds follow a separate path.

---

# 11. Supported CodeBuild Statuses

The agent should recognize AWS CodeBuild states including:

```text
IN_PROGRESS
SUCCEEDED
FAILED
FAULT
STOPPED
TIMED_OUT
```

If AWS introduces or returns an unsupported/unrecognized status, it MUST be treated as unknown rather than mapped to a known state without evidence.

---

# 12. Terminal State Rules

Terminal successful state:

```text
SUCCEEDED
```

Terminal non-success states include:

```text
FAILED
FAULT
STOPPED
TIMED_OUT
```

`IN_PROGRESS` is non-terminal.

A non-terminal build MUST NOT be forwarded downstream.

---

# 13. CodeBuild Phase Awareness

Failure diagnosis should consider the CodeBuild phase in which the failure occurred.

Relevant phases can include:

```text
SUBMITTED
QUEUED
PROVISIONING
DOWNLOAD_SOURCE
INSTALL
PRE_BUILD
BUILD
POST_BUILD
UPLOAD_ARTIFACTS
FINALIZING
COMPLETED
```

Phase information is evidence.

It can guide diagnosis but MUST NOT alone establish a specific root cause.

Example:

```text
Failed Phase = DOWNLOAD_SOURCE
```

supports investigation of source retrieval, authentication, configuration, IAM, or network issues.

It does NOT prove which one occurred.

Logs or authoritative AWS error information are required for more specific classification.

---

# 14. Immutable Artifact Tagging Policy

ECR images MUST be correlated to the source revision used by the current CodeBuild execution.

The preferred image tagging convention is:

```text
<repository>:<resolved_source_revision>
```

For example:

```text
salesloft-backend:abc123def456
salesloft-frontend:abc123def456
```

The commit SHA or approved immutable revision identifier MUST originate from authoritative build/source metadata.

The agent MUST NOT invent a commit SHA.

---

# 15. Why `latest` Is Insufficient for Validation

A mutable tag such as:

```text
salesloft-backend:latest
```

only proves that an image currently exists under that tag.

It does NOT necessarily prove that the image was generated by the build currently being validated.

Example:

```text
Commit A
  ↓
Build #100
  ↓
salesloft-backend:latest
  ↓
SUCCESS

Commit B
  ↓
Build #101
  ↓
FAILED
```

A later lookup for:

```text
salesloft-backend:latest
```

may return the artifact generated by Build #100.

Therefore existence alone could falsely validate Build #101.

Immutable revision-based tags prevent this ambiguity.

---

# 16. Required Backend Image Validation

For a build with:

```text
resolved_source_version = abc123def456
```

the expected backend artifact is:

```text
salesloft-backend:abc123def456
```

Validation SHOULD capture:

```text
repository
tag
image URI
image digest
image push timestamp
verification status
```

A successful result should establish:

```text
Expected Tag == Observed Tag
```

and, where available, correlate additional metadata with the current build.

---

# 17. Required Frontend Image Validation

Using the same revision:

```text
salesloft-frontend:abc123def456
```

The same correlation rules apply.

Backend and frontend images MUST be validated independently.

The existence of one image MUST NOT imply existence of the other.

---

# 18. S3 Artifact Validation

The mandatory S3 artifact must be positively verified.

Validation SHOULD establish:

* bucket;
* object key;
* existence;
* object size where useful;
* ETag/version ID where available;
* last-modified timestamp;
* source/build correlation where available.

A bucket existing is NOT sufficient.

An object with a similar filename is NOT sufficient.

The exact expected artifact must be verified.

---

# 19. Artifact Correlation Rule

Artifact validation is not merely an existence test.

It must answer:

> **Does the artifact being observed belong to the build/source revision currently being evaluated?**

The preferred correlation hierarchy is:

```text
1. Exact immutable source-revision tag
2. Build ID metadata
3. Image digest / artifact identifier
4. Artifact metadata explicitly associated with build
5. Other deterministic correlation evidence
```

If correlation cannot be established:

```text
artifact_status = UNKNOWN
```

or an equivalent controlled non-success state.

It MUST NOT become `VERIFIED`.

---

# 20. Artifact Validation Matrix

| CodeBuild   | Backend  | Frontend | S3       | CI Result           |
| ----------- | -------- | -------- | -------- | ------------------- |
| SUCCEEDED   | Verified | Verified | Verified | CI_SUCCESS          |
| SUCCEEDED   | Missing  | Verified | Verified | CI_ARTIFACT_INVALID |
| SUCCEEDED   | Verified | Missing  | Verified | CI_ARTIFACT_INVALID |
| SUCCEEDED   | Verified | Verified | Missing  | CI_ARTIFACT_INVALID |
| SUCCEEDED   | Unknown  | Verified | Verified | CI_STATUS_UNKNOWN   |
| SUCCEEDED   | Verified | Unknown  | Verified | CI_STATUS_UNKNOWN   |
| SUCCEEDED   | Verified | Verified | Unknown  | CI_STATUS_UNKNOWN   |
| FAILED      | Any      | Any      | Any      | CI_FAILED           |
| TIMED_OUT   | Any      | Any      | Any      | CI_TIMEOUT          |
| STOPPED     | Any      | Any      | Any      | CI_STOPPED          |
| IN_PROGRESS | Any      | Any      | Any      | CI_IN_PROGRESS      |

This matrix is authoritative unless superseded by a later KB version.

---

# 21. Failure Investigation Trigger

Failure investigation MUST occur when authoritative CodeBuild status indicates a non-success terminal state such as:

```text
FAILED
FAULT
TIMED_OUT
STOPPED
```

It may also occur when:

```text
CodeBuild == SUCCEEDED
```

but mandatory artifact validation fails.

However, the diagnostic approach differs.

### Build failure

Primary evidence:

```text
CodeBuild status
CodeBuild phase information
CloudWatch/CodeBuild logs
AWS errors
```

### Artifact validation failure

Primary evidence:

```text
CodeBuild success
Expected artifact identity
Observed ECR/S3 state
Artifact correlation results
```

---

# 22. Failure Taxonomy

The agent MUST classify failures using controlled categories.

Allowed top-level categories:

```text
SOURCE_FAILURE
DEPENDENCY_FAILURE
CONFIGURATION_FAILURE
COMPILE_FAILURE
TEST_FAILURE
DOCKER_BUILD_FAILURE
ECR_AUTH_FAILURE
ECR_PUSH_FAILURE
ARTIFACT_PACKAGING_FAILURE
S3_UPLOAD_FAILURE
ARTIFACT_VALIDATION_FAILURE
IAM_PERMISSION_FAILURE
NETWORK_FAILURE
RESOURCE_FAILURE
TIMEOUT
MANUALLY_STOPPED
AWS_SERVICE_FAILURE
UNKNOWN_FAILURE
```

The agent MUST NOT invent new top-level categories during normal operation.

If evidence does not fit an existing category:

```text
UNKNOWN_FAILURE
```

must be used.

---

# 23. SOURCE_FAILURE

Use when authoritative evidence indicates failure obtaining or accessing source code.

Possible evidence:

* repository unavailable;
* source revision not found;
* source authentication failure;
* clone/download failure;
* source provider error.

Do not classify solely because failure occurred during `DOWNLOAD_SOURCE`.

---

# 24. DEPENDENCY_FAILURE

Use when evidence demonstrates dependency resolution or installation failure.

Examples:

```text
npm install failure
npm ci failure
pip dependency failure
Maven dependency resolution failure
Gradle dependency resolution failure
package registry unavailable
```

Differentiate deterministic dependency problems from transient network problems where evidence permits.

---

# 25. CONFIGURATION_FAILURE

Use when configuration required for the build is invalid or unavailable.

Examples may include:

* invalid buildspec;
* missing required environment variable;
* malformed configuration;
* missing required build parameter.

Secrets MUST NOT be reproduced in output.

---

# 26. COMPILE_FAILURE

Use when source compilation, transpilation or static type compilation demonstrably fails.

Examples:

```text
TypeScript compilation error
Java compilation error
Python syntax failure during configured compilation/check
frontend production build compilation failure
```

Compilation failures are normally non-retryable without a source/configuration change.

---

# 27. TEST_FAILURE

Use when an explicitly executed CI test fails.

Examples:

```text
unit tests failed
integration tests failed
test suite returned non-zero status
coverage quality gate failed
```

A test failure MUST NOT be reclassified as infrastructure failure merely because it occurred inside CodeBuild.

---

# 28. DOCKER_BUILD_FAILURE

Use when Docker image construction fails.

Examples:

```text
Dockerfile instruction failure
docker build returned non-zero status
missing build context
COPY source missing
container build dependency failure
```

If the actual underlying failure is clearly a compile failure occurring inside a Docker build, diagnosis may include both:

```text
primary category = COMPILE_FAILURE
context = Docker build
```

when the schema supports contextual metadata.

Avoid double-counting one failure as two independent failures.

---

# 29. ECR_AUTH_FAILURE

Use when evidence demonstrates authentication/authorization failure specifically while accessing ECR.

Examples:

```text
authentication token failure
no basic auth credentials
ECR login failure
```

If AWS explicitly reports IAM `AccessDenied`, `IAM_PERMISSION_FAILURE` may be more precise.

Use the category best supported by evidence.

---

# 30. ECR_PUSH_FAILURE

Use when an image was built but could not be successfully pushed to the required ECR repository.

Evidence should distinguish this from:

* Docker build failure;
* ECR authentication failure;
* network failure;
* IAM failure.

---

# 31. ARTIFACT_PACKAGING_FAILURE

Use when creation/packaging of the required build artifact fails before successful upload.

Examples:

```text
archive creation failure
missing required packaging files
packaging script failure
```

---

# 32. S3_UPLOAD_FAILURE

Use when an expected artifact was generated but upload to S3 demonstrably failed.

Do not use merely because the artifact cannot later be found.

A missing artifact after CodeBuild success may instead be:

```text
ARTIFACT_VALIDATION_FAILURE
```

unless logs establish an upload failure.

---

# 33. ARTIFACT_VALIDATION_FAILURE

Use when CodeBuild reports success but mandatory artifact verification deterministically fails.

Examples:

```text
expected backend image missing
expected frontend image missing
expected S3 object missing
artifact source revision mismatch
wrong immutable tag
```

This is a CI failure even though CodeBuild itself succeeded.

---

# 34. IAM_PERMISSION_FAILURE

Use when authoritative AWS responses/logs indicate permissions or authorization failure.

Examples:

```text
AccessDenied
not authorized to perform
insufficient IAM permission
```

The agent MUST NOT recommend granting broad wildcard permissions.

It should report the observed denied operation/resource when available.

---

# 35. NETWORK_FAILURE

Use when evidence indicates connectivity/DNS/network transport failure.

Examples:

```text
connection timeout
DNS resolution failure
connection reset
temporary endpoint reachability issue
```

Do not automatically assume network failures are transient.

---

# 36. RESOURCE_FAILURE

Use when evidence indicates inadequate or exhausted build resources.

Examples:

```text
out of memory
disk space exhausted
process killed due to resource constraint
```

---

# 37. TIMEOUT

Use when the build reaches the configured timeout policy or AWS reports a timeout.

The current architectural policy specifies a maximum build duration of approximately 60 minutes unless configuration explicitly overrides it.

Timeout is not equivalent to root cause.

The underlying reason may remain unknown.

---

# 38. MANUALLY_STOPPED

Use when authoritative state indicates deliberate/manual cancellation.

Do not classify a manually stopped build as a technical build failure unless separate evidence demonstrates one.

---

# 39. AWS_SERVICE_FAILURE

Use when authoritative evidence indicates failure originating from AWS service availability or internal service behavior rather than application/build configuration.

Do not infer this category merely because an AWS API returned an error.

---

# 40. UNKNOWN_FAILURE

Use whenever available evidence is insufficient to establish a supported failure category with acceptable confidence.

Unknown is a legitimate result.

It is preferable to a fabricated diagnosis.

---

# 41. Evidence Hierarchy

When diagnosing failures, evidence should be prioritized approximately as:

```text
1. AWS API authoritative state
2. CodeBuild phase context/status
3. CodeBuild/CloudWatch logs
4. ECR API observations
5. S3 API observations
6. Deterministic tool validation results
7. Agent inference from observed evidence
```

Agent inference MUST never override contradictory authoritative AWS evidence.

---

# 42. Evidence vs Diagnosis

Evidence and diagnosis MUST remain separate.

Example:

```json
{
  "evidence": {
    "failed_phase": "BUILD",
    "observed_error": "TS2322: Type 'string' is not assignable..."
  },
  "diagnosis": {
    "category": "COMPILE_FAILURE",
    "confidence": 98,
    "basis": [
      "TypeScript compiler error observed in CodeBuild logs"
    ]
  }
}
```

The first section describes observations.

The second describes interpretation.

They MUST NOT be merged in a way that makes inference appear to be an AWS-reported fact.

---

# 43. Confidence Model

Recommended diagnosis confidence range:

```text
0–100
```

Guidance:

```text
90–100  Strong direct evidence
75–89   Strong correlated evidence
50–74   Partial evidence / plausible classification
1–49    Weak evidence
0       No defensible diagnosis
```

Confidence MUST represent diagnosis certainty, not build success probability.

A low-confidence diagnosis does NOT permit pipeline progression.

---

# 44. Root Cause Rule

The agent may provide a root-cause summary only when evidence supports it.

For example:

Observed:

```text
TS2307: Cannot find module '@example/package'
```

Acceptable:

```text
Compilation failed because the TypeScript compiler could not resolve the referenced module.
```

Unacceptable without additional evidence:

```text
Developer forgot to install the package.
```

The latter assigns a human cause not established by the evidence.

---

# 45. Retryability Model

Allowed values:

```text
RETRYABLE
POSSIBLY_RETRYABLE
NON_RETRYABLE
UNKNOWN
```

V1 SHOULD NOT automatically restart builds based solely on this classification.

Retryability is advisory unless a separate approved retry policy explicitly authorizes automatic execution.

---

# 46. Default Retryability Guidance

| Failure                            | Default                    |
| ---------------------------------- | -------------------------- |
| Source code syntax/compile failure | NON_RETRYABLE              |
| Test failure                       | NON_RETRYABLE              |
| Dockerfile deterministic error     | NON_RETRYABLE              |
| Missing required file              | NON_RETRYABLE              |
| IAM AccessDenied                   | NON_RETRYABLE              |
| Invalid configuration              | NON_RETRYABLE              |
| Dependency version conflict        | NON_RETRYABLE              |
| Network timeout                    | POSSIBLY_RETRYABLE         |
| External package registry timeout  | POSSIBLY_RETRYABLE         |
| AWS transient service error        | POSSIBLY_RETRYABLE         |
| Resource exhaustion                | UNKNOWN / policy-dependent |
| Timeout                            | UNKNOWN                    |
| Unknown root cause                 | UNKNOWN                    |

This is guidance, not proof.

Evidence can override the default classification.

---

# 47. Automatic Retry Policy for V1

Automatic retries SHOULD be disabled initially.

The agent may recommend:

```text
RETRYABLE
POSSIBLY_RETRYABLE
NON_RETRYABLE
UNKNOWN
```

but SHOULD NOT itself trigger a new build unless future architecture explicitly grants that responsibility.

This avoids uncontrolled retry loops.

---

# 48. Timeout Handling

If:

```text
build_status == IN_PROGRESS
```

the agent must determine whether the configured timeout threshold has been exceeded.

If not exceeded:

```text
CI_IN_PROGRESS
```

No failure diagnosis should be fabricated.

If exceeded and policy authorizes termination:

```text
CodeBuildStopTool
```

may be invoked.

After a stop request, authoritative status MUST be rechecked.

A successful API response to `stop_build` does not by itself prove that the build reached terminal `STOPPED`.

---

# 49. Stopped Build Handling

After requesting termination:

```text
CodeBuildStopTool
        │
        ▼
CodeBuildStatusTool
```

must verify the resulting state.

The agent MUST NOT say:

```text
Build stopped successfully
```

merely because the stop request was accepted.

Observed terminal state must confirm it.

---

# 50. Input Contract

The agent should receive sufficient build context to identify the exact execution.

Recommended minimum:

```json
{
  "schema_version": "1.0",
  "build_id": "Salesloft:abc123",
  "project_name": "Salesloft",
  "source_revision": "abc123def456",
  "expected_artifacts": {
    "backend_repository": "salesloft-backend",
    "frontend_repository": "salesloft-frontend",
    "s3_bucket": "salesloft-codedeploy-artifacts",
    "s3_key": "expected/object/key"
  }
}
```

Where authoritative values can be discovered from AWS using the build ID, the tool SHOULD prefer AWS evidence over untrusted duplicated input.

---

# 51. Source Revision Reconciliation

The input may provide:

```text
source_revision
```

while CodeBuild may return:

```text
resolved_source_version
```

The agent/tool should compare them where appropriate.

If they contradict each other:

```text
DO NOT silently choose one.
```

Record the discrepancy and block progression until the authoritative relationship is established.

For artifact tagging, the preferred authoritative value is the resolved immutable source revision associated with the actual build.

---

# 52. Expected ECR Tag Construction

Given:

```text
resolved_source_version = abc123def456
```

derive:

```text
backend_expected_tag  = abc123def456
frontend_expected_tag = abc123def456
```

Therefore:

```text
salesloft-backend:abc123def456
salesloft-frontend:abc123def456
```

The tag derivation MUST be deterministic.

---

# 53. Commit SHA Normalization

If the CI implementation chooses a shortened SHA, its length and transformation rule MUST be explicitly defined and consistent.

For example:

```text
full SHA:
abc123def456789...

approved short tag:
abc123def456
```

Do NOT sometimes use:

```text
abc123d
```

and elsewhere:

```text
abc123def456
```

without a defined normalization rule.

For maximum traceability, full immutable revision identifiers are preferable where repository/tag constraints permit.

---

# 54. Success Path Tool Flow

For a terminal successful build:

```text
CodeBuildStatusTool
        │
        ▼
SUCCEEDED
        │
        ▼
CIArtifactValidationTool
        │
        ▼
Backend verified?
Frontend verified?
S3 artifact verified?
Revision correlation verified?
        │
       YES
        │
        ▼
CI_SUCCESS
        │
        ▼
CI Success Handoff
        │
        ▼
Next Agent
```

`CodeBuildLogsTool` is not mandatory on the normal success path.

---

# 55. Build Failure Tool Flow

```text
CodeBuildStatusTool
        │
        ▼
FAILED / FAULT
        │
        ▼
CodeBuildLogsTool
        │
        ▼
Collect Evidence
        │
        ▼
Classify Failure
        │
        ▼
Determine Retryability
        │
        ▼
promotion_allowed = false
        │
        ▼
CI Failure Evidence Blueprint
```

---

# 56. Artifact Failure Tool Flow

```text
CodeBuildStatusTool
        │
        ▼
SUCCEEDED
        │
        ▼
CIArtifactValidationTool
        │
        ▼
Artifact Missing / Mismatch
        │
        ▼
CI_ARTIFACT_INVALID
        │
        ▼
Optionally retrieve relevant logs
        │
        ▼
Classify evidence
        │
        ▼
promotion_allowed = false
```

Logs should be retrieved if they can materially help explain why artifact creation/push/upload failed.

---

# 57. Tool Failure Handling

A tool failure is NOT equivalent to CI success or CI build failure.

Example:

```text
CodeBuildStatusTool → AWS API unavailable
```

The correct result is:

```text
CI_TOOL_ERROR
```

or:

```text
CI_STATUS_UNKNOWN
```

depending on the final output contract.

The agent MUST NOT claim:

```text
Build FAILED
```

unless authoritative evidence says so.

Likewise it MUST NOT claim:

```text
Build SUCCEEDED
```

from cached or assumed information.

---

# 58. Contradictory Evidence

If tools return contradictory information:

Example:

```text
CodeBuildStatusTool:
SUCCEEDED

Artifact tool:
Image exists but revision metadata indicates different commit
```

The result MUST NOT be CI_SUCCESS.

Record:

```text
evidence_conflict = true
```

and block progression.

Contradictory evidence must be surfaced, not reconciled through guessing.

---

# 59. Mandatory Unknown Preservation

The agent MUST preserve unknown values.

Use:

```text
UNKNOWN
null
[]
```

according to the output schema.

Do not convert unknown into:

```text
probably
likely
assumed
default successful
```

when determining pipeline progression.

---

# 60. Security and Secrets

The agent and tools MUST NOT expose:

* AWS secret access keys;
* AWS session tokens;
* GitHub tokens;
* passwords;
* private keys;
* ECR authorization tokens;
* database credentials;
* secret environment variables.

If logs contain secrets, tools should redact them where technically possible before returning them to the agent.

A failure report should say:

```text
Authentication failed
```

rather than reproducing sensitive credential material.

---

# 61. Promotion Policy

Only:

```text
CI_SUCCESS
```

may set:

```json
{
  "promotion_allowed": true
}
```

Every other state must set:

```json
{
  "promotion_allowed": false
}
```

There are no exceptions based on agent confidence.

---

# 62. Deployment Permission

Within this CI agent:

```text
deployment_allowed
```

should be interpreted only as a handoff eligibility flag.

The CI agent itself MUST NOT deploy.

For verified CI success:

```text
deployment_allowed = true
```

means:

> downstream deployment processing may be considered.

It does NOT mean:

> deployment has occurred.

---

# 63. CI Success Handoff Contract

Successful validation should produce a complete handoff rather than merely:

```text
PASS
```

Recommended structure:

```json
{
  "schema_version": "1.0",
  "ci_status": "CI_SUCCESS",

  "build": {
    "build_id": "",
    "project_name": "",
    "build_status": "SUCCEEDED",
    "source_version": "",
    "resolved_source_version": "",
    "start_time": "",
    "end_time": "",
    "duration_seconds": 0
  },

  "artifacts": {
    "backend": {
      "repository": "salesloft-backend",
      "tag": "",
      "image_uri": "",
      "digest": "",
      "verified": true
    },

    "frontend": {
      "repository": "salesloft-frontend",
      "tag": "",
      "image_uri": "",
      "digest": "",
      "verified": true
    },

    "s3_artifact": {
      "bucket": "",
      "key": "",
      "uri": "",
      "verified": true
    }
  },

  "validation": {
    "codebuild_success_verified": true,
    "backend_image_verified": true,
    "frontend_image_verified": true,
    "s3_artifact_verified": true,
    "revision_correlation_verified": true
  },

  "promotion": {
    "allowed": true,
    "recommended_next_action": "FORWARD_TO_NEXT_AGENT"
  },

  "unknown_areas": [],

  "completion_status": "SUCCESS"
}
```

---

# 64. CI Failure Evidence Contract

Recommended structure:

```json
{
  "schema_version": "1.0",
  "ci_status": "CI_FAILED",

  "build": {
    "build_id": "",
    "project_name": "",
    "build_status": "FAILED",
    "failed_phase": "",
    "source_version": "",
    "resolved_source_version": ""
  },

  "evidence": {
    "logs_retrieved": true,
    "log_group": "",
    "log_stream": "",
    "error_signals": []
  },

  "diagnosis": {
    "category": "UNKNOWN_FAILURE",
    "subcategory": null,
    "root_cause_summary": null,
    "confidence": 0,
    "basis": []
  },

  "artifact_state": {
    "backend": "NOT_VERIFIED",
    "frontend": "NOT_VERIFIED",
    "s3_artifact": "NOT_VERIFIED"
  },

  "recovery": {
    "retryability": "UNKNOWN",
    "recommended_action": ""
  },

  "promotion": {
    "allowed": false,
    "deployment_allowed": false
  },

  "unknown_areas": [],

  "completion_status": "FAILURE_HANDLED"
}
```

---

# 65. CI Artifact Invalid Contract

CodeBuild can succeed while CI fails.

Example:

```json
{
  "ci_status": "CI_ARTIFACT_INVALID",

  "build": {
    "build_status": "SUCCEEDED"
  },

  "artifact_state": {
    "backend": "VERIFIED",
    "frontend": "MISSING",
    "s3_artifact": "VERIFIED"
  },

  "promotion": {
    "allowed": false
  }
}
```

This state must remain distinct from a CodeBuild `FAILED` result.

---

# 66. Success Handoff Traceability

The downstream agent should be able to answer:

```text
Which source revision produced this artifact?
Which CodeBuild execution produced it?
Which backend image corresponds to it?
Which frontend image corresponds to it?
Which S3 artifact corresponds to it?
How were those artifacts verified?
```

without guessing or re-discovering fundamental CI information.

This is why the CI Success Handoff must contain full immutable artifact identities.

---

# 67. Do Not Re-query Without Need

Once authoritative build and artifact information has been validated and included in the handoff, downstream agents SHOULD consume the validated handoff rather than independently rediscovering basic identifiers.

This reduces:

* inconsistent AWS observations;
* race conditions;
* accidental use of newer artifacts;
* duplicate API calls;
* LLM ambiguity.

---

# 68. Example Successful Build

Input:

```text
Build:
Salesloft:build-101

Resolved revision:
abc123def456
```

CodeBuildStatusTool:

```text
SUCCEEDED
```

Expected images:

```text
salesloft-backend:abc123def456
salesloft-frontend:abc123def456
```

Artifact validation:

```text
Backend image   VERIFIED
Frontend image  VERIFIED
S3 artifact     VERIFIED
Correlation     VERIFIED
```

Final result:

```text
CI_SUCCESS
promotion_allowed = true
FORWARD_TO_NEXT_AGENT
```

---

# 69. Example Compile Failure

CodeBuild:

```text
FAILED
```

Phase:

```text
BUILD
```

Observed log:

```text
TypeScript compiler error
```

Diagnosis:

```text
COMPILE_FAILURE
```

Result:

```text
promotion_allowed = false
retryability = NON_RETRYABLE
```

Recommended action:

```text
Correct the reported compilation failure and submit a new source revision.
```

---

# 70. Example Stale Image Protection

Current build:

```text
revision = def789abc123
```

ECR contains:

```text
salesloft-backend:abc123def456
```

but not:

```text
salesloft-backend:def789abc123
```

The agent MUST NOT accept the older image.

Result:

```text
backend artifact = MISSING
CI_ARTIFACT_INVALID
promotion_allowed = false
```

This is exactly why immutable source-revision tagging is mandatory.

---

# 71. Example Partial Artifact Build

CodeBuild:

```text
SUCCEEDED
```

Artifacts:

```text
Backend image   VERIFIED
Frontend image  VERIFIED
S3 artifact     MISSING
```

Result:

```text
CI_ARTIFACT_INVALID
```

NOT:

```text
CI_SUCCESS
```

Two out of three is not sufficient.

---

# 72. Example Unknown Verification

CodeBuild:

```text
SUCCEEDED
```

ECR:

```text
Backend VERIFIED
Frontend verification API timed out
```

S3:

```text
VERIFIED
```

Result:

```text
CI_STATUS_UNKNOWN
promotion_allowed = false
```

The agent MUST NOT assume the frontend image exists.

---

# 73. Example Tool Error

CodeBuildStatusTool:

```text
AccessDenied
```

Without authoritative build status:

```text
CI_TOOL_ERROR
promotion_allowed = false
```

Do not infer the build status from upstream text alone.

---

# 74. Anti-Hallucination Rules

The following rules are mandatory.

The agent MUST NOT:

1. invent build IDs;
2. invent commit SHAs;
3. invent image tags;
4. invent ECR repositories;
5. invent image digests;
6. invent S3 paths;
7. invent CodeBuild states;
8. invent failed phases;
9. invent CloudWatch logs;
10. invent root causes;
11. invent AWS error messages;
12. invent artifact existence;
13. assume `latest` belongs to the current build;
14. assume successful CodeBuild means artifacts exist;
15. assume failed build means production is affected;
16. assume a tool error means build failure;
17. assume missing evidence means success;
18. modify evidence returned by tools to fit an expected conclusion;
19. silently reconcile contradictory evidence;
20. forward an unverified build downstream.

---

# 75. Agent Reasoning Boundary

The agent is permitted to:

```text
classify
correlate
summarize
evaluate
decide according to policy
```

based on authoritative evidence.

It is NOT permitted to fabricate observations.

For example:

Tool evidence:

```text
"no basic auth credentials"
```

Agent may classify:

```text
ECR_AUTH_FAILURE
```

Tool returns no authentication-related evidence:

Agent must NOT invent an ECR authentication failure.

---

# 76. Recommended Action Rules

Recommendations must be proportional to evidence.

Good:

```text
Compilation failed at the reported TypeScript error.
Correct the compilation issue and submit a new source revision.
```

Bad:

```text
Rewrite the frontend authentication architecture.
```

unless evidence genuinely supports that recommendation.

The Failure Handler is not a speculative refactoring agent.

---

# 77. Source Modification Policy

The CI Failure Handler MUST NOT automatically modify source code.

It may identify:

* error;
* affected stage;
* affected file if evidenced;
* likely corrective category;
* retryability.

Actual source correction should belong to a separate remediation process or developer workflow unless future architecture explicitly adds automatic repair.

---

# 78. Git Rollback Policy

The agent MUST NOT automatically:

```text
git revert
git reset
force push
delete branch
rewrite history
```

in response to CI failure.

A failed commit should remain traceable.

The pipeline should block it from promotion rather than silently rewriting source history.

---

# 79. Artifact Mutation Policy

The agent MUST NOT fix CI by:

```text
retagging an old image with the new commit SHA
copying an old artifact into the new artifact location
changing artifact metadata to appear current
```

That would destroy build provenance.

A missing current artifact means the current build has not satisfied CI requirements.

---

# 80. Idempotency Principle

Repeated validation of the same unchanged build should produce materially equivalent conclusions.

For example:

```text
Build 101
Revision abc123def456
Backend digest sha256:X
Frontend digest sha256:Y
Artifact version Z
```

should not become associated with unrelated artifacts merely because a newer build has subsequently run.

Immutable identifiers are essential for this property.

---

# 81. Auditability Principle

Every final decision should be explainable using:

```text
Input
  ↓
Tool Observations
  ↓
Evidence
  ↓
Policy / KB Rule
  ↓
Decision
```

No decision should depend on hidden invented facts.

---

# 82. Final CI State Model

Allowed high-level outcomes:

```text
CI_SUCCESS
CI_FAILED
CI_ARTIFACT_INVALID
CI_IN_PROGRESS
CI_TIMEOUT
CI_STOPPED
CI_STATUS_UNKNOWN
CI_INPUT_INVALID
CI_TOOL_ERROR
```

Do not generate arbitrary final state names.

---

# 83. Downstream Routing Rules

```text
CI_SUCCESS
    ↓
FORWARD TO NEXT AGENT
```

All other final states:

```text
DO NOT FORWARD FOR DEPLOYMENT/PROMOTION
```

They may instead route to:

```text
Failure Reporting
Notification
Human Review
Future Remediation Agent
```

depending on the broader workflow.

---

# 84. Completion Criteria

The CI Build Validation & Failure Handling Agent has completed successfully only when it has produced one of two meaningful outcomes:

### Verified success

```text
CI state established
+
all required artifacts verified
+
artifact/source correlation verified
+
complete Success Handoff generated
```

or:

### Failure/uncertain state safely handled

```text
non-success state established
+
available evidence preserved
+
diagnosis performed where evidence permits
+
unknowns preserved
+
promotion blocked
+
Failure Evidence Blueprint generated
```

"Could not determine anything but allowed pipeline to continue" is never an acceptable outcome.

---

# 85. Core Policy Summary

The agent must always follow these principles:

```text
VERIFY, DON'T ASSUME.

CORRELATE ARTIFACTS TO THE EXACT BUILD.

SEPARATE EVIDENCE FROM INFERENCE.

PRESERVE UNKNOWN INFORMATION.

FAIL CLOSED.

NEVER PROMOTE PARTIAL ARTIFACTS.

NEVER TREAT CODEBUILD SUCCESS ALONE AS CI SUCCESS.

NEVER TREAT CI FAILURE AS PRODUCTION ROLLBACK.

NEVER MODIFY SOURCE OR ARTIFACT HISTORY TO HIDE FAILURE.

FORWARD COMPLETE BUILD DETAILS ONLY AFTER VERIFIED CI SUCCESS.
```

---