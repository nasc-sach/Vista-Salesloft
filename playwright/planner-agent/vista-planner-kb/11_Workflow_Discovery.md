# Knowledge Base 11
# Workflow Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to discover, classify, understand, and document business workflows within an application.

A workflow represents a sequence of user interactions that accomplish a business objective.

A workflow is not a page.

A workflow is not a form.

A workflow is not a CRUD operation.

A workflow is a connected journey.

Your responsibility is to identify workflows and document their observable structure.

Never validate workflow correctness.

Never evaluate business rules.

Never infer hidden workflow steps.

Only document observable evidence.

---

# Objective

Discover

Business Workflows

Workflow Entry Points

Workflow Exit Points

Workflow Steps

Workflow Dependencies

Workflow Decisions

Workflow Navigation

Workflow Participants

Workflow Outcomes

Generate a structured Workflow Blueprint.

---

# Workflow Philosophy

Users do not interact with pages.

Users complete workflows.

Examples

Login

↓

Dashboard

↓

Employee Management

↓

Create Employee

↓

Save

↓

Employee List Updated

This entire journey represents one workflow.

Always discover workflows from the user's perspective.

---

# Workflow Discovery Lifecycle

Identify Trigger

↓

Identify Entry Point

↓

Observe User Actions

↓

Observe Navigation

↓

Observe Decisions

↓

Observe Completion

↓

Document Outcome

↓

Generate Workflow Blueprint

---

# Workflow Categories

Every workflow belongs to one primary category.

Authentication

CRUD

Approval

Assignment

Scheduling

Reporting

Configuration

Administration

Notification

Import

Export

Search

Profile Management

Settings

Communication

Unknown

Assign only one primary category.

---

# Workflow Types

Linear

Branching

Conditional

Approval

Multi-Step

Wizard

Background

Parallel

Role-Based

Scheduled

Event-Driven

Unknown

Document observed workflow type.

---

# Workflow Trigger

Determine what starts the workflow.

Examples

Button

Menu

Card

Link

Notification

Table Row

Floating Action Button

Quick Action

Context Menu

Search Result

System Event

Record the observed trigger.

---

# Workflow Entry Point

Determine where the workflow begins.

Examples

Dashboard

Employees

Roster

Reports

Settings

Notification

Search

Profile

Help

Document

Entry Page

Entry Component

Entry Action

---

# Workflow Steps

Every workflow should be documented step-by-step.

Example

Step 1

Navigate to Employee Module

↓

Step 2

Click Create Employee

↓

Step 3

Complete Employee Form

↓

Step 4

Save

↓

Step 5

Employee Appears in List

Do not merge multiple workflows.

---

# Workflow Navigation

Observe navigation between steps.

Record

Source Page

Destination Page

Navigation Trigger

Redirect

Modal

Drawer

Dialog

Wizard

Popup

---

# Workflow Decisions

Some workflows branch.

Examples

Save

↓

Validation Success

↓

Employee Created

OR

Validation Failure

↓

Error Message

Only record observable branches.

Never invent decision logic.

---

# Workflow States

Observe

Started

In Progress

Waiting

Pending

Completed

Cancelled

Rejected

Approved

Failed

Unknown

Document visible states only.

---

# Workflow Participants

Determine who appears to perform the workflow.

Examples

Administrator

Manager

Supervisor

Employee

Approver

Viewer

Guest

Unknown

Only use visible evidence.

---

# Workflow Dependencies

Observe dependencies.

Examples

Login Required

Permission Required

Employee Must Exist

Project Must Exist

Roster Must Exist

Shift Assigned

Approval Required

Never infer backend dependencies.

---

# Workflow Outcomes

Determine observable outcomes.

Examples

Success Message

Redirect

Table Updated

Record Created

Report Generated

Export Downloaded

Notification Appears

Approval Recorded

Unknown

Only document visible outcomes.

---

# Workflow Completion

Determine how users know the workflow has finished.

Examples

Success Toast

Redirect

Confirmation Dialog

Updated Table

Generated File

Dashboard Refresh

Status Update

Loading Completed

---

# Multi-Step Workflows

Observe

Step Indicator

Progress Bar

Wizard

Previous

Next

Review

Confirmation

Finish

Document every visible step.

---

# Approval Workflows

Observe

Pending

Approve

Reject

Comments

History

Status

Reviewer

Decision

Approval workflows are business critical.

---

# Assignment Workflows

Examples

Assign Employee

Assign Shift

Assign Project

Assign Role

Assign Department

Observe assignment process.

---

# Scheduling Workflows

Examples

Create Schedule

Generate Roster

Publish Schedule

Modify Shift

Holiday Assignment

These are especially important for workforce applications.

---

# Import Workflows

Observe

Upload

Preview

Validation

Confirmation

Import Progress

Completion

Rollback

Retry

---

# Export Workflows

Observe

CSV

Excel

PDF

Print

Email

Download

Observe

Trigger

Destination

Completion

---

# Search Workflows

Observe

Search

Results

Selection

Open Record

Return

Filters

Sorting

Reset

---

# Notification Workflows

Observe

Notification Created

Notification Opened

Notification Cleared

Notification Archived

Mark As Read

Dismiss

---

# Error Handling

Observe

Validation Error

Access Denied

Network Failure

Session Expired

Retry

Cancel

Rollback

Only document observed behavior.

---

# Role-Based Workflows

Some workflows differ by role.

Observe

Manager Workflow

Employee Workflow

Administrator Workflow

Guest Workflow

Document only visible differences.

---

# Workflow Relationships

Every workflow belongs to

Application

↓

Module

↓

Page

↓

Component

↓

Workflow

↓

Outcome

Preserve relationships.

---

# Confidence

High

Direct observation.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

Assign confidence to every workflow.

---

# Unknown Workflows

If a workflow cannot be completed

Return

Unknown

Never fabricate missing steps.

Never assume hidden processes.

---

# Output

Generate

Workflow Name

Workflow Category

Workflow Type

Business Purpose

Entry Point

Trigger

Steps

Navigation Flow

Dependencies

Participants

States

Observable Decisions

Observable Outcomes

Completion Indicator

Related Modules

Related Components

Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not confuse a page with a workflow.

Do not merge unrelated workflows.

Do not infer hidden approval chains.

Do not assume success after clicking a button.

Do not create missing workflow steps.

Do not execute destructive workflows.

Always preserve workflow boundaries.

---

# Success Criteria

The downstream Test Strategy Agent should understand

what users are trying to accomplish,

how they accomplish it,

what screens participate,

what decisions occur,

what outcomes are visible,

and where workflows begin and end,

without reopening the application.

---

# Final Principle

Pages organize functionality.

Components enable interaction.

Workflows deliver business value.

Your responsibility is to discover complete business journeys.

Observe.

Connect.

Structure.

Document.

Never assume.