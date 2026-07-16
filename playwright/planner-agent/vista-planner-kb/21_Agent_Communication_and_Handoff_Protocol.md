# Knowledge Base 21
# Agent Communication and Handoff Protocol

---

# Purpose

This knowledge base defines how the Application Discovery Planner Agent communicates with other agents inside the AI Test Automation Workflow.

The Planner Agent is not an isolated system.

It is one stage within a multi-agent architecture.

Its responsibility is to receive structured information from the previous agent, enrich that information through discovery, and hand over a complete Application Blueprint to the next agent.

Agents must communicate using contracts rather than assumptions.

---

# Workflow Position

Previous Agent

Input Collection Agent

↓

Current Agent

Application Discovery Planner Agent

↓

Next Agent

Test Strategy Agent

---

# Communication Philosophy

Agents never communicate through conversation.

Agents communicate through structured information.

Every handoff must be

Complete

Deterministic

Versioned

Self-contained

Evidence-backed

No downstream agent should need to ask the Planner for clarification.

---

# Planner Responsibilities

Receive

↓

Validate

↓

Discover

↓

Enrich

↓

Model

↓

Package

↓

Transfer

Never skip any stage.

---

# Previous Agent Contract

The Planner Agent expects structured input from the Input Collection Agent.

The previous agent is responsible for

collecting

validating

and normalizing

user inputs.

The Planner Agent should never perform user interviews.

---

# Expected Input

The previous agent may provide

Frontend URL

Platform

Browser

Execution Mode

Environment

Credentials

Authentication Method

Device Type

Viewport

Language

Additional Instructions

Session Metadata

Discovery Configuration

Optional Parameters

All fields except Frontend URL are optional.

---

# Required Input

The following information is mandatory.

Frontend URL

If no URL exists

Discovery cannot begin.

---

# Optional Input

Examples

Username

Password

SSO Information

OTP Availability

Preferred Browser

Desktop

Tablet

Mobile

Execution Depth

Excluded Modules

Discovery Scope

Application Notes

These should enhance discovery.

Never become mandatory.

---

# Input Validation

Before discovery begins verify

URL Exists

Platform Supported

Configuration Valid

Browser Supported

Discovery Scope Valid

Unknown optional values should remain Unknown.

---

# Planner Output

The Planner Agent produces exactly one deliverable.

Application Blueprint

Nothing else.

---

# Blueprint Ownership

Once generated

the Application Blueprint becomes immutable.

Downstream agents may

read

reference

annotate

but should never modify Planner discoveries.

New information should exist as downstream metadata.

Never overwrite Planner observations.

---

# Next Agent Contract

The Test Strategy Agent receives

Application Blueprint

Discovery Metadata

Evidence

Confidence

Unknown Areas

Discovery Recommendations

No additional discovery should be required.

---

# Handoff Contents

Every handoff contains

Application Blueprint

Discovery Status

Confidence Summary

Unknown Areas

Restricted Areas

Visited Modules

Visited Pages

Visited Workflows

Evidence Summary

Planner Metadata

Version Information

---

# Discovery Metadata

Metadata includes

Discovery Start

Discovery End

Planner Version

Knowledge Base Version

Blueprint Version

Discovery Duration

Completion Percentage

Checkpoint Count

Recovery Count

Tool Execution Summary

---

# Unknown Areas

Unknowns are first-class citizens.

Examples

Restricted Pages

Permission Protected Modules

Authentication Required Areas

Session Timeout

Navigation Blocked

Unsupported Platform

Tool Failure

Unknowns must be preserved.

Never remove them.

---

# Confidence Transfer

Every object transferred must contain

Confidence

Evidence Count

Observation Source

Discovery Status

Downstream agents must preserve confidence.

Confidence belongs to Planner discoveries.

---

# Version Compatibility

Every handoff should contain

Planner Version

Blueprint Version

Schema Version

Knowledge Base Version

Communication Version

Downstream agents should validate compatibility before processing.

---

# Communication Principles

Never omit required information.

Never fabricate missing values.

Never remove Unknown.

Never flatten hierarchy.

Never duplicate objects.

Always preserve relationships.

Always preserve evidence.

---

# Immutable Discoveries

The following objects are immutable after handoff

Application

Modules

Pages

Components

Forms

CRUD Entities

Workflows

Navigation

Authentication

Network Observations

Performance Observations

If downstream agents discover new information

they should extend

not modify

Planner output.

---

# Downstream Responsibilities

The Test Strategy Agent is responsible for

interpreting

prioritizing

and planning

tests.

It is not responsible for rediscovery.

The Planner should eliminate unnecessary rediscovery.

---

# Communication Failures

If handoff fails

Record

Failure Reason

Transfer Status

Blueprint Version

Retry Count

Timestamp

Never regenerate the blueprint unnecessarily.

Retry transfer.

---

# Partial Discovery

Partial discoveries may still be transferred.

Include

Completed Areas

Unknown Areas

Blocked Areas

Confidence

Discovery Completion

Reason

Downstream agents should continue using available information.

---

# Retry Strategy

Retry communication only when

Temporary Failure

Network Failure

Agent Unavailable

Timeout

Maximum retries

Three

After maximum retries

Persist Blueprint

Record Failure

Notify Workflow

---

# Communication Logging

Maintain

Sender

Receiver

Timestamp

Blueprint Version

Transfer Status

Payload Identifier

Retry Count

Duration

Logs support auditability.

---

# Security

Never transfer

Passwords

Authentication Tokens

Cookies

Sensitive Session Data

Personally Identifiable Information

Secrets

Only transfer discovery information.

---

# Success Criteria

The Test Strategy Agent should begin strategy generation immediately after receiving the Application Blueprint.

No additional clarification should be required.

The handoff should be deterministic, complete, and self-contained.

---

# Final Principle

The Planner Agent does not simply finish discovery.

It transfers architectural knowledge.

The Application Blueprint is the official communication contract between discovery and testing.

Every downstream agent should trust the blueprint,

preserve its integrity,

and build upon it,

never replace it.