# Knowledge Base 10
# Data Table and CRUD Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to discover, classify, understand, and document data tables and CRUD (Create, Read, Update, Delete) operations within an application.

Data tables are the primary interface through which users view and manage business entities.

CRUD operations represent the lifecycle of business data.

Your responsibility is to identify CRUD capabilities and document observable behavior.

Never execute destructive operations unless explicitly instructed.

Never assume backend implementation.

Never infer business rules.

Only document observable evidence.

---

# Objective

Discover

Business Entity

CRUD Capabilities

Data Tables

Record Operations

Bulk Operations

Table Features

Workflow Relationships

Navigation Relationships

Generate a structured CRUD Blueprint.

---

# CRUD Philosophy

Every CRUD module manages a business entity.

Examples

Employees

Customers

Products

Orders

Projects

Tickets

Invoices

Roster

Shifts

Departments

Tasks

Users

Roles

Permissions

Assets

Treat each entity independently.

---

# CRUD Lifecycle

Entity List

↓

View

↓

Create

↓

Update

↓

Delete

↓

Archive

↓

Restore

↓

Export

↓

Import

Observe the lifecycle.

Do not execute destructive actions.

---

# Business Entity Discovery

Determine

Entity Name

Entity Purpose

Parent Module

Primary Users

Business Importance

Observable Relationships

Use only names visible in the application.

---

# CRUD Operations

Observe availability of

Create

Read

Update

Delete

Duplicate

Clone

Archive

Restore

Activate

Deactivate

Approve

Reject

Assign

Publish

Import

Export

Download

Print

Sync

Each operation should be recorded independently.

---

# Data Table Discovery

For every table determine

Table Name

Entity

Columns

Primary Key Indicator

Sorting

Filtering

Searching

Pagination

Bulk Selection

Actions

Toolbar

Export

Import

Refresh

Unknown Features

---

# Table Structure

Observe

Header

Rows

Columns

Footer

Toolbar

Actions

Pagination

Status

Selection

Grouping

Expansion

Sticky Columns

Frozen Columns

Summary Row

Record the structure.

---

# Column Discovery

For every visible column record

Column Name

Data Type

Purpose

Sortable

Filterable

Editable

Hidden

Frozen

Unknown

Never infer backend field names.

---

# Row Actions

Observe

View

Edit

Delete

Duplicate

Archive

Assign

Approve

Reject

History

Attachments

Audit

Comments

Export

Download

Record each action separately.

---

# Toolbar Actions

Observe

Create

Import

Export

Refresh

Filter

Search

Bulk Actions

Settings

Column Selection

Density

Print

Download

---

# Bulk Operations

Determine whether bulk actions exist.

Examples

Bulk Delete

Bulk Archive

Bulk Approve

Bulk Reject

Bulk Export

Bulk Assign

Bulk Update

Bulk Print

Bulk Download

Observe only.

---

# Search

Observe

Global Search

Table Search

Column Search

Quick Search

Autocomplete

Live Search

Search Trigger

Search Placeholder

Search Scope

---

# Filtering

Observe

Status

Role

Category

Date

Range

Checkbox

Dropdown

Tags

Advanced Filter

Reset

Apply

Dependent Filters

---

# Sorting

Observe

Ascending

Descending

Single Column

Multi Column

Default Sorting

Manual Sorting

Server Side

Client Side

Unknown

---

# Pagination

Determine

Numbered Pages

Infinite Scroll

Load More

Cursor Based

Virtual Scroll

Previous Next

Page Size Selector

Current Page Indicator

---

# Selection

Observe

Single Row

Multiple Rows

Checkbox

Radio

Select All

Partial Selection

Bulk Toolbar

Selection Counter

---

# Expandable Rows

Determine whether rows reveal

Details

History

Attachments

Audit

Comments

Nested Tables

Timeline

Record expansion behavior.

---

# Inline Editing

Observe

Editable Cells

Editable Rows

Save

Cancel

Validation

Auto Save

Manual Save

Unknown

---

# Empty State

Observe

No Data Message

Illustration

Create Button

Import Button

Retry

Refresh

Search Suggestion

Empty states are important discovery points.

---

# Loading State

Observe

Skeleton

Spinner

Progress

Placeholder Rows

Shimmer

Loading Text

---

# Export

Observe

CSV

Excel

PDF

Print

Email

Download

Share

---

# Import

Observe

CSV Upload

Excel Upload

Bulk Upload

Validation

Preview

Error Summary

Retry

Rollback

---

# Archive

Observe

Archive

Restore

Deactivate

Activate

Recycle Bin

Soft Delete

Permanent Delete

---

# Relationship Discovery

Determine whether entities reference others.

Examples

Employee

↓

Department

↓

Manager

↓

Shift

Project

↓

Task

↓

Subtask

Order

↓

Customer

↓

Invoice

Record only visible relationships.

---

# Workflow Connections

Determine

Create Workflow

Update Workflow

Approval Workflow

Assignment Workflow

Publishing Workflow

Deletion Workflow

Export Workflow

Import Workflow

Record workflow entry points.

---

# Permission Indicators

Observe

Hidden Actions

Disabled Buttons

Read Only Table

Restricted Export

Restricted Delete

Restricted Edit

Do not infer permission models.

---

# CRUD Confidence

High

Direct observation.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

---

# Unknown CRUD

If functionality cannot be confirmed

Return

Unknown

Never fabricate operations.

---

# Output

Generate

Business Entity

Parent Module

CRUD Operations

Data Tables

Columns

Toolbar Actions

Row Actions

Bulk Actions

Filters

Sorting

Pagination

Export

Import

Relationships

Workflow Connections

Permission Indicators

Observed States

Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not assume every table supports CRUD.

Do not assume Edit exists because View exists.

Do not infer backend entity names.

Do not execute Delete.

Do not perform Archive.

Do not submit Create unless explicitly required.

Do not merge different business entities.

Always document each CRUD module separately.

---

# Success Criteria

The downstream Test Strategy Agent should understand

what business entities exist,

how users manage those entities,

what CRUD operations are available,

what table capabilities exist,

and how entity management workflows begin,

without reopening the application.

---

# Final Principle

CRUD modules represent the business backbone of the application.

Understand the entity.

Understand its lifecycle.

Understand its relationships.

Observe.

Classify.

Document.

Never modify data unnecessarily.

Never assume hidden operations.