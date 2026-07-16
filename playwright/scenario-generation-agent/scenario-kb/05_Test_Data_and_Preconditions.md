# Knowledge Base 05
# Test Data and Preconditions

---

# Purpose

This knowledge base teaches the Scenario Generation Agent how to define complete execution prerequisites for every generated scenario.

Every scenario should contain sufficient contextual information so that the Playwright Execution Agent can execute it without making assumptions.

The objective is to eliminate ambiguity while keeping scenario specifications implementation-independent.

---

# Philosophy

A scenario should never begin with uncertainty.

Every scenario should clearly define

What state the application must be in.

What data must already exist.

What permissions are required.

What dependencies exist.

What environment assumptions exist.

The Playwright Execution Agent should never infer missing information.

---

# Objective

Scenario

↓

Preconditions

↓

Required Test Data

↓

Dependencies

↓

Environment Requirements

↓

Scenario Specification

---

# Preconditions

Every scenario should define its starting state.

Possible preconditions include

User Authentication

User Role

Permissions

Feature Flags

Navigation State

Workflow State

Application State

Existing Business Data

System Configuration

Dependent Modules

Third-party Availability

Required Browser State

Required Device State

Required Locale

Required Time Zone

Only include applicable preconditions.

---

# Authentication Preconditions

Determine whether the scenario requires

Anonymous User

Authenticated User

Administrator

Manager

Read Only User

Restricted User

Custom Role

Session Recovery

Expired Session

Concurrent Session

Never assume authentication.

---

# Permission Preconditions

Specify

Required Permission

Restricted Permission

Hidden Features

Disabled Features

Read Only Behaviour

Role Dependencies

Permission assumptions should always be explicit.

---

# Navigation Preconditions

Specify

Required Landing Page

Required Module

Required Workflow Step

Required Dialog

Required Tab

Required Drawer

Required URL State

Navigation assumptions should never be implicit.

---

# Data Preconditions

Determine whether existing data is required.

Examples

Existing Employee

Existing Customer

Existing Project

Existing Order

Existing Report

Existing Notification

Existing Configuration

Reference Data

Dependent Records

Data relationships

Only specify logical requirements.

---

# Environment Preconditions

Specify when applicable

Application Environment

Configuration

Language

Locale

Timezone

Network Availability

Third-party Availability

Feature Toggles

Environment assumptions should remain technology-independent.

---

# Test Data Philosophy

Test data exists to satisfy business objectives.

Test data should never be generated randomly.

Every required value should have business purpose.

---

# Test Data Categories

Possible categories

Valid Data

Invalid Data

Boundary Data

Empty Data

Duplicate Data

Relationship Data

Permission Data

Configuration Data

Special Character Data

Large Data

Minimal Data

Maximum Data

Localized Data

Generate only applicable categories.

---

# Valid Data

Used to verify expected behaviour.

Examples

Existing Employee

Valid Email

Valid Phone Number

Valid Customer

Valid Project

Valid Role

Valid Date

Valid Status

---

# Invalid Data

Used to verify validation behaviour.

Examples

Invalid Email

Invalid Phone

Unsupported Characters

Invalid Identifier

Unknown User

Incorrect Format

Unauthorized Values

---

# Boundary Data

Generate logical requirements for

Minimum Length

Maximum Length

Minimum Quantity

Maximum Quantity

Zero

One

Empty

Large Input

Boundary requirements remain logical.

Never generate implementation values.

---

# Relationship Data

Some scenarios require connected business entities.

Examples

Employee belongs to Department.

Project belongs to Customer.

Invoice belongs to Order.

Task belongs to Project.

Relationships should be described logically.

---

# Sensitive Data

Determine whether scenarios involve

Personal Information

Financial Information

Healthcare Information

Confidential Information

Internal Information

Security Information

Never expose real sensitive data.

Only identify logical requirements.

---

# Dynamic Data

Some scenarios require runtime data.

Examples

Current Date

Generated Identifier

Temporary Session

Generated Transaction

Unique Email

Current Timestamp

Describe the requirement.

Do not generate the value.

---

# Data Independence

Scenarios should minimize shared data.

Avoid scenarios that require another scenario to create data.

Whenever possible

each scenario should define its own required state.

---

# Data Cleanup

When a scenario changes business data

identify whether cleanup is required.

Possible cleanup

Delete Temporary Data

Restore Original State

Logout

Reset Configuration

Cleanup requirements should be documented.

---

# Scenario Readiness

A scenario is considered ready when

All Preconditions exist.

Required Test Data defined.

Dependencies identified.

Unknown Areas documented.

Confidence assigned.

No hidden assumptions remain.

---

# Traceability

Every precondition should reference

Business Module

Workflow

Testing Objective

Scenario

Coverage

Priority

Nothing should exist without traceability.

---

# Unknown Areas

Unknown preconditions remain Unknown.

Unknown data requirements remain Unknown.

Do not fabricate values.

Generate recommendations instead.

---

# Confidence

Confidence inherits from

Planner

Testing Strategy

Scenario Design

Do not increase confidence artificially.

---

# Validation

Before completion verify

Every scenario contains Preconditions.

Every scenario contains Test Data Requirements.

Every dependency documented.

Sensitive data identified.

Unknowns preserved.

No hidden assumptions.

---

# Common Mistakes

Do not generate production data.

Do not generate SQL inserts.

Do not generate JSON payloads.

Do not generate browser setup.

Do not invent business entities.

Do not invent configuration.

Do not remove Unknown values.

---

# Success Criteria

The Playwright Execution Agent should know exactly

What must already exist.

What data is required.

What permissions are required.

What state the application must be in.

before automation begins.

---

# Final Principle

Preconditions remove ambiguity.

Test Data enables confidence.

A complete scenario begins before the first action is performed.