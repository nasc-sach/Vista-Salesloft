# Knowledge Base 02
# Scenario Generation Methodology

---

# Purpose

This knowledge base defines the methodology used by the Scenario Generation Agent to transform a Testing Strategy Blueprint into a comprehensive Scenario Specification Blueprint.

The objective is to systematically generate complete, traceable, automation-ready scenario specifications.

Scenario generation should always preserve business intent, testing objectives, coverage requirements, and priorities defined by the Test Strategy Planner Agent.

---

# Objective

Receive

Testing Strategy Blueprint

↓

Understand Business Context

↓

Understand Testing Objectives

↓

Understand Coverage

↓

Generate Scenario Families

↓

Generate Scenario Variants

↓

Define Preconditions

↓

Define Test Data Requirements

↓

Define Expected Outcomes

↓

Define Logical Assertions

↓

Generate Scenario Specification Blueprint

---

# Philosophy

A testing strategy defines

"What should be tested."

A scenario specification defines

"How that functionality should logically be verified."

Automation is not part of this process.

Scenario generation should remain implementation independent.

---

# Primary Input

Receive

Testing Strategy Blueprint

Coverage Matrix

Priority Matrix

Testing Objectives

Business Module Strategies

Workflow Strategies

Unknown Areas

Confidence

Strategy Metadata

Never modify the Testing Strategy Blueprint.

Never reinterpret strategic decisions.

---

# Generation Lifecycle

Testing Strategy Blueprint

↓

Business Module

↓

Workflow

↓

Testing Objective

↓

Coverage Requirement

↓

Scenario Family

↓

Scenario Variants

↓

Expected Outcomes

↓

Logical Assertions

↓

Scenario Specification Blueprint

---

# Business Understanding

Before generating any scenario understand

Business Purpose

Workflow Purpose

Business Goal

Primary User

Business Importance

Priority

Risk

Coverage

Never generate scenarios without understanding business context.

---

# Scenario Families

Every testing objective should generate one or more scenario families.

Possible families include

Positive

Negative

Boundary

Permission

Validation

Workflow

CRUD

Navigation

Authentication

Authorization

Search

Filtering

Sorting

Pagination

Integration

Recovery

Configuration

Notification

Reporting

Session

Import

Export

Generate only applicable families.

---

# Scenario Variants

Every scenario family should generate appropriate variants.

Examples

Positive

Valid Input

Valid Workflow

Successful Completion

Negative

Invalid Input

Missing Input

Unauthorized Access

Unexpected State

Boundary

Minimum Values

Maximum Values

Empty Values

Large Values

Special Characters

Permission

Authorized User

Unauthorized User

Restricted Role

Read Only User

Variants should maximize confidence while avoiding duplication.

---

# Preconditions

Every scenario should define

Application State

Authentication State

User Role

Permissions

Navigation State

Required Configuration

Feature Flags

Dependent Modules

Required Test Data

Environment Conditions

Preconditions should remove ambiguity.

---

# Test Data Requirements

Every scenario should specify

Required Data

Optional Data

Boundary Data

Invalid Data

Relationship Data

Permission Data

Configuration Data

Sensitive Data Requirements

Do not generate production values.

Only describe data requirements.

---

# Expected Outcomes

Every scenario should define

Expected Application Behaviour

Expected Business Behaviour

Expected User Outcome

Expected Navigation

Expected Data State

Expected Permission Behaviour

Expected Validation Behaviour

Expected Error Behaviour

Expected Recovery Behaviour

Expected outcomes should be observable.

Never describe implementation.

---

# Logical Assertions

Every scenario should define

What must be verified.

Examples

User successfully authenticated.

Employee created successfully.

Permission denied correctly.

Validation message displayed.

Session expired.

Navigation completed.

Workflow completed.

Assertions describe logical verification.

Never generate automation assertions.

---

# Scenario Independence

Every scenario should

Validate one primary objective.

Be independently executable.

Avoid dependency on previous scenarios.

Minimize shared state.

Reduce cascading failures.

---

# Scenario Granularity

Generate scenarios at

Business Module Level

↓

Workflow Level

↓

Testing Objective Level

↓

Scenario Family

↓

Scenario Variant

↓

Scenario Specification

Never generate automation steps.

---

# Traceability

Every scenario must reference

Business Module

Workflow

Testing Objective

Coverage Category

Coverage Depth

Priority

Business Criticality

Testing Risk

Application Blueprint Reference

Testing Strategy Reference

Nothing should exist without traceability.

---

# Unknown Areas

Preserve

Planner Unknowns

Strategy Unknowns

Restricted Features

Unavailable Workflows

Permission Unknowns

Generate recommendations for validation.

Never invent missing functionality.

---

# Confidence

Scenario confidence inherits from

Application Blueprint

Testing Strategy

Coverage

Priority

Unknown Areas

Never artificially increase confidence.

---

# Validation

Before completion verify

Every Testing Objective has scenarios.

Every Workflow has scenarios.

Every High Priority feature has sufficient scenarios.

Every Coverage Category is represented.

Unknowns preserved.

No duplicate scenarios.

No conflicting scenarios.

---

# Output

Generate one

Scenario Specification Blueprint

Containing

Scenario Hierarchy

Scenario Families

Scenario Variants

Preconditions

Test Data Requirements

Expected Outcomes

Logical Assertions

Scenario Metadata

Traceability

Confidence

Unknown Areas

Automation Readiness

---

# Common Mistakes

Do not generate Playwright.

Do not generate Selenium.

Do not generate Cypress.

Do not generate executable scripts.

Do not generate locators.

Do not generate CSS selectors.

Do not generate XPath.

Do not generate browser commands.

Do not duplicate scenarios.

Do not invent business rules.

Do not remove Unknown values.

---

# Success Criteria

The Playwright Execution Agent should generate executable automation using only the Scenario Specification Blueprint.

No strategic reasoning should remain.

No scenario design decisions should remain.

Only automation implementation should remain.

---

# Final Principle

Think like a Test Designer.

Not an Automation Engineer.

Describe

what should be verified,

under what conditions,

with what expectations,

and why.

Leave implementation to the next agent.