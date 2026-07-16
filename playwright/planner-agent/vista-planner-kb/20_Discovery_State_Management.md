# Knowledge Base 20
# Discovery State Management

---

# Purpose

This knowledge base defines how the Application Discovery Planner Agent manages discovery progress throughout its execution.

Application discovery is a long-running process.

Discovery may pause, resume, restart, or partially complete.

The Planner Agent must preserve progress at every stage.

The objective is continuous discovery rather than perfect uninterrupted execution.

---

# Objective

Maintain

Discovery State

Current Progress

Application Blueprint

Evidence

Confidence

Tool Status

Session Status

Unknown Areas

Resume discovery without losing information.

---

# Discovery Philosophy

Discovery is incremental.

Knowledge accumulates.

Discovery should never restart unless explicitly requested.

Every successful observation should permanently strengthen the Application Blueprint.

---

# Discovery Lifecycle

Initialize

↓

Explore

↓

Checkpoint

↓

Continue

↓

Pause

↓

Resume

↓

Complete

Every transition should preserve state.

---

# Discovery Session

Each discovery execution belongs to one session.

A session contains

Session Identifier

Application URL

Platform

Environment

Start Time

Current Stage

Progress

Status

Blueprint Version

Evidence

Tool History

---

# Discovery States

Every session exists in one state.

Initialized

Running

Paused

Waiting

Recovering

Completed

Partially Completed

Interrupted

Failed

Cancelled

Unknown

Only one active state may exist at a time.

---

# Discovery Stages

Track the current stage.

Input Collection

Application Startup

Authentication

Navigation

Module Discovery

Page Discovery

Component Discovery

Form Discovery

CRUD Discovery

Workflow Discovery

Network Observation

Performance Observation

Blueprint Generation

Handoff

---

# Progress Tracking

Track

Visited Modules

Visited Pages

Visited Screens

Visited Dialogs

Visited Forms

Visited CRUD Modules

Visited Workflows

Visited Components

Observed APIs

Completed Stages

Remaining Stages

---

# Checkpoints

Create checkpoints during discovery.

Recommended checkpoints

Authentication Complete

Navigation Complete

Each New Module

Each New Workflow

Blueprint Updated

Before Tool Switch

Before Session End

Checkpoints reduce recovery time.

---

# Checkpoint Contents

Each checkpoint stores

Blueprint Snapshot

Discovery Progress

Visited Objects

Current Navigation

Evidence

Confidence

Tool Status

Session Status

Timestamp

Unknown Areas

---

# Resume Strategy

When resuming discovery

Restore

Blueprint

Progress

Navigation Queue

Visited Objects

Evidence

Confidence

Current Stage

Continue from the latest checkpoint.

Never restart automatically.

---

# Duplicate Prevention

During resume

Verify

Module already explored

Page already explored

Workflow already explored

Component already explored

Endpoint already observed

Avoid rediscovery unless evidence has changed.

---

# Incremental Discovery

New discoveries should

Extend

the existing blueprint.

Never replace

previous discoveries

without stronger evidence.

---

# Session Recovery

Recovery may occur after

Browser Crash

Authentication Timeout

Network Failure

Tool Failure

Application Restart

Planner Restart

Recover using the latest checkpoint.

---

# Authentication Expiry

If authentication expires

Record

Current Progress

Protected Areas

Completed Discovery

Unknown Areas

Reauthenticate if credentials exist.

Resume from last checkpoint.

---

# Tool Failure

If a tool fails

Record

Tool

Failure Reason

Discovery Impact

Retry Count

Fallback Tool

Continue using remaining tools.

Never terminate discovery because one tool failed.

---

# Retry Strategy

Retry only when

Temporary Failure

Page Reload

Navigation Failure

Session Refresh

Network Interruption

Maximum retries

Three

After maximum retries

Continue discovery.

Mark affected area

Unknown.

---

# Partial Discovery

Discovery is still valuable even when incomplete.

Record

Completed Sections

Incomplete Sections

Blocked Sections

Reason

Confidence

Never discard completed work.

---

# Blueprint Updates

Every successful discovery updates

Application Blueprint

Evidence

Confidence

Relationships

Metadata

Blueprint should evolve continuously.

---

# Unknown Areas

Maintain a dedicated list.

Examples

Restricted Modules

Permission Protected Pages

Session Expired Areas

Unavailable Navigation

Tool Failures

Unknown Components

Unknown is an expected outcome.

---

# Discovery Completion

Discovery completes when

Navigation exhausted

Maximum exploration depth reached

Application unavailable

User stops discovery

Planner interrupted

All reachable content explored

Unknown areas do not prevent completion.

---

# State Validation

Before every stage verify

Blueprint Loaded

Checkpoint Valid

Evidence Preserved

Navigation Queue Valid

Session Active

Current Stage Correct

---

# Session Metadata

Maintain

Planner Version

Blueprint Version

Knowledge Base Version

Discovery Duration

Checkpoint Count

Recovery Count

Retry Count

Tool Execution Count

Completion Percentage

---

# Integrity Rules

Never lose evidence.

Never lose confidence.

Never lose relationships.

Never duplicate discoveries.

Never overwrite stronger evidence.

Always preserve blueprint integrity.

---

# Logging

Record

Stage

Action

Timestamp

Tool

Result

Checkpoint

Recovery

Failure

Resume

Logs support debugging and auditing.

---

# Success Criteria

The Planner Agent should be able to pause, resume, recover, and complete long-running application discovery sessions without losing architectural knowledge.

The final Application Blueprint should remain consistent regardless of interruptions.

---

# Final Principle

Discovery is a continuous process.

Knowledge should survive interruptions.

Every observation should be preserved.

Every checkpoint should strengthen recovery.

The Planner Agent should continue from where it stopped, never from where it started.