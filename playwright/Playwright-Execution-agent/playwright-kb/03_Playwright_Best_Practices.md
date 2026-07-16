# Knowledge Base 03
# Playwright Best Practices

---

# Purpose

This knowledge base defines the engineering standards for generating maintainable, reliable, reusable, and deterministic Playwright automation.

The objective is to ensure that every generated Playwright test follows consistent engineering practices while remaining faithful to the Scenario Specification Blueprint.

The Playwright Execution Agent should generate automation that is stable, maintainable, reusable, and scalable.

---

# Philosophy

Automation should be treated as production software.

Generated automation should be

Readable

Maintainable

Reusable

Deterministic

Scalable

Avoid generating scripts that only work for one execution.

---

# General Principles

Automation should

Follow Playwright best practices.

Prefer readability over cleverness.

Reuse existing logic whenever possible.

Avoid duplicate code.

Fail predictably.

Produce useful execution evidence.

---

# Test Organization

Organize automation using

Configuration

↓

Fixtures

↓

Utilities

↓

Page Objects

↓

Tests

↓

Execution Reports

Separate concerns.

Never mix business logic with browser interaction logic.

---

# Single Responsibility

Each generated Playwright test should validate one Scenario Specification.

Each Page Object should represent one application page or component.

Each helper function should perform one reusable operation.

Avoid large monolithic tests.

---

# Naming Standards

Generated identifiers should be meaningful.

Examples

Authentication Tests

Employee CRUD Tests

Customer Workflow Tests

Reporting Tests

Search Tests

Filtering Tests

Avoid generic names.

Avoid generated random identifiers.

---

# Page Object Principles

Page Objects should contain

Navigation

Element Actions

Reusable Browser Operations

Synchronization

Page Utilities

Page Objects should never contain

Business Rules

Testing Strategy

Scenario Decisions

Assertions unrelated to page behaviour

---

# Reusable Components

Identify reusable browser interactions.

Examples

Authentication

Navigation

Common Forms

Common Dialogs

Confirmation Popups

Toast Verification

File Upload

Search Components

Filtering Components

Reuse instead of duplication.

---

# Locator Best Practices

Preferred order

Accessibility Locator

Data Test Identifier

Role Locator

Label Locator

Placeholder Locator

Visible Text

CSS Selector

XPath

Prefer stable locators.

Avoid positional selectors.

Avoid brittle selectors.

---

# Synchronization

Prefer explicit synchronization.

Examples

Page Loaded

Element Visible

Element Enabled

Request Completed

Navigation Finished

Application Ready

Avoid fixed waits.

Avoid arbitrary delays.

Automation should wait for application readiness.

---

# Assertions

Assertions should originate only from

Verification Objectives

Logical Assertions

Expected Outcomes

Avoid redundant assertions.

Avoid implementation-specific assertions.

Assertions should validate business behaviour.

---

# Data Handling

Use scenario-defined test data.

Avoid hardcoded values.

Prefer parameterized data.

Support dynamically generated values.

Protect sensitive information.

Never expose secrets.

---

# Error Handling

Gracefully handle

Timeouts

Navigation Failures

Unexpected Dialogs

Missing Elements

Assertion Failures

Authentication Expiration

Unexpected Redirects

Execution should capture useful diagnostics.

---

# Retry Strategy

Retries should be controlled.

Retry only when configured.

Report retry attempts.

Never hide failures through excessive retries.

---

# Parallel Execution

Scenarios should support parallel execution whenever dependencies allow.

Avoid shared mutable state.

Avoid execution interference.

Respect Execution Sequence when dependencies exist.

---

# Logging

Capture structured execution logs.

Record

Scenario

Phase

Action

Duration

Status

Error Summary

Do not generate excessive logging.

---

# Browser Interaction

Browser actions should be deterministic.

Avoid

Random waits

Repeated clicking

Blind retries

Force clicking without justification

Browser interaction should reflect Scenario Phases.

---

# Navigation

Always verify successful navigation.

Avoid assuming navigation succeeded.

Detect

Unexpected Redirects

Missing Pages

Authentication Redirects

Permission Redirects

Navigation Failures

---

# Form Interaction

Populate forms using

Scenario Test Data

Verify

Required Fields

Validation

Submission

Business Outcomes

Avoid interacting with hidden elements.

---

# Dialog Handling

Handle

Confirmation Dialogs

Alert Dialogs

Modal Windows

Side Panels

Popup Windows

Only when required by the Scenario.

---

# File Operations

Support

Upload

Download

Export

Import

Only when defined by the Scenario Specification.

Never invent file operations.

---

# Session Handling

Support

Login

Logout

Session Expiration

Session Recovery

Role Switching

Concurrent Sessions

Only when required.

---

# Cleanup

Restore application state whenever required.

Cleanup should

Maintain test independence.

Avoid affecting subsequent executions.

Only perform cleanup when specified by the Scenario.

---

# Performance

Automation should prioritize reliability over speed.

Avoid unnecessary browser interactions.

Reuse existing browser state when appropriate.

Avoid redundant navigation.

---

# Security

Never log

Passwords

Tokens

Secrets

Cookies

Personally Identifiable Information

Sensitive business information

Sensitive values should always be masked.

---

# Evidence Collection

Capture structured evidence.

Include

Execution Status

Execution Timeline

Navigation History

Interaction History

Console Summary

JavaScript Exception Summary

Network Summary

Execution Metadata

Automation Metadata

Evidence should remain text-based.

---

# Quality Checklist

Before execution verify

Scenario completely translated.

Page Objects reusable.

Locators stable.

Synchronization deterministic.

Assertions complete.

Logging enabled.

Evidence collection enabled.

Execution metadata enabled.

---

# Common Mistakes

Do not hardcode waits.

Do not hardcode URLs unless defined.

Do not duplicate browser interactions.

Do not generate unnecessary assertions.

Do not ignore synchronization.

Do not expose secrets.

Do not use unstable locators.

Do not mix business logic into Page Objects.

Do not redesign Scenario Specifications.

---

# Success Criteria

Generated Playwright automation should be

Readable

Reusable

Reliable

Deterministic

Maintainable

Scalable

Evidence-rich

Production-ready

---

# Final Principle

Automation quality is measured by

Reliability,

Maintainability,

Reusability,

Determinism,

and

Faithfulness to the Scenario Specification Blueprint.

The Playwright Execution Agent should generate automation that engineers can confidently execute, maintain, and extend.