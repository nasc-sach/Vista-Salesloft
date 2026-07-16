# Knowledge Base 02
# Failure Analysis Methodology

---

# Purpose

This knowledge base defines the methodology for analyzing execution evidence and determining the most probable root cause of execution failures.

The Result Analysis Agent performs analytical reasoning.

It transforms observed execution evidence into structured technical understanding.

The objective is to explain failures using only observable evidence.

---

# Objective

Receive

Execution Evidence Blueprint

↓

Understand Execution

↓

Correlate Evidence

↓

Identify Failure

↓

Determine Probable Root Cause

↓

Assess Confidence

↓

Assess Business Impact

↓

Generate Execution Analysis Blueprint

---

# Philosophy

Execution records facts.

Analysis explains facts.

Every conclusion must originate from observed execution evidence.

Never speculate.

Never invent causes.

Never assume missing information.

---

# Analysis Lifecycle

Execution Evidence Blueprint

↓

Evidence Validation

↓

Evidence Correlation

↓

Failure Identification

↓

Failure Classification

↓

Root Cause Determination

↓

Confidence Assessment

↓

Impact Assessment

↓

Execution Analysis Blueprint

Never skip a stage.

---

# Evidence Validation

Before analysis verify

Execution Summary exists.

Scenario Results exist.

Scenario Phase Results exist.

Execution Timeline exists.

Navigation History exists.

Interaction History exists.

Console Summary exists.

JavaScript Exception Summary exists.

Network Summary exists.

Execution Metadata exists.

Automation Metadata exists.

If mandatory evidence is missing

Reduce confidence.

Do not fabricate observations.

---

# Evidence Correlation

Never analyze observations independently.

Correlate

Scenario Results

↓

Scenario Phase Results

↓

Execution Timeline

↓

Navigation History

↓

Interaction History

↓

Console Summary

↓

JavaScript Exceptions

↓

Network Summary

↓

Execution Metadata

↓

Automation Metadata

Evidence should support one another.

---

# Failure Identification

Determine

Which Scenario failed.

Which Phase failed.

When failure occurred.

What was being executed.

What observation first indicated failure.

Separate

Observed Failure

from

Underlying Cause.

---

# Symptom vs Root Cause

Always distinguish

Symptom

from

Root Cause.

Example

Symptom

Login failed.

Possible Root Cause

Authentication service unavailable.

Do not report symptoms as root causes.

---

# Root Cause Analysis

Determine the most probable cause using correlated evidence.

Possible categories

Application Logic

Frontend

Backend

API

Database

Authentication

Authorization

Validation

Navigation

Browser

Network

Configuration

Environment

Automation

Dependency

Unknown

Choose only the category best supported by evidence.

---

# Multi-Evidence Rule

A root cause should normally be supported by multiple observations.

Examples

HTTP 500

+

JavaScript Exception

+

Failed Verification

↓

Backend Failure

Examples

Timeout

+

Navigation Failure

+

No Network Errors

↓

Frontend Performance Issue

Single observations should reduce confidence.

---

# Contradictory Evidence

When evidence conflicts

Do not force a conclusion.

Return

Competing Hypotheses

Confidence

Supporting Evidence

Missing Evidence

Unknown Areas

---

# Confidence Assessment

Confidence depends upon

Evidence Completeness

Evidence Consistency

Evidence Quantity

Evidence Quality

Correlated Observations

Use

High

Medium

Low

Unknown

Never inflate confidence.

---

# Failure Pattern Recognition

Identify recurring patterns.

Examples

Authentication Failure

Navigation Failure

API Failure

Validation Failure

Permission Failure

Browser Crash

Timeout

Environment Failure

Configuration Issue

Automation Issue

Do not invent new categories.

---

# Impact Assessment

Assess

Affected Business Module

Affected Workflow

Affected Features

Affected User Journey

Execution Scope

Potential User Impact

Business Risk

Assessment should remain proportional.

---

# Unknown Handling

Unknown observations remain Unknown.

Unknown root causes remain Unknown.

Unknown impact remains Unknown.

Generate uncertainty explicitly.

Never fabricate conclusions.

---

# Traceability

Every conclusion should reference

Execution Observation

↓

Scenario

↓

Scenario Phase

↓

Evidence

↓

Failure Classification

↓

Root Cause

↓

Confidence

Nothing should exist without evidence.

---

# Validation

Before completion verify

Every failure supported by evidence.

Every root cause supported by observations.

Confidence assigned.

Business impact assigned.

Unknown Areas preserved.

No unsupported conclusions.

---

# Common Analysis Mistakes

Do not confuse symptoms with root causes.

Do not rely on one observation.

Do not ignore contradictory evidence.

Do not invent missing observations.

Do not recommend solutions.

Do not classify without evidence.

Do not remove Unknown Areas.

---

# Success Criteria

Every identified root cause should

Be evidence-driven.

Be traceable.

Be confidence-aware.

Be technically meaningful.

Be understandable by downstream agents.

---

# Final Principle

Observe first.

Correlate second.

Conclude third.

Confidence always follows evidence.

The strongest analysis is not the one with the most conclusions.

It is the one with the most defensible conclusions.