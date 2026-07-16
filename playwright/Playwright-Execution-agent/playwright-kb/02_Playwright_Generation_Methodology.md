# Knowledge Base 02
# Playwright Generation Methodology

---

# Purpose

This knowledge base defines the methodology for transforming a validated Scenario Specification Blueprint into executable Playwright automation.

The Playwright Execution Agent is responsible for implementation only.

Business reasoning, testing strategy, priorities, coverage, and scenario design have already been completed by previous agents.

The objective is to faithfully implement the Scenario Specification Blueprint while producing maintainable, deterministic, reusable Playwright automation.

---

# Objective

Receive

Scenario Specification Blueprint

↓

Understand Scenario

↓

Generate Playwright Components

↓

Generate Automation

↓

Execute Automation

↓

Collect Evidence

↓

Generate Execution Evidence Blueprint

---

# Philosophy

Automation is implementation.

Automation is not business reasoning.

Automation should never redesign scenarios.

Automation should never change business behaviour.

Automation should faithfully execute what the Scenario Specification Blueprint defines.

---

# Primary Input

Receive

Scenario Specification Blueprint

Scenario Metadata

Scenario Phases

Automation Hints

Execution Profile

Execution Sequence

Confidence

Unknown Areas

Never modify the Scenario Specification Blueprint.

Never reinterpret Scenario intent.

---

# Generation Lifecycle

Scenario Specification Blueprint

↓

Scenario

↓

Scenario Phases

↓

Playwright Actions

↓

Logical Assertions

↓

Execution

↓

Evidence Collection

↓

Execution Evidence Blueprint

---

# Implementation Principles

Every Scenario should become one executable Playwright test.

Every Scenario Phase should become one logical execution block.

Every Verification Objective should become one or more Playwright assertions.

Implementation should remain deterministic.

---

# Scenario Translation

Translate

Preparation Phase

↓

Environment Preparation

Authentication

Required Navigation

Required Preconditions

---

Translate

Navigation Phase

↓

Logical Navigation

Route Changes

Menu Navigation

Workflow Navigation

Never redesign navigation.

---

Translate

Business Action Phase

↓

Business Operations

Form Submission

CRUD Actions

Search

Filtering

Sorting

Workflow Progression

Implement only what the Scenario specifies.

---

Translate

Verification Phase

↓

Assertions

Validation

Business State Verification

Navigation Verification

Workflow Completion

Data Verification

Assertions should directly correspond to Verification Objectives.

---

Translate

Cleanup Phase

↓

Restore State

Delete Temporary Data

Logout

Reset Environment

Cleanup should preserve execution independence.

---

# Playwright Structure

Automation should be organized using reusable components.

Preferred organization

Configuration

↓

Fixtures

↓

Page Objects

↓

Utilities

↓

Tests

↓

Reports

Business logic should remain inside tests.

Reusable browser interactions should remain inside Page Objects.

---

# Page Object Principle

Page Objects should contain

Navigation

Element Interactions

Reusable Operations

Utility Functions

Page Objects should never contain

Business Decisions

Testing Strategy

Scenario Logic

---

# Locator Strategy

Use stable locators whenever possible.

Preferred order

Accessibility Locators

Data Test Identifiers

Role Based Locators

Visible Text

CSS Selectors

XPath only as a last resort.

Avoid fragile locators.

Avoid positional selectors.

---

# Synchronization Strategy

Prefer deterministic synchronization.

Use

Element Visibility

Element State

Network Completion

Navigation Completion

Application Stability

Avoid unnecessary fixed waits.

Avoid arbitrary delays.

Synchronization should reflect application readiness.

---

# Assertion Strategy

Generate assertions only from

Verification Objectives

Expected Outcomes

Logical Assertions

Never invent additional assertions.

Every assertion should validate business behaviour.

---

# Error Handling

Handle

Navigation Failure

Element Not Found

Timeout

Assertion Failure

Network Failure

Unexpected Dialog

Unexpected Page

Session Expiration

Execution should fail gracefully.

Execution should continue when allowed by execution policy.

---

# Retry Strategy

Retry only when

Scenario Configuration allows retries.

Retry should not hide legitimate failures.

Retries should be reported.

Retry counts should be included in execution evidence.

---

# Test Independence

Every test should execute independently.

Avoid shared execution state.

Avoid dependency on previous tests.

Restore state whenever practical.

---

# Execution Order

Execute according to

Execution Profile

↓

Execution Sequence

Never randomly reorder execution.

Respect business dependencies.

---

# Automation Hints

Use Automation Hints only to improve implementation.

Examples

Reusable Authentication

Dynamic Test Data

Reusable Navigation

Modal Handling

File Upload

Download Verification

Session Recovery

Automation Hints should never modify Scenario intent.

---

# Unknown Areas

Unknown Scenario information remains Unknown.

Execution should report

Unable to Execute

Unable to Verify

Environment Limitation

Restricted Access

Never fabricate observations.

---

# Confidence

Confidence is inherited.

Execution never changes confidence.

Execution only reports observations.

---

# Validation

Before execution verify

Scenario complete.

Scenario Phases exist.

Preconditions exist.

Required Test Data exists.

Execution Profile assigned.

Execution Sequence assigned.

Automation Hints available.

Unknown Areas preserved.

---

# Common Mistakes

Do not redesign scenarios.

Do not change business workflows.

Do not introduce additional business rules.

Do not generate unnecessary assertions.

Do not ignore Execution Sequence.

Do not ignore Execution Profile.

Do not remove Unknown Areas.

Do not hardcode unstable waits.

Do not use fragile locators.

Do not duplicate reusable logic.

---

# Success Criteria

Every Scenario should become

One executable Playwright test.

Every Scenario Phase should become

One logical execution block.

Every Verification Objective should become

One or more Playwright assertions.

Execution should be deterministic.

Evidence should be complete.

---

# Final Principle

The Playwright Execution Agent is an implementation engine.

It faithfully transforms Scenario Specifications into reliable automation.

It never redesigns.

It never reinterprets.

It simply implements, executes, observes, and reports.