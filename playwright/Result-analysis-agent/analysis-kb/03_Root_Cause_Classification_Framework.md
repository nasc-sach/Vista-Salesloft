# Knowledge Base 03
# Root Cause Classification Framework

---

# Purpose

This knowledge base defines the standard framework used by the Result Analysis Agent to classify execution failures and determine probable root causes.

The objective is to ensure that similar failures always receive consistent classifications, confidence assessments, and evidence mappings.

Classification must remain deterministic, evidence-driven, and traceable.

---

# Philosophy

Classification is not diagnosis.

Classification organizes failures into standardized categories based on available evidence.

Root Cause represents the most probable technical explanation supported by evidence.

If evidence is insufficient, classify the failure as Unknown rather than making unsupported assumptions.

---

# Classification Lifecycle

Execution Evidence

↓

Failure Detection

↓

Evidence Correlation

↓

Failure Category

↓

Root Cause

↓

Confidence

↓

Impact

↓

Execution Analysis Blueprint

---

# Classification Principles

Every execution failure should receive

Failure Category

↓

Failure Subcategory

↓

Probable Root Cause

↓

Supporting Evidence

↓

Confidence

↓

Business Impact

↓

Affected Components

↓

Unknown Areas

Never omit classification.

---

# Primary Failure Categories

Classify failures into one of the following categories.

Application Failure

Automation Failure

Environment Failure

Configuration Failure

Infrastructure Failure

Network Failure

Authentication Failure

Authorization Failure

Validation Failure

Navigation Failure

Browser Failure

Performance Failure

Dependency Failure

Security Failure

Unknown Failure

Only assign one primary category.

---

# Application Failure

Typical observations

Business logic executed incorrectly.

Unexpected application behaviour.

Incorrect calculations.

Unexpected workflow behaviour.

Unexpected application state.

Common evidence

Scenario verification failed.

Business rules violated.

Application response inconsistent.

---

# Automation Failure

Typical observations

Element not found.

Locator failure.

Synchronization issue.

Automation timeout.

Incorrect automation interaction.

Common evidence

Browser interaction failure.

No corresponding application error.

Automation exception.

---

# Environment Failure

Typical observations

Application unavailable.

Environment unstable.

Required services unavailable.

Infrastructure inaccessible.

Common evidence

Application not reachable.

Unexpected downtime.

Missing environment resources.

---

# Configuration Failure

Typical observations

Feature disabled.

Incorrect configuration.

Incorrect environment settings.

Unsupported execution configuration.

Common evidence

Configuration mismatch.

Feature unavailable.

Configuration-dependent failures.

---

# Infrastructure Failure

Typical observations

Service unavailable.

Container unavailable.

Database unavailable.

Infrastructure timeout.

Common evidence

503 responses.

Service interruptions.

Infrastructure logs.

---

# Network Failure

Typical observations

HTTP failures.

Timeouts.

Connection refused.

DNS resolution failure.

Network interruptions.

Common evidence

Failed requests.

Timeouts.

HTTP error codes.

Connection errors.

---

# Authentication Failure

Typical observations

Login unsuccessful.

Session expired.

Authentication rejected.

Invalid credentials.

Common evidence

401 responses.

Authentication redirects.

Login verification failed.

---

# Authorization Failure

Typical observations

Permission denied.

Restricted access.

Unauthorized workflow.

Role restriction.

Common evidence

403 responses.

Permission validation failed.

Access denied.

---

# Validation Failure

Typical observations

Input validation failed.

Required field missing.

Business validation failed.

Data rejected.

Common evidence

Validation messages.

Rejected submission.

Expected validation behaviour.

---

# Navigation Failure

Typical observations

Incorrect page.

Navigation interrupted.

Unexpected redirect.

Missing destination.

Common evidence

Navigation history.

Unexpected routes.

Workflow interruption.

---

# Browser Failure

Typical observations

Browser crash.

Unexpected browser closure.

Rendering failure.

JavaScript execution failure.

Common evidence

Browser events.

Console errors.

Unhandled exceptions.

---

# Performance Failure

Typical observations

Slow execution.

Timeout.

Long response time.

Performance degradation.

Common evidence

Execution timing.

Network timing.

Response timing.

Timeout events.

---

# Dependency Failure

Typical observations

Third-party service unavailable.

API dependency unavailable.

External authentication unavailable.

File storage unavailable.

Common evidence

Failed dependency requests.

Unavailable integrations.

Service interruptions.

---

# Security Failure

Typical observations

Security policy violation.

Certificate issue.

Mixed content.

Blocked request.

CORS failure.

Common evidence

Browser security messages.

Network observations.

Console errors.

---

# Unknown Failure

Assign when

Evidence is insufficient.

Evidence is contradictory.

Failure cannot be confidently classified.

Never invent categories.

---

# Supporting Evidence

Every classification should reference

Scenario

Scenario Phase

Observed Behaviour

Console Summary

JavaScript Summary

Network Summary

Navigation History

Interaction History

Execution Metadata

Supporting evidence is mandatory.

---

# Confidence Levels

Assign

High

Evidence strongly supports one conclusion.

Medium

Evidence supports one likely conclusion but alternatives exist.

Low

Evidence is weak or incomplete.

Unknown

Evidence insufficient for classification.

Never inflate confidence.

---

# Business Impact

Assess

Affected Module

Affected Workflow

Affected Feature

Affected User Journey

Execution Scope

Potential User Impact

Business Risk

Assessment should remain proportional.

---

# Affected Components

Identify the technical components involved.

Possible components

Frontend

Backend

API

Database

Authentication Service

Authorization Service

Network

Browser

Configuration

Infrastructure

Third-party Integration

Multiple components may be identified.

Only include components supported by evidence.

---

# Contradictory Evidence

If observations conflict

Return

Primary Hypothesis

Alternative Hypothesis

Supporting Evidence

Missing Evidence

Confidence

Do not force a single conclusion.

---

# Unknown Areas

Preserve

Execution Unknowns

Environment Unknowns

Automation Unknowns

Analysis Unknowns

Unknown Root Cause

Unknown Impact

Never fabricate certainty.

---

# Traceability

Every classification shall reference

Execution Evidence Blueprint

↓

Scenario

↓

Scenario Phase

↓

Execution Observation

↓

Failure Category

↓

Root Cause

↓

Confidence

↓

Impact

Nothing shall exist without traceability.

---

# Validation

Before completion verify

Failure classified.

Root Cause identified.

Evidence linked.

Confidence assigned.

Impact assigned.

Affected Components identified.

Unknown Areas preserved.

No unsupported conclusions.

---

# Common Mistakes

Do not classify based on one observation.

Do not confuse symptoms with root causes.

Do not invent technical causes.

Do not ignore contradictory evidence.

Do not recommend fixes.

Do not remove Unknown Areas.

---

# Success Criteria

A developer reading the Execution Analysis Blueprint should immediately understand

What failed.

Why it probably failed.

What evidence supports that conclusion.

How confident the conclusion is.

Which parts of the system were affected.

without requiring access to the original execution logs.

---

# Final Principle

Classification should reduce ambiguity.

Root Cause should explain evidence.

Confidence should reflect certainty.

Impact should reflect business importance.

Every conclusion should remain factual, traceable, and evidence-driven.