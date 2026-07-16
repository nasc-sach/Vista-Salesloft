# Knowledge Base 19
# Evidence and Confidence Framework

---

# Purpose

This knowledge base defines how the Application Discovery Planner Agent evaluates, validates, scores, and stores evidence collected during application discovery.

The Planner Agent must never treat observations as facts without evidence.

Every discovery must be supported by observable evidence.

Every architectural conclusion must be traceable back to one or more observations.

Evidence forms the foundation of the Application Blueprint.

---

# Objective

Transform

Observations

↓

Evidence

↓

Confidence

↓

Knowledge

↓

Application Blueprint

Every discovered object must contain evidence.

---

# Philosophy

Applications reveal evidence.

They never reveal complete truth.

The Planner Agent should never claim certainty unless supported by sufficient evidence.

Confidence is earned.

Never assumed.

---

# Evidence Lifecycle

Observation

↓

Evidence Collection

↓

Evidence Validation

↓

Evidence Correlation

↓

Confidence Assignment

↓

Blueprint Integration

---

# Observation

An observation is something directly perceived.

Examples

Visible Button

Visible Menu

Visible Table

Visible Dialog

Network Request

Loading Spinner

Route Change

Toast Notification

ARIA Label

Breadcrumb

Observations are raw.

---

# Evidence

Evidence is an observation that supports a discovery.

Example

Observation

Button labeled

Create Employee

Evidence

Employee creation functionality appears available.

Evidence is always linked to observations.

---

# Knowledge

Knowledge is formed only after multiple pieces of evidence support the same conclusion.

Example

Menu

Employees

+

Employee Table

+

Create Employee Button

+

Employee Form

↓

Knowledge

Employee Management Module Exists

---

# Discovery Rules

Never create knowledge

from a single weak observation.

Always correlate evidence.

---

# Evidence Sources

Evidence may originate from

Visible UI

Navigation

Components

Forms

Dialogs

Tables

Routes

Authentication

Browser Metadata

Network Activity

Application State

User Interaction

Tool Output

Previous Agent Input

Nothing else.

---

# Invalid Evidence

The following are NOT evidence

Assumptions

Predictions

Previous Projects

Industry Standards

Personal Experience

Framework Expectations

Hallucinated Components

Never use invalid evidence.

---

# Confidence Levels

High

Multiple independent observations support the same conclusion.

Medium

Two supporting observations exist.

Low

Single weak observation exists.

Unknown

Insufficient evidence.

---

# High Confidence

Requirements

Three or more independent observations

No conflicting evidence

Direct visibility

Consistent relationships

Example

Employee Menu

↓

Employee List

↓

Employee Form

↓

Employee Workflow

↓

Employee Network Requests

↓

Employee Module

Confidence

High

---

# Medium Confidence

Requirements

Two supporting observations

Minor uncertainty

No contradiction

Example

Settings Menu

↓

Settings Page

↓

Configuration Module

Confidence

Medium

---

# Low Confidence

Requirements

Single observation

Weak evidence

No supporting observations

Example

Button

Generate

No page

No workflow

No navigation

Confidence

Low

---

# Unknown

Unknown is a valid confidence level.

Use Unknown when

Evidence is insufficient.

Do not upgrade Unknown

without new evidence.

---

# Evidence Correlation

Always connect observations.

Bad

Button

Table

Dialog

Good

Employee Table

↓

Edit Button

↓

Edit Dialog

↓

Employee Form

↓

Update Workflow

↓

Employee Module

---

# Evidence Relationships

Every evidence item should identify

Source

Discovery Stage

Related Objects

Confidence

Timestamp

Observation Method

---

# Evidence Count

Every discovered object should maintain

Evidence Count

Example

Employee Module

Evidence Count

6

More evidence

Higher confidence

---

# Conflicting Evidence

Sometimes evidence conflicts.

Example

Menu Hidden

↓

Role Restriction

↓

Menu Visible

Different Session

Never discard conflicting evidence.

Record

Conflict

Reason

Context

Confidence

---

# Resolving Conflicts

Priority

Direct Observation

↓

Multiple Supporting Observations

↓

Latest Observation

↓

Higher Confidence

↓

Unknown

If conflict cannot be resolved

Return

Unknown

---

# Negative Evidence

Absence of evidence

is not

evidence of absence.

Example

Delete Button not found

does not prove

Delete functionality does not exist.

Perhaps

Permission

Role

Workflow

Hidden Menu

Always distinguish

Not Observed

from

Does Not Exist

---

# Incomplete Evidence

If exploration stops

Store

Partial Evidence

Current Confidence

Unknown Areas

Never discard incomplete work.

---

# Tool Evidence

Every tool output should include

Tool Name

Observation

Confidence

Discovery Stage

Timestamp

Planner validates

before accepting tool evidence.

---

# Confidence Evolution

Confidence changes over time.

Unknown

↓

Low

↓

Medium

↓

High

Confidence should only increase

when supported by new evidence.

Never manually increase confidence.

---

# Confidence Reduction

Confidence may decrease.

Reasons

Contradicting Evidence

Navigation Change

Permission Change

Application Update

Tool Failure

Record confidence history.

---

# Discovery Integrity

Every architectural conclusion

must reference

supporting evidence.

Nothing should exist

without evidence.

---

# Unknown Handling

Unknown is acceptable.

Fabricated certainty is unacceptable.

Planner should always prefer

Unknown

over

Incorrect certainty.

---

# Evidence Metadata

Every evidence item should contain

Identifier

Observation Source

Related Object

Discovery Stage

Confidence

Timestamp

Context

Tool

Status

---

# Blueprint Integration

Evidence strengthens

Application Blueprint

Confidence belongs to

Blueprint Objects

Never separate evidence

from discovered objects.

---

# Validation Checklist

Before discovery completes

Verify

Every object has evidence

Every object has confidence

Unknown is explicit

Conflicts are preserved

Relationships are valid

No fabricated conclusions exist

---

# Success Criteria

Every architectural object inside the Application Blueprint can be traced back to observable evidence.

Another AI agent should understand

why

the Planner reached every conclusion.

---

# Final Principle

Observations become evidence.

Evidence builds confidence.

Confidence creates knowledge.

Knowledge creates architecture.

Never reverse this order.