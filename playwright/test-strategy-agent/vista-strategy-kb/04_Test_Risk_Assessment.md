# Knowledge Base 04
# Testing Risk Assessment

---

# Purpose

This knowledge base teaches the Test Strategy Planner Agent how to assess testing risk for every business capability discovered in the Application Blueprint.

Testing risk determines how much testing effort should be allocated to a feature.

Testing risk is influenced by business criticality, workflow importance, data sensitivity, user impact, and operational consequences.

Testing risk is not equivalent to implementation complexity.

Testing risk exists to optimize testing effort.

---

# Objective

Analyze

Business Criticality

↓

Business Workflows

↓

Business Dependencies

↓

Failure Consequences

↓

Testing Risk

↓

Testing Priority

↓

Testing Strategy Blueprint

---

# Philosophy

Testing resources are finite.

Not every feature deserves identical testing effort.

Testing effort should increase with testing risk.

High-risk capabilities require deeper validation.

Low-risk capabilities require proportionally lower effort.

---

# Risk Assessment Lifecycle

Business Criticality

↓

Workflow Analysis

↓

Failure Analysis

↓

Operational Impact

↓

User Impact

↓

Testing Risk

↓

Testing Priority

---

# Risk Dimensions

Evaluate every feature across the following dimensions

Business Risk

Operational Risk

Workflow Risk

Data Risk

Permission Risk

Recovery Risk

Integration Risk

Availability Risk

Security Sensitivity

Configuration Risk

Every dimension should be considered.

---

# Business Risk

Determine

What business operations fail if this capability becomes unavailable.

Examples

Authentication

Employee Management

Scheduling

Payments

Reporting

Administration

Higher business disruption increases testing risk.

---

# Operational Risk

Determine

How much operational disruption occurs.

Examples

Application Unusable

Primary Workflow Blocked

Major Workflow Delayed

Minor Workflow Delayed

Cosmetic Impact

Operational disruption influences testing depth.

---

# Workflow Risk

Determine

How many workflows depend upon this feature.

Examples

Authentication

↓

Every Workflow

Employee Search

↓

Several Workflows

Help

↓

Independent

More dependent workflows increase testing risk.

---

# Data Risk

Determine sensitivity of affected data.

Examples

Public

Internal

Business

Confidential

Financial

Healthcare

Personal Information

Sensitive data requires greater testing confidence.

---

# Permission Risk

Determine whether incorrect permissions could affect

Visibility

Access

Modification

Deletion

Administration

Role Assignment

Permission-sensitive features require expanded testing.

---

# Integration Risk

Determine whether the feature depends upon

External Services

Internal APIs

Authentication Providers

Notifications

Payments

Reporting

Imports

Exports

Higher integration increases testing risk.

---

# Recovery Risk

Determine

How difficult recovery would be after failure.

Examples

Automatic Recovery

User Retry

Administrator Action

Manual Database Recovery

Unknown

Difficult recovery increases testing effort.

---

# Availability Risk

Determine

Can users continue working if this feature fails?

Categories

No Impact

Minor Impact

Reduced Productivity

Major Workflow Failure

Application Unusable

---

# User Impact

Estimate

Very High

High

Medium

Low

Rare

Frequently used functionality generally deserves deeper testing.

---

# Failure Consequences

Analyze

Data Loss

Workflow Failure

Permission Failure

Customer Impact

Operational Delay

Financial Loss

Compliance Issues

Reputation Damage

The greater the consequence, the greater the testing effort.

---

# Testing Risk Levels

Assign one value

Critical

High

Medium

Low

Minimal

Every level requires justification.

---

# Risk Justification

Every assessment should explain

Business Reason

Workflow Dependency

Operational Impact

Failure Consequences

Data Sensitivity

Recovery Difficulty

Never assign risk without explanation.

---

# Relationship Between Criticality and Risk

Business Criticality and Testing Risk are related but independent.

Examples

Login

Business Criticality

Critical

Testing Risk

High

Help

Business Criticality

Low

Testing Risk

Low

Reports

Business Criticality

High

Testing Risk

Critical

Do not automatically copy Business Criticality into Testing Risk.

---

# Unknown Areas

If evidence is insufficient

Assign

Unknown

Document

Reason

Unknown is acceptable.

Guessing is unacceptable.

---

# Confidence

Confidence inherits from the Application Blueprint.

Levels

High

Medium

Low

Unknown

Do not inflate confidence.

---

# Traceability

Every Testing Risk decision must reference

Business Module

Workflow

Planner Evidence

Business Criticality

Justification

Confidence

---

# Validation

Before completion verify

Every module assessed

Every workflow assessed

Every high-risk capability justified

Unknowns preserved

No conflicting assessments

---

# Output

Generate

Testing Risk Matrix

Containing

Business Module

Business Function

Business Criticality

Testing Risk

Operational Impact

Workflow Dependency

Failure Consequences

Data Sensitivity

Recovery Difficulty

Justification

Confidence

Unknown Areas

---

# Common Mistakes

Do not confuse implementation complexity with testing risk.

Do not copy Business Criticality directly into Testing Risk.

Do not ignore workflow dependencies.

Do not underestimate permission-sensitive features.

Do not remove Unknown values.

Do not duplicate Planner observations.

---

# Success Criteria

The downstream Coverage Planning process should understand where testing effort should be concentrated and why.

Testing priorities should be explainable, evidence-backed, and proportional to risk.

---

# Final Principle

Business Criticality answers

"What is important?"

Testing Risk answers

"What deserves greater testing effort?"

Understand both before planning coverage.