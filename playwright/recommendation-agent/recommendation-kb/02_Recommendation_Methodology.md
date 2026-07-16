# Knowledge Base 02
# Recommendation Methodology

---

# Purpose

This knowledge base defines the methodology for transforming an Execution Analysis Blueprint into actionable engineering recommendations.

The Recommendation Agent performs decision-making.

It does not perform execution analysis.

It does not determine Root Causes.

It transforms validated analysis into structured implementation guidance.

The objective is to recommend actions that improve application quality, reduce operational risk, and prevent recurrence.

---

# Objective

Receive

Execution Analysis Blueprint

↓

Understand Analysis

↓

Group Related Findings

↓

Determine Priorities

↓

Generate Recommendations

↓

Generate Implementation Roadmap

↓

Generate Recommendation Blueprint

---

# Philosophy

Analysis identifies problems.

Recommendations identify actions.

Every recommendation must originate from validated technical analysis.

Never recommend actions unsupported by evidence.

Never recommend speculative solutions.

---

# Recommendation Lifecycle

Execution Analysis Blueprint

↓

Analysis Validation

↓

Recommendation Planning

↓

Recommendation Prioritization

↓

Recommendation Grouping

↓

Implementation Roadmap

↓

Recommendation Blueprint

Never skip a stage.

---

# Analysis Understanding

Before generating recommendations understand

Analysis Summary

Failure Analysis

Root Cause Analysis

Failure Classification

Confidence Assessment

Business Impact

Technical Impact

Affected Components

Execution Scope

Recurring Pattern Analysis

Alternative Hypotheses

Evidence Quality

Unknown Areas

Never recommend before understanding the complete analysis.

---

# Recommendation Generation

Generate recommendations for

Resolved Root Causes

Recurring Failures

High Impact Issues

Critical Business Risks

Technical Improvements

Operational Improvements

Recommendations should remain practical.

---

# Recommendation Categories

Possible recommendation categories

Implementation Recommendation

Developer Action

Testing Recommendation

Regression Recommendation

Infrastructure Recommendation

Deployment Recommendation

Monitoring Recommendation

Configuration Recommendation

Security Recommendation

Documentation Recommendation

Preventive Recommendation

Operational Recommendation

Only generate categories supported by analysis.

---

# Recommendation Principles

Every recommendation should

Address the identified Root Cause.

Reduce future failures.

Improve application quality.

Improve maintainability.

Reduce operational risk.

Improve testing quality.

Improve system reliability.

Recommendations should be actionable.

---

# Recommendation Grouping

Group recommendations when multiple failures share the same Root Cause.

Examples

Authentication Failures

↓

Single Authentication Improvement Recommendation

Repeated API Failures

↓

Single API Reliability Recommendation

Repeated Validation Failures

↓

Single Validation Improvement Recommendation

Avoid duplicate recommendations.

---

# Recommendation Prioritization

Prioritize recommendations using

Business Impact

Technical Impact

Confidence

Operational Risk

Failure Scope

Recurring Pattern Frequency

Deployment Risk

Priority should always remain evidence-driven.

---

# Recommendation Types

Possible recommendation types include

Immediate Fix

Preventive Improvement

Architecture Improvement

Configuration Change

Automation Improvement

Infrastructure Improvement

Monitoring Enhancement

Documentation Improvement

Testing Improvement

Operational Improvement

Only recommend actions supported by analysis.

---

# Developer Actions

Generate clear engineering actions.

Examples

Review authentication workflow.

Investigate API timeout.

Optimize database queries.

Improve validation logic.

Review retry mechanism.

Improve session management.

Actions should describe

What needs attention,

not implementation details.

---

# Testing Recommendations

Generate testing improvements.

Examples

Add regression coverage.

Expand negative testing.

Improve boundary testing.

Increase API integration coverage.

Add resilience testing.

Improve authentication scenarios.

Testing recommendations should strengthen quality assurance.

---

# Preventive Recommendations

Recommend actions that reduce recurrence.

Examples

Improve monitoring.

Improve logging.

Increase automated regression coverage.

Improve health checks.

Improve deployment validation.

Improve dependency monitoring.

Preventive recommendations should reduce future failures.

---

# Deployment Recommendations

Recommend deployment improvements when supported.

Examples

Validate environment configuration.

Perform staged rollout.

Verify service availability.

Validate dependency readiness.

Confirm migration completion.

Only recommend deployment activities supported by analysis.

---

# Monitoring Recommendations

Recommend monitoring improvements.

Examples

API monitoring.

Authentication monitoring.

Database performance monitoring.

Infrastructure monitoring.

Application health monitoring.

Alert improvements.

Recommendations should improve observability.

---

# Implementation Roadmap

Organize recommendations into

Immediate Actions

↓

Short-Term Improvements

↓

Long-Term Improvements

↓

Validation Activities

↓

Monitoring Improvements

↓

Preventive Improvements

The roadmap should provide logical implementation order.

---

# Unknown Handling

Unknown analysis remains Unknown.

If confidence is Low or Unknown

Prefer

Further Investigation

over speculative recommendations.

Never fabricate solutions.

---

# Traceability

Every recommendation shall reference

Execution Analysis Blueprint

↓

Failure Analysis

↓

Root Cause

↓

Confidence

↓

Business Impact

↓

Supporting Evidence

Recommendations without traceability should not exist.

---

# Validation

Before completion verify

Every recommendation supported by Root Cause.

Every recommendation supported by evidence.

Priority assigned.

Recommendation category assigned.

Implementation roadmap complete.

Unknown Areas preserved.

No duplicate recommendations.

No unsupported recommendations.

---

# Common Mistakes

Do not recommend fixes unsupported by analysis.

Do not duplicate recommendations.

Do not exaggerate priority.

Do not ignore confidence.

Do not ignore business impact.

Do not remove uncertainty.

Do not recommend implementation details.

Do not assign people or teams.

---

# Success Criteria

Every recommendation should

Be actionable.

Be technically meaningful.

Be evidence-driven.

Be traceable.

Be prioritized.

Be grouped logically.

Support engineering decision-making.

---

# Final Principle

Recommendations should transform

Evidence

into

Action.

Every recommendation should answer

What should be done,

Why it should be done,

and

Why it matters,

while remaining grounded in validated technical analysis.