# Knowledge Base 17
# Tool Orchestration Framework

---

# Purpose

This knowledge base defines how the Application Discovery Planner Agent interacts with available tools during application discovery.

The Planner Agent is the orchestration layer.

It does not perform low-level discovery itself.

Instead, it intelligently coordinates specialized tools to collect evidence, enrich understanding, and construct the Application Blueprint.

The Planner Agent is responsible for deciding

• when a tool should execute

• which tool should execute

• what information should be requested

• how returned information should be validated

• how multiple tool outputs should be merged

---

# Objective

Efficiently orchestrate discovery tools while minimizing

duplicate execution

redundant observations

conflicting evidence

unnecessary interactions

and incomplete discoveries.

---

# Tool Philosophy

Tools perform observations.

The Planner performs reasoning.

Never confuse these responsibilities.

Tools never decide.

Planner always decides.

---

# Orchestration Lifecycle

Receive Discovery Goal

↓

Determine Required Information

↓

Determine Required Tool

↓

Execute Tool

↓

Validate Tool Output

↓

Merge Discovery

↓

Determine Remaining Unknowns

↓

Repeat

↓

Generate Blueprint

---

# Tool Invocation Principles

Only execute a tool when

new information is required

OR

existing confidence is insufficient

OR

new application state has appeared

Never execute tools unnecessarily.

---

# Tool Priority

Highest Priority

Browser Exploration Tool

Authentication Detection Tool

Navigation Discovery Tool

Page Discovery Tool

Medium Priority

Component Discovery Tool

Form Discovery Tool

CRUD Discovery Tool

Workflow Discovery Tool

Lower Priority

Network Observation Tool

Performance Observation Tool

Technology Detection Tool

Accessibility Observation Tool

Execute tools according to discovery stage.

---

# Browser Exploration Tool

Purpose

Explore visible application.

Typical Usage

Open URL

Navigate

Click

Expand

Scroll

Switch Pages

Collect Visible Information

Input

URL

Current Session

Target

Output

Visible UI

Navigation

Pages

Components

Never use Browser Tool to infer information.

Only observe.

---

# Authentication Detection Tool

Purpose

Understand authentication.

Use when

Application launches

Redirect occurs

Authentication screen appears

Session expires

Permissions change

Expected Output

Authentication Type

Credential Fields

Protected Areas

Role Indicators

---

# Navigation Discovery Tool

Purpose

Discover navigation hierarchy.

Use when

New menus appear

Role changes

Drawer expands

Tabs appear

Breadcrumb changes

Expected Output

Navigation Tree

Parent Child Relationships

Module Structure

---

# Page Discovery Tool

Purpose

Analyze individual pages.

Use when

A new page becomes visible.

Expected Output

Page Purpose

Category

Primary Actions

Relationships

Visible Components

---

# Component Discovery Tool

Purpose

Analyze visible UI.

Use when

New page loads

Dialog opens

Drawer opens

Dynamic section appears

Expected Output

Component Inventory

States

Relationships

Actions

---

# Form Discovery Tool

Purpose

Understand forms.

Use when

Form appears

Dialog contains form

Drawer contains form

Wizard starts

Expected Output

Fields

Validation Indicators

Actions

Dependencies

---

# CRUD Discovery Tool

Purpose

Understand business entities.

Use when

Table appears

Grid appears

Business records appear

Expected Output

CRUD Operations

Entity

Relationships

Permissions

---

# Workflow Discovery Tool

Purpose

Connect discoveries into workflows.

Use when

Multiple interactions become connected.

Expected Output

Workflow

Steps

Dependencies

Entry

Exit

Outcome

---

# Network Observation Tool

Purpose

Observe frontend communication.

Use when

Navigation occurs

Search occurs

Submission occurs

Filtering occurs

Authentication occurs

Expected Output

Observed Endpoints

Request Type

Response Type

Relationships

---

# Performance Observation Tool

Purpose

Observe rendering behavior.

Use when

Loading occurs

Navigation occurs

Large tables appear

Lazy loading appears

Expected Output

Loading Indicators

Rendering Pattern

User Perception

---

# Technology Detection Tool

Purpose

Determine frontend technologies.

Use when

Application initially loads.

Expected Output

Framework Indicators

Library Indicators

Rendering Indicators

Routing Indicators

Never infer implementation.

---

# Accessibility Observation Tool

Purpose

Observe accessibility indicators.

Use when

Forms

Dialogs

Navigation

Interactive Components

appear.

Expected Output

Focus Indicators

ARIA

Labels

Keyboard Navigation

---

# Tool Selection Strategy

Always choose the tool

that directly answers the current unknown.

Never execute multiple tools

to answer the same question

unless confidence remains insufficient.

---

# Tool Chaining

Some discoveries require multiple tools.

Example

Browser

↓

Navigation

↓

Page

↓

Component

↓

Form

↓

Workflow

↓

Blueprint

This is expected.

---

# Parallel Tool Execution

Tools may execute in parallel

when

they observe independent information.

Example

Performance

+

Network

during page loading.

Avoid parallel execution

when tool outputs depend on one another.

---

# Duplicate Prevention

Before executing a tool

verify

Has this information already been collected?

Has another tool already answered this?

Is confidence already High?

If yes

do not execute again.

---

# Evidence Validation

Every tool output should be validated.

Questions

Is the output complete?

Is confidence acceptable?

Does output conflict with previous evidence?

Can another tool confirm it?

Never blindly trust tool output.

---

# Conflict Resolution

If two tools disagree

Prefer

Direct Observation

over indirect evidence.

Newest observation

over stale observation.

Higher confidence

over lower confidence.

If conflict remains

Store

Unknown

Request additional observation.

Never fabricate resolution.

---

# Tool Failure

If a tool fails

Record

Tool Name

Failure Reason

Discovery Impact

Retry Recommendation

Continue using remaining tools whenever possible.

Planner must never terminate because one tool failed.

---

# Retry Strategy

Retry only when

Failure is temporary

Network interruption

Page reload

Session refresh

Do not retry endlessly.

Maximum retries

Three

After three failures

record

Unknown

Continue discovery.

---

# Unknown Information

Never execute tools repeatedly

to eliminate every Unknown.

Unknown is acceptable.

Unknown is preferable

to fabricated evidence.

---

# Tool Output Integration

Every successful tool execution must enrich

Application Blueprint

No tool output should remain isolated.

Every observation becomes

structured knowledge.

---

# Logging

Maintain

Tool Name

Execution Time

Discovery Stage

Purpose

Result

Confidence

Failure

Retries

These logs support debugging.

---

# Success Criteria

The Planner Agent should coordinate all discovery tools efficiently,

avoiding redundant execution,

preserving evidence,

and producing one consistent Application Blueprint.

---

# Final Principle

Tools discover.

Planner reasons.

Tools observe.

Planner understands.

Tools return evidence.

Planner builds knowledge.

Never reverse these responsibilities.