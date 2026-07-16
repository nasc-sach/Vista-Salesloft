# Knowledge Base 05
# Page Classification

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to classify every discovered page according to its purpose within the application.

Correct page classification enables downstream agents to generate more accurate testing strategies.

A page should never be treated as simply another URL.

Every page serves a business purpose.

Your responsibility is to determine that purpose.

---

# Objective

For every discovered page determine

• Page Category

• Business Purpose

• Primary User

• Navigation Source

• Entry Point

• Exit Point

• Importance

• Confidence

---

# Classification Philosophy

Pages should be classified according to behavior.

Never classify using visual appearance.

Never classify using page title alone.

Always observe

Purpose

User interaction

Primary action

Navigation

Available controls

Workflow position

---

# Primary Categories

Every page belongs to one primary category.

Dashboard

Authentication

CRUD List

CRUD Create

CRUD Update

CRUD View

CRUD Delete

Reports

Analytics

Configuration

Administration

Workflow

Approval

Search

Notification

Help

Profile

Settings

Landing

Error

Maintenance

Utility

Unknown

Only assign one primary category.

---

# Dashboard Pages

Purpose

Provide summary information.

Common indicators

Cards

Charts

KPIs

Statistics

Widgets

Recent Activity

Quick Actions

Notifications

Shortcuts

Dashboard pages usually become workflow entry points.

---

# Authentication Pages

Examples

Login

Logout

Register

Forgot Password

Reset Password

OTP

SSO

MFA

Password Expired

Session Expired

Access Denied

Authentication pages should never be classified as Forms.

---

# CRUD List Pages

Purpose

Display business records.

Indicators

Table

Cards

Grid

Search

Filters

Pagination

Bulk Actions

Sorting

Export

Selection

Row Actions

Examples

Employees

Customers

Products

Orders

Projects

Roster

Shifts

---

# CRUD Create Pages

Purpose

Create new records.

Indicators

Save

Create

Submit

Add

Register

New

Wizard

Form

Required Fields

---

# CRUD Update Pages

Purpose

Modify existing records.

Indicators

Edit

Update

Save Changes

Existing Values

Editable Form

Version Information

---

# CRUD View Pages

Purpose

Display record information.

Indicators

Read Only

Summary

Timeline

History

Attachments

Audit

Profile

Details

---

# CRUD Delete

Usually appears as

Confirmation Dialog

Delete Button

Archive

Deactivate

Remove

Trash

Do not classify an entire page as Delete unless it is dedicated to deletion.

Delete normally belongs to another page.

---

# Configuration Pages

Purpose

Manage system configuration.

Examples

General Settings

Notification Settings

Email Configuration

Business Rules

Regional Settings

Language

Theme

Time Zone

Configuration pages rarely contain business data.

---

# Administration Pages

Purpose

Manage the application.

Examples

Roles

Permissions

Users

Audit Logs

Organizations

Feature Flags

Integrations

System Status

---

# Report Pages

Purpose

Present historical information.

Indicators

Charts

Tables

Export

Date Range

Filters

PDF

CSV

Excel

Print

Reports usually have few editing capabilities.

---

# Analytics Pages

Purpose

Present trends.

Indicators

Charts

KPIs

Heatmaps

Forecast

Comparison

Growth

Distribution

Analytics differs from reports.

Reports present facts.

Analytics presents insights.

---

# Workflow Pages

Purpose

Guide users through a business process.

Indicators

Next

Previous

Step

Wizard

Progress

Timeline

Review

Confirmation

Approval

Workflow pages are highly important.

---

# Approval Pages

Indicators

Approve

Reject

Review

Comment

Pending

History

Decision

Approval Queue

These pages usually contain business-critical workflows.

---

# Search Pages

Purpose

Locate information.

Indicators

Global Search

Advanced Search

Filters

Suggestions

Autocomplete

Recent Searches

Search Results

---

# Notification Pages

Examples

Inbox

Alerts

Announcements

Tasks

Messages

Warnings

Activity Feed

---

# Help Pages

Examples

Documentation

FAQ

Support

Tutorial

Contact

Knowledge Base

Chatbot

---

# Profile Pages

Purpose

Manage current user.

Indicators

Avatar

Personal Information

Password

Preferences

Sessions

Devices

---

# Settings Pages

Purpose

Manage user preferences.

Examples

Theme

Language

Timezone

Notifications

Accessibility

---

# Landing Pages

Usually appear before login.

Indicators

Marketing

Pricing

Features

Contact

Documentation

Get Started

---

# Error Pages

Examples

404

403

500

Maintenance

Session Expired

Access Denied

Network Error

Offline

---

# Utility Pages

Examples

Import

Export

Upload

Download

Redirect

Loading

Initialization

Migration

These support workflows but rarely contain business logic.

---

# Unknown Pages

If purpose cannot be determined

Category

Unknown

Never invent categories.

---

# Classification Priority

Business Purpose

↓

User Goal

↓

Primary Interaction

↓

Navigation

↓

Visible Controls

↓

Page Title

The title alone should never determine classification.

---

# Multiple Purposes

Some pages perform multiple functions.

Example

Employee List

Search

Filter

Export

Create

Edit

Delete

Primary Category

CRUD List

Secondary Capabilities

Search

Filter

Export

Create

Edit

Delete

Never create multiple primary categories.

---

# Importance Levels

Critical

Application cannot function without page.

High

Major business functionality.

Medium

Supporting business functionality.

Low

Convenience functionality.

Informational

Read-only.

Unknown

Unable to determine.

---

# Workflow Position

Record

Entry Page

Intermediate Page

Final Page

Standalone Page

Supporting Page

---

# Business Criticality

Determine whether the page affects

Revenue

Operations

Compliance

Security

Administration

Reporting

Communication

Scheduling

Unknown

Do not infer.

Use visible evidence.

---

# Confidence

High

Observed directly.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

---

# Output

Each page should produce

Page Name

Category

Business Purpose

Parent Module

Primary Actions

Secondary Actions

Importance

Workflow Position

Confidence

---

# Success Criteria

Another AI agent should understand

what every page exists for

without reopening the application.

---

# Final Principle

Every page exists to solve a business problem.

Your responsibility is to identify that business purpose accurately.

Never classify by appearance.

Always classify by purpose.