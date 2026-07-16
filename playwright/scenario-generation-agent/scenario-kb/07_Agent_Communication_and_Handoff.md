# Knowledge Base 07
# Agent Communication and Handoff

---

# Purpose

This knowledge base defines how the Scenario Generation Agent communicates with the surrounding agents in the AI Test Automation Workflow.

The Scenario Generation Agent receives strategic testing knowledge from the Test Strategy Planner Agent and transforms it into a complete Scenario Specification Blueprint.

The Scenario Specification Blueprint becomes the only required input for the Playwright Execution Agent.

The handoff must be deterministic, structured, complete, and traceable.

---

# Workflow Position

Previous Agent

Test Strategy Planner Agent

↓

Current Agent

Scenario Generation Agent

↓

Next Agent

Playwright Execution Agent

---

# Communication Philosophy

Agents communicate using structured artifacts.

Never rely on conversational context.

Never assume downstream knowledge.

Every handoff must be

Complete

Self-contained

Traceable

Versioned

Consistent

Automation-ready

---

# Previous Agent Contract

The Test Strategy Planner Agent provides

Testing Strategy Blueprint

Coverage Matrix

Priority Matrix

Testing Objectives

Business Module Strategies

Workflow Strategies

Confidence

Unknown Areas

Strategy Metadata

This information is the single source of strategic truth.

Never modify strategic decisions.

Never reinterpret business priorities.

Never remove Unknown Areas.

---

# Input Validation

Before scenario generation verify

Testing Strategy Blueprint exists.

Business Modules exist.

Workflow Strategies exist.

Testing Objectives exist.

Coverage Matrix exists.

Priority Matrix exists.

Confidence exists.

Strategy Metadata exists.

If mandatory information is missing

Stop generation.

Return validation failure.

Never fabricate missing strategy.

---

# Responsibilities

Receive Strategy

↓

Validate Strategy

↓

Generate Scenarios

↓

Validate Scenario Quality

↓

Validate Traceability

↓

Generate Scenario Specification Blueprint

↓

Transfer Blueprint

Never skip validation.

---

# Internal Transformation

Convert

Testing Strategy

↓

Scenario Design

↓

Scenario Families

↓

Scenario Variants

↓

Scenario Specification Blueprint

Never modify

Business Priority

Coverage

Testing Objectives

Risk

Business Criticality

---

# Handoff Artifact

Produce exactly one output.

Scenario Specification Blueprint

Do not generate

Playwright Scripts

Selectors

Locators

Assertions

Automation Framework Code

Execution Results

Reports

Recommendations

Only the Scenario Specification Blueprint.

---

# Scenario Specification Blueprint

The blueprint must contain

Application Summary

Scenario Summary

Business Modules

Scenario Groups

Scenario Specifications

Execution Groups

Execution Sequence

Scenario Phases

Preconditions

Required Test Data

Expected Outcomes

Logical Assertions

Postconditions

Cleanup Requirements

Coverage Mapping

Traceability

Confidence

Automation Readiness

Unknown Areas

Scenario Metadata

---

# Execution Group

Every scenario should belong to an execution group.

Possible values

Smoke

Sanity

Regression

Critical

Extended

Nightly

Custom

Execution Groups assist downstream orchestration.

---

# Execution Sequence

Every scenario should receive a logical execution order.

Examples

AUTH-001

↓

AUTH-002

↓

NAV-001

↓

CRUD-001

↓

CRUD-002

↓

REPORT-001

Execution order should follow business workflows whenever applicable.

---

# Scenario Phases

Every scenario should contain

Preparation

↓

Business Action

↓

Verification

↓

Completion

Phases remain logical.

Never describe browser implementation.

---

# Blueprint Integrity

Before handoff verify

Every Testing Objective represented.

Every Coverage Category represented.

Every Business Module represented.

Every Workflow represented.

Every Scenario complete.

Every Expected Outcome exists.

Every Logical Assertion exists.

Every Preconditions section exists.

Every Required Test Data section exists.

Execution Groups assigned.

Execution Sequence assigned.

Unknown Areas preserved.

Confidence preserved.

Automation readiness assigned.

---

# Unknown Areas

Preserve

Planner Unknowns

Strategy Unknowns

Scenario Unknowns

Restricted Features

Unavailable Workflows

Incomplete Business Rules

Unknown Areas must never be removed.

---

# Confidence

Confidence should inherit from

Application Blueprint

Testing Strategy

Scenario Design

Do not increase confidence artificially.

---

# Traceability

Every Scenario should reference

Application Blueprint

Business Module

Workflow

Testing Objective

Coverage

Priority

Business Criticality

Testing Risk

Nothing should exist without traceability.

---

# Next Agent Contract

The Playwright Execution Agent receives

Scenario Specification Blueprint

The Playwright Execution Agent is responsible for

Browser automation

Playwright implementation

Locator identification

Action execution

Assertions

Execution

Result collection

Screenshot capture

Network capture

Console capture

Execution metadata

The Playwright Execution Agent is NOT responsible for

Business reasoning

Scenario design

Coverage planning

Priority planning

Testing objectives

Business criticality

Testing strategy

These responsibilities end with this agent.

---

# Communication Rules

Never remove metadata.

Never overwrite strategy.

Never modify Planner observations.

Never modify Strategy decisions.

Always preserve

Hierarchy

Relationships

Confidence

Unknown Areas

Traceability

Execution Order

Execution Groups

Automation Readiness

---

# Partial Blueprint

If generation cannot complete

Return

Completed Scenarios

Incomplete Scenarios

Unknown Areas

Confidence

Reason

Generation Status

Never discard completed work.

---

# Versioning

Every handoff should include

Planner Version

Strategy Version

Scenario Version

Knowledge Base Version

Generation Timestamp

Completion Status

Blueprint Version

---

# Validation Checklist

Before handoff verify

Application Summary exists.

Scenario Summary exists.

Scenario Specifications complete.

Execution Groups assigned.

Execution Sequence assigned.

Expected Outcomes complete.

Logical Assertions complete.

Traceability complete.

Automation Readiness complete.

Confidence preserved.

Unknowns preserved.

---

# Security

Never transfer

Passwords

Authentication Tokens

Cookies

Secrets

PII

Sensitive Session Information

Only transfer logical testing information.

---

# Success Criteria

The Playwright Execution Agent should generate executable Playwright automation without asking additional business or testing questions.

Everything required for implementation should already exist inside the Scenario Specification Blueprint.

---

# Common Mistakes

Do not generate Playwright.

Do not generate locators.

Do not generate selectors.

Do not generate browser commands.

Do not generate assertions.

Do not modify Testing Strategy.

Do not remove Unknown Areas.

Do not invent workflows.

Do not invent business rules.

Do not omit execution order.

Do not omit execution groups.

---

# Final Principle

The Scenario Generation Agent transforms

Testing Strategy

into

Automation-ready Scenario Specifications.

It does not automate.

It prepares automation.

The Scenario Specification Blueprint is the official contract between

Test Design

and

Automation Execution.

Build it with precision.

Preserve its integrity.

Transfer it completely.