# Knowledge Base 03
# Business Criticality Assessment

---

# Purpose

This knowledge base teaches the Test Strategy Planner Agent how to determine the business importance of application features before assigning testing priorities.

Business criticality represents the impact that a failure would have on the organization, end users, and business operations.

Business criticality is independent of implementation complexity.

A technically simple feature may still be business critical.

Business criticality must always be evaluated before risk assessment.

---

# Objective

Analyze

Application Blueprint

↓

Business Modules

↓

Business Functions

↓

Business Dependencies

↓

Business Importance

↓

Criticality Classification

↓

Provide Business Criticality Model

---

# Philosophy

Not every application feature has equal business value.

Testing effort should follow business value.

Features that enable users to achieve primary business objectives require greater testing attention.

Business value should always be determined before technical considerations.

---

# Assessment Lifecycle

Application Blueprint

↓

Identify Business Goals

↓

Identify Business Functions

↓

Identify User Objectives

↓

Identify Business Dependencies

↓

Determine Business Impact

↓

Assign Criticality

↓

Record Justification

---

# Business Goals

Determine

Why the application exists.

Examples

Employee Management

Project Tracking

Scheduling

Inventory Management

Healthcare

Banking

Payments

CRM

E-commerce

Learning

Analytics

Communication

Business goals guide criticality.

---

# Business Functions

Every module provides one or more business functions.

Examples

Authentication

Employee Creation

Project Assignment

Shift Scheduling

Invoice Generation

Order Placement

Customer Registration

Report Generation

Notification Management

Settings

Help

Document each business function.

---

# Primary User Objectives

Determine

What users are trying to accomplish.

Examples

Login

Create Employee

Approve Leave

Generate Report

Assign Task

Place Order

Update Profile

Track Shipment

Business objectives drive testing priority.

---

# Critical Business Modules

Examples

Authentication

Authorization

Payments

Employee Management

Scheduling

Order Processing

Inventory

Project Management

Reporting

Administration

These modules often require higher testing coverage.

---

# Supporting Modules

Examples

Notifications

Preferences

Profile

Search

Help

Documentation

Theme

Feedback

These may require lower testing depth depending on business purpose.

---

# Business Dependency

Determine whether a feature enables another feature.

Examples

Authentication

↓

Dashboard

↓

Employee Module

↓

Employee Workflow

Failure in Authentication affects every downstream module.

Dependencies increase business importance.

---

# User Frequency

Estimate relative usage.

Categories

Very High

High

Medium

Low

Rare

Frequently used features generally deserve more testing attention.

---

# Operational Dependency

Determine

How many workflows depend on a feature.

Examples

Authentication

Used by every workflow.

Reports

Used occasionally.

Settings

Used infrequently.

Higher dependency increases criticality.

---

# Business Impact Levels

Classify

Critical

High

Medium

Low

Informational

Definitions

Critical

Application cannot fulfill its primary purpose.

High

Major business capability affected.

Medium

Business continues with reduced efficiency.

Low

Minor inconvenience.

Informational

No meaningful operational impact.

---

# Business Criticality Factors

Consider

Business Purpose

Workflow Dependency

Operational Dependency

User Frequency

Business Visibility

Customer Impact

Financial Impact

Regulatory Impact

Data Sensitivity

Service Availability

Recovery Importance

Evaluate every factor.

---

# Business Visibility

Determine

Internal

Customer Facing

Partner Facing

Public

Public-facing functionality generally carries greater business importance.

---

# Financial Impact

Determine whether failures may affect

Revenue

Billing

Payments

Orders

Subscriptions

Invoices

Licensing

Financially sensitive functions deserve higher priority.

---

# Regulatory Impact

Examples

Healthcare

Finance

Government

Education

Compliance

Privacy

Audit

Security

Regulated functionality typically requires greater testing.

---

# Data Sensitivity

Determine

Public Data

Internal Data

Business Data

Personal Data

Financial Data

Healthcare Data

Confidential Data

Sensitive data increases business importance.

---

# Workflow Contribution

Determine whether a feature

Starts a workflow

Continues a workflow

Completes a workflow

Supports a workflow

Business-critical workflow stages deserve greater attention.

---

# Criticality Scoring

Assign one value

Critical

High

Medium

Low

Informational

Every score must include a justification.

---

# Justification

Every criticality decision should explain

Business Reason

Primary User

Business Goal

Dependencies

Impact

Never assign criticality without explanation.

---

# Unknown Areas

If insufficient information exists

Assign

Unknown

Document why.

Never guess business importance.

---

# Confidence

Confidence inherits from the Application Blueprint.

Levels

High

Medium

Low

Unknown

Never increase confidence without supporting evidence.

---

# Traceability

Every business criticality decision must reference

Business Module

Planner Evidence

Workflow

Application Blueprint Object

Justification

---

# Validation

Before completion verify

Every business module classified

Every workflow classified

Criticality justification present

Unknowns preserved

No conflicting classifications

---

# Output

Generate

Business Criticality Matrix

Containing

Business Module

Business Function

Primary Users

Business Goal

Criticality

Business Impact

Dependencies

Frequency

Justification

Confidence

Unknown Areas

---

# Common Mistakes

Do not confuse technical complexity with business importance.

Do not classify based on personal opinion.

Do not assume every CRUD module is critical.

Do not ignore supporting workflows.

Do not remove Unknown values.

Do not duplicate Planner observations.

---

# Success Criteria

The downstream Risk Assessment process should understand which application capabilities are most important to the business and why.

Business importance should be clear before technical risk is evaluated.

---

# Final Principle

Business value determines what deserves attention.

Criticality determines testing investment.

Always understand the business before assessing the risk.