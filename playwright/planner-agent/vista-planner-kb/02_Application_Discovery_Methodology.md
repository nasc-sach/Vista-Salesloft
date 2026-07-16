# Knowledge Base 02
# Application Discovery Methodology

---

# Purpose

This document defines the systematic methodology that the Application Discovery Planner Agent must follow while exploring an unknown application.

The methodology ensures every application is explored consistently regardless of technology stack, business domain, or UI complexity.

Never skip discovery stages.

Never randomly explore pages.

Always follow this methodology.

---

# Discovery Philosophy

Application discovery is a structured process.

Do not click random buttons.

Do not randomly navigate.

Do not make assumptions.

Treat every application as completely unknown.

Your objective is to progressively reduce uncertainty until a complete application blueprint is created.

---

# Discovery Lifecycle

Always follow this exact sequence.

Stage 1

Receive Input

↓

Stage 2

Validate Accessibility

↓

Stage 3

Establish Session

↓

Stage 4

Discover Authentication

↓

Stage 5

Discover Navigation

↓

Stage 6

Discover Application Modules

↓

Stage 7

Discover Individual Pages

↓

Stage 8

Discover UI Components

↓

Stage 9

Discover Workflows

↓

Stage 10

Discover Data Operations

↓

Stage 11

Discover Integrations

↓

Stage 12

Generate Structured Blueprint

Never change this sequence.

---

# Stage 1
# Receive Input

The previous workflow provides structured input.

Possible inputs include

Frontend URL

Platform

Browser

Credentials

Environment

Additional Instructions

Do not modify input.

Do not validate business correctness.

Only ensure required values exist.

---

# Stage 2
# Validate Accessibility

Verify

• URL is reachable

• Application loads

• Browser session starts

Observe

HTTP status

Initial redirects

SSL warnings

Application loading state

Initial title

Application favicon

Loading spinner

If application cannot be reached

Terminate discovery.

Produce partial output.

---

# Stage 3
# Establish Session

Determine

Does application require authentication?

Does application automatically login?

Does application redirect?

Does application use SSO?

Does application use OAuth?

Does application show guest mode?

Determine only.

Do not test authentication.

---

# Stage 4
# Authentication Discovery

If login exists

Discover

Login URL

Authentication type

Username fields

Password fields

OTP

Remember Me

Forgot Password

Password visibility toggle

Captcha

Social Login

SSO

MFA

Authentication redirects

Session timeout indicators

Logout location

Never brute force credentials.

Never intentionally fail authentication.

Observe only.

---

# Stage 5
# Navigation Discovery

Navigation is the backbone of the application.

Identify

Top Navigation

Side Navigation

Bottom Navigation

Drawer Navigation

Floating Menu

Hamburger Menu

Breadcrumb

Tabs

Nested Navigation

Accordion Navigation

Quick Links

Profile Menu

Context Menu

Settings

Help

Support

Notifications

Search

User Avatar

Every navigation item represents a possible application module.

Record all of them.

---

# Stage 6
# Application Module Discovery

A module is a logical business capability.

Examples

Dashboard

Orders

Customers

Employees

Inventory

Reports

Settings

Profile

Notifications

Calendar

Tasks

Analytics

Approvals

Administration

Billing

AI Assistant

Scheduler

Roster

Shift Management

Do not name modules yourself.

Use names visible inside UI.

---

# Stage 7
# Page Discovery

Every module contains pages.

For every page discover

Page Name

Route

Visible URL

Parent Module

Purpose

Primary Components

Major Actions

Navigation Source

Entry Method

Exit Method

Empty State

Loading State

Error State

Permission Indicator

Unknown values should remain Unknown.

---

# Stage 8
# UI Component Discovery

Inspect every page.

Identify

Buttons

Text Fields

Dropdowns

Checkboxes

Radio Buttons

Date Pickers

Time Pickers

Tables

Cards

Charts

Dialogs

Accordions

Tabs

Steppers

Search Bars

Pagination

Tree Views

Toast Notifications

Snackbars

Badges

Tags

Progress Bars

Upload Controls

Download Controls

Floating Buttons

Drawer Panels

Side Sheets

Each component may represent future testing scope.

---

# Stage 9
# Workflow Discovery

A workflow is a connected sequence of user actions.

Examples

Login

Create Employee

Delete Employee

Generate Report

Export CSV

Approve Leave

Assign Shift

Publish Roster

Reset Password

Each workflow has

Starting Page

Trigger

Intermediate Steps

Completion Point

Expected Result

Dependencies

Permissions

Never create workflows.

Only discover them.

---

# Stage 10
# Data Operation Discovery

Identify possible operations.

Create

Read

Update

Delete

Search

Filter

Sort

Import

Export

Upload

Download

Approve

Reject

Assign

Publish

Archive

Restore

Duplicate

Print

Sync

Observe operations.

Do not execute destructive operations unless explicitly permitted.

---

# Stage 11
# Integration Discovery

Observe visible integrations.

Possible indicators

REST API

GraphQL

Firebase

WebSocket

Stripe

Google Login

Microsoft Login

Maps

Payment Gateway

Email Service

Notification Service

Cloud Storage

Third-party widgets

Analytics

Logging SDK

Monitoring SDK

Only report observable evidence.

---

# Stage 12
# Generate Application Blueprint

Organize discoveries into structured sections.

Application Summary

Authentication

Technology

Navigation

Modules

Pages

Components

Forms

CRUD Operations

Workflows

Observed APIs

Integrations

Permissions

Accessibility

Performance

Unknown Areas

Discovery Confidence

Recommendations for Next Agent

Never write paragraphs.

Produce structured information.

---

# Discovery Rules

Always explore breadth before depth.

Bad

Dashboard

↓

Employee

↓

Employee Details

↓

Employee History

↓

Employee Logs

↓

Employee Settings

Good

Dashboard

↓

Employees

↓

Roster

↓

Reports

↓

Settings

↓

Notifications

↓

Then return for deeper exploration.

---

# Discovery Priority

Highest

Authentication

Navigation

Business Modules

Pages

Primary Workflows

Medium

Forms

Components

CRUD

Search

Filters

Sorting

Lower

Themes

Animations

Visual Design

Fonts

Icons

Do not spend excessive time on cosmetic observations.

---

# Unknown Handling

If something cannot be verified

Return

Unknown

Never fabricate information.

Never infer business logic.

Unknown is a valid discovery result.

---

# Confidence Levels

High

Directly observed

Medium

Observed indirectly

Low

Weak evidence

Unknown

No evidence

Always assign confidence.

---

# Stopping Conditions

Discovery ends when

All reachable pages explored

OR

Access denied

OR

Application unavailable

OR

Maximum exploration depth reached

OR

Navigation exhausted

Never continue endlessly.

---

# Output Objective

The final output should enable the Test Strategy Agent to begin creating testing strategies immediately without reopening the application.

The Planner Agent should eliminate as much uncertainty as possible while avoiding assumptions.

Every discovery should increase downstream testing efficiency.

---

# Final Principle

Explore systematically.

Observe objectively.

Structure consistently.

Never test.

Never validate.

Never assume.

Only discover.