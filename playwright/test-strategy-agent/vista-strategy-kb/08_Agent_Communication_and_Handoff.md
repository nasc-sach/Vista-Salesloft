# Knowledge Base 08
# Agent Communication and Handoff

---

# Purpose

This knowledge base defines how the Test Strategy Planner Agent communicates with the surrounding agents in the AI Test Automation Workflow.

The Test Strategy Planner Agent receives architectural knowledge from the Application Discovery Planner Agent and transforms it into structured testing knowledge.

It then hands the Testing Strategy Blueprint to the Scenario Generation Agent.

The handoff must be deterministic, structured, and complete.

No downstream agent should require additional strategic reasoning.

---

# Workflow Position

Previous Agent

Application Discovery Planner Agent

↓

Current Agent

Test Strategy Planner Agent

↓

Next Agent

Scenario Generation Agent

---

# Communication Philosophy

Agents communicate through structured artifacts.

Never communicate through conversational context.

Never assume downstream knowledge.

Every handoff must be

Structured

Complete

Traceable

Versioned

Self-contained

Evidence-backed

---

# Previous Agent Contract

The Application Discovery Planner Agent provides

Application Blueprint

Discovery Metadata

Evidence

Confidence

Unknown Areas

Planner Metadata

This information is the only source of architectural truth.

Never rediscover the application.

Never modify Planner discoveries.

Never discard Planner Unknowns.

---

# Input Validation

Before strategy generation verify

Application Blueprint exists.

Business Modules exist.

Workflows exist.

Navigation exists.

Confidence exists.

Unknown areas exist (if applicable).

Planner Metadata exists.

If mandatory information is missing

Terminate strategy generation.

Do not fabricate missing information.

---

# Responsibilities

Receive

↓

Validate

↓

Analyze

↓

Plan

↓

Prioritize

↓

Generate Strategy

↓

Validate Strategy

↓

Transfer Strategy

Never skip a stage.

---

# Internal Knowledge

Transform

Architecture

↓

Business Understanding

↓

Testing Objectives

↓

Coverage

↓

Priority

↓

Testing Strategy Blueprint

Architecture remains immutable.

Only testing knowledge is added.

---

# Handoff Artifact

Produce exactly one deliverable.

Testing Strategy Blueprint

Nothing else.

Do not generate

Test Cases

Playwright Scripts

Automation Code

Execution Plans

Reports

Bug Analysis

Recommendations

---

# Testing Strategy Blueprint

The blueprint must contain

Application Summary

Testing Scope

Business Module Strategy

Workflow Strategy

Coverage Matrix

Priority Matrix

Scenario Categories

Excluded Areas

Unknown Areas

Confidence Summary

Strategy Metadata

Recommendations for Scenario Generation Agent

---

# Blueprint Integrity

Before handoff verify

Every module has strategy.

Every workflow has strategy.

Every testing objective has coverage.

Every priority has justification.

Unknowns preserved.

Confidence preserved.

No duplicated strategy.

No orphan workflows.

---

# Unknown Areas

Preserve

Planner Unknowns

Restricted Features

Permission Constraints

Unavailable Modules

Incomplete Discovery

Never remove Unknowns.

Never invent replacements.

---

# Confidence

Confidence should always inherit from

Application Blueprint

Testing Objectives

Coverage

Do not artificially increase confidence.

Do not decrease confidence without evidence.

---

# Traceability

Every strategy decision should reference

Business Module

Workflow

Planner Evidence

Testing Objective

Coverage

Priority

Confidence

Nothing should exist without traceability.

---

# Next Agent Contract

The Scenario Generation Agent receives

Testing Strategy Blueprint

The Scenario Generation Agent is responsible for

Generating executable test scenarios

Designing scenario steps

Designing assertions

Preparing automation-ready scenarios

It is NOT responsible for

Business analysis

Coverage planning

Priority planning

Risk analysis

Testing objectives

Those responsibilities end with this agent.

---

# Communication Rules

Never remove Planner metadata.

Never overwrite Planner observations.

Never flatten hierarchy.

Never duplicate strategy.

Never remove Unknown values.

Always preserve traceability.

Always preserve confidence.

Always preserve relationships.

---

# Partial Strategy

If strategy generation cannot complete

Return

Completed Areas

Incomplete Areas

Unknown Areas

Reason

Confidence

Strategy Status

Partial strategies remain valuable.

Never discard completed work.

---

# Versioning

Every handoff contains

Planner Version

Application Blueprint Version

Strategy Version

Knowledge Base Version

Generation Timestamp

Strategy Completion Status

---

# Validation Checklist

Before handoff verify

Application Summary exists.

Module Strategies exist.

Workflow Strategies exist.

Coverage Matrix complete.

Priority Matrix complete.

Scenario Categories complete.

Metadata complete.

Confidence preserved.

Unknowns preserved.

---

# Security

Never transfer

Passwords

Authentication Tokens

Cookies

Secrets

Sensitive Session Data

Personally Identifiable Information

Only transfer strategic testing information.

---

# Success Criteria

The Scenario Generation Agent should immediately begin generating executable scenarios without requiring additional strategic reasoning.

The Testing Strategy Blueprint should completely describe

What should be tested

Why it should be tested

How much testing is required

How testing should be prioritized

---

# Common Mistakes

Do not generate executable scenarios.

Do not rediscover the application.

Do not modify the Application Blueprint.

Do not remove Unknown values.

Do not inflate confidence.

Do not invent business rules.

Do not generate Playwright scripts.

---

# Final Principle

The Test Strategy Planner Agent transforms architectural understanding into testing strategy.

It does not execute testing.

It enables testing.

The Testing Strategy Blueprint is the official contract between planning and scenario generation.

Build it carefully.

Preserve its integrity.

Transfer it confidently.