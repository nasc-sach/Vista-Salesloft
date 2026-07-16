# Knowledge Base 03
# Test Design Strategies

---

# Purpose

This knowledge base defines the scenario design strategies used by the Scenario Generation Agent.

It teaches the agent how to transform testing objectives into comprehensive logical scenarios.

The purpose is to maximize testing confidence while minimizing unnecessary scenario duplication.

The output should always be technology-independent and automation-ready.

---

# Philosophy

A scenario should never exist without purpose.

Every scenario should validate one or more testing objectives.

Every scenario should establish confidence.

Every scenario should contribute measurable testing value.

Avoid redundant scenarios.

Prefer quality over quantity.

---

# Scenario Design Lifecycle

Testing Objective

↓

Business Context

↓

Identify Applicable Design Strategies

↓

Generate Scenario Families

↓

Generate Scenario Variants

↓

Validate Coverage

↓

Produce Scenario Specification

---

# Strategy Selection

Not every design strategy applies to every feature.

Select only strategies that are relevant.

The chosen strategy should reflect

Business Context

Testing Objective

Workflow Complexity

Risk

Coverage Requirements

---

# Positive Testing

Purpose

Verify expected behaviour using valid conditions.

Generate scenarios where

Valid inputs are provided.

Business rules are satisfied.

Authorized users perform expected actions.

Normal workflows complete successfully.

Positive scenarios establish baseline confidence.

---

# Negative Testing

Purpose

Verify application behaviour under invalid conditions.

Generate scenarios using

Invalid input

Missing input

Unexpected values

Unauthorized access

Invalid workflow order

Restricted operations

Network interruptions

Application errors

Negative scenarios verify resilience.

---

# Boundary Value Analysis

Purpose

Verify behaviour around minimum and maximum acceptable values.

Examples

Minimum length

Maximum length

Minimum quantity

Maximum quantity

Zero

One

Empty values

Large values

Boundary scenarios should focus on limit behaviour.

---

# Equivalence Partitioning

Purpose

Reduce unnecessary scenarios while maintaining confidence.

Group inputs into

Valid partitions

Invalid partitions

Representative values

Generate scenarios only for representative values unless additional coverage is required.

---

# State Transition Testing

Purpose

Verify behaviour as the application changes state.

Examples

Logged Out

↓

Logging In

↓

Authenticated

↓

Session Expired

↓

Logged Out

Generate scenarios for

Valid transitions

Invalid transitions

Unexpected transitions

Recovery transitions

---

# Decision Table Testing

Purpose

Verify combinations of business rules.

Generate scenarios where outcomes depend upon multiple conditions.

Examples

User Role

+

Approval Status

+

Payment Status

↓

Expected Result

Use decision-based scenarios when business rules interact.

---

# Workflow Testing

Purpose

Verify complete business processes.

Generate scenarios covering

Workflow Start

Intermediate Steps

Decision Points

Alternative Paths

Workflow Completion

Workflow Cancellation

Workflow Recovery

Workflow testing validates business objectives.

---

# CRUD Testing

Generate scenarios for

Create

Read

Update

Delete

Archive

Restore

Import

Export

Permissions

Relationships

Validation

Concurrency (if applicable)

Not every CRUD operation requires identical depth.

---

# Permission Testing

Generate scenarios for

Authorized User

Unauthorized User

Read Only User

Administrator

Manager

Guest

Restricted Roles

Role Changes

Permission scenarios verify access control.

---

# Authentication Testing

Generate scenarios for

Valid Login

Invalid Login

Logout

Session Timeout

Session Recovery

Concurrent Sessions

Protected Resources

Expired Session

Password Recovery (if applicable)

MFA (if applicable)

Authentication scenarios should remain implementation-independent.

---

# Navigation Testing

Generate scenarios for

Valid Navigation

Invalid Navigation

Restricted Navigation

Breadcrumbs

Menus

Tabs

Dialogs

Drawers

Redirects

Deep Links

Navigation should preserve business flow.

---

# Validation Testing

Generate scenarios for

Required Fields

Optional Fields

Conditional Fields

Invalid Formats

Duplicate Data

Business Validation

Field Dependencies

Dynamic Validation

Validation scenarios should verify business correctness.

---

# Search and Filter Testing

Generate scenarios for

Valid Search

Empty Search

No Results

Special Characters

Combined Filters

Sorting

Pagination

Reset Filters

Search performance is not evaluated here.

---

# Integration Testing

Generate logical scenarios for

API-dependent features

External services

Notifications

Imports

Exports

Background processing

Synchronization

Only verify expected business behaviour.

---

# Recovery Testing

Generate scenarios for

Interrupted Workflow

Application Refresh

Session Recovery

Retry

Cancellation

Rollback

Recovery scenarios validate resilience.

---

# Scenario Optimization

Avoid generating duplicate scenarios.

Merge scenarios where

Testing Objectives

Coverage

Expected Outcomes

Business Value

are identical.

One scenario may validate multiple objectives.

---

# Scenario Independence

Every scenario should

Be independently executable.

Avoid dependency on previous scenarios.

Have clear preconditions.

Produce predictable outcomes.

---

# Expected Outcomes

Every scenario must define

Expected Business Behaviour

Expected Application Behaviour

Expected Navigation

Expected Validation

Expected Data State

Expected User Outcome

Expected Permission Behaviour

Never describe technical implementation.

---

# Scenario Completeness

Every generated scenario should include

Scenario Identifier

Scenario Name

Business Module

Workflow

Testing Objective

Scenario Category

Priority

Preconditions

Required Test Data

Execution Flow

Expected Outcomes

Logical Assertions

Coverage Mapping

Traceability

Confidence

Automation Readiness

---

# Strategy Selection Guidelines

Simple informational page

↓

Positive

Navigation

Permission

Business Form

↓

Positive

Negative

Boundary

Validation

CRUD

Workflow

Authentication Module

↓

Positive

Negative

Session

Permission

Recovery

Reporting Module

↓

Positive

Filtering

Sorting

Export

Permission

Large Workflow

↓

Workflow

Decision Table

Recovery

Integration

Permission

Choose only applicable strategies.

---

# Validation

Before completing scenario generation verify

Every Testing Objective has scenarios.

Every High Priority capability has comprehensive coverage.

Every Business Workflow has at least one positive scenario.

Every Validation Rule has negative coverage.

Boundary scenarios exist where limits are defined.

Permission scenarios exist where authorization applies.

Duplicate scenarios eliminated.

Unknowns preserved.

---

# Common Mistakes

Do not generate Playwright.

Do not generate locators.

Do not generate selectors.

Do not generate executable automation.

Do not generate browser interactions.

Do not overuse Boundary Value Analysis.

Do not apply every strategy to every feature.

Do not duplicate scenarios.

Do not invent business rules.

Do not remove Unknown Areas.

---

# Success Criteria

Every generated scenario should be

Business-focused

Logically complete

Automation-ready

Technology-independent

Traceable

Independent

Comprehensive

---

# Final Principle

Good scenarios are not created by applying every testing technique.

Good scenarios are created by selecting the right design strategy for the right business objective.

Always maximize confidence while minimizing unnecessary complexity.