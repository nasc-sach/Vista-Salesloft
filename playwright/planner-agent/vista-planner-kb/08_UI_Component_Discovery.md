# Knowledge Base 08
# UI Component Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to identify, classify, understand, and document user interface components within an application.

A component is the smallest reusable interactive or visual building block of the application.

Components represent how users interact with business functionality.

The objective is to identify components and their observable behavior.

Never infer business logic.

Never inspect source code.

Never assume implementation.

Only document observable evidence.

---

# Objective

Discover

Component Type

Component Purpose

Component State

Component Relationships

Component Actions

Component Visibility

Component Hierarchy

Component Accessibility

Component Confidence

Produce a structured UI component inventory.

---

# Component Philosophy

Applications are collections of reusable UI components.

Pages do not contain business logic directly.

Pages organize components.

Components create workflows.

Components create interactions.

Always discover components individually.

---

# Discovery Lifecycle

Locate Component

↓

Identify Component Type

↓

Determine Purpose

↓

Determine State

↓

Determine Relationships

↓

Determine Available Actions

↓

Determine Accessibility

↓

Generate Component Metadata

---

# Component Categories

Every discovered component belongs to one primary category.

Navigation Component

Input Component

Selection Component

Display Component

Action Component

Feedback Component

Container Component

Visualization Component

Media Component

Utility Component

Unknown

Never assign multiple primary categories.

---

# Navigation Components

Examples

Navigation Bar

Sidebar

Drawer

Tabs

Breadcrumb

Tree

Accordion Menu

Floating Navigation

Command Palette

Profile Menu

Settings Menu

Quick Links

Pagination

Record

Purpose

Trigger

Hierarchy

Navigation Destination

---

# Input Components

Examples

Text Input

Password

Email

Phone

Number

Textarea

Rich Text Editor

Search

OTP

URL

Hidden Input

Masked Input

Color Picker

Slider

Code Editor

Observe

Placeholder

Required

Read Only

Disabled

Validation

---

# Selection Components

Examples

Dropdown

Multi Select

Checkbox

Radio Button

Toggle

Switch

Date Picker

Time Picker

Date Range Picker

Calendar

Autocomplete

Lookup

Tree Select

Chip Selector

Tag Selector

Observe

Selection Type

Default Value

Available Options

Dependency

---

# Action Components

Examples

Button

Icon Button

Floating Action Button

Split Button

Dropdown Action

Hyperlink

Card Action

Toolbar Action

Context Menu Action

Observe

Action Label

Enabled

Disabled

Loading

Confirmation

Navigation

Submission

---

# Display Components

Examples

Card

Panel

List

Table

Data Grid

Tile

Badge

Avatar

Chip

Tag

Label

Description

Timeline

Observe

Displayed Data

Grouping

Sorting

Filtering

Layout

---

# Feedback Components

Examples

Toast

Snackbar

Alert

Banner

Inline Validation

Tooltip

Loading Spinner

Skeleton

Progress Bar

Success Message

Error Message

Information Message

Warning Message

Confirmation Dialog

Observe

Trigger

Duration

Dismissible

Severity

---

# Container Components

Examples

Modal

Dialog

Drawer

Accordion

Tabs

Wizard

Stepper

Collapse

Expandable Panel

Side Sheet

Container components organize other components.

Record parent-child relationships.

---

# Visualization Components

Examples

Bar Chart

Line Chart

Pie Chart

Area Chart

Heatmap

Gauge

Radar Chart

Scatter Plot

Histogram

Tree Map

Organization Chart

Kanban

Calendar

Scheduler

Timeline

Observe

Visualization Type

Interactivity

Filters

Legends

Drill-down

---

# Media Components

Examples

Image

Video

Audio

PDF Viewer

Document Viewer

Carousel

Gallery

Observe

Preview

Download

Zoom

Fullscreen

---

# Utility Components

Examples

Divider

Spacer

Separator

Icon

Logo

Branding

Theme Switch

Language Switch

Help

Support

These components rarely contain business functionality.

---

# Unknown Components

If the component cannot be identified

Category

Unknown

Confidence

Unknown

Never invent component types.

---

# Component States

Every component may exist in one or more observable states.

Visible

Hidden

Disabled

Enabled

Focused

Selected

Hovered

Expanded

Collapsed

Loading

Read Only

Editable

Required

Optional

Empty

Populated

Unknown

Document observed states only.

---

# Component Relationships

Every component exists within a hierarchy.

Application

↓

Page

↓

Section

↓

Container

↓

Component

↓

Child Component

Preserve hierarchy.

Never flatten components.

---

# Buttons

Observe

Label

Icon

Style

Position

Primary

Secondary

Danger

Success

Disabled

Loading

Navigation

Submission

Confirmation

Record

Purpose

Trigger

Result

---

# Tables

Observe

Columns

Rows

Sorting

Filtering

Pagination

Selection

Bulk Actions

Expandable Rows

Inline Editing

Export

Search

Actions

Tables often indicate CRUD functionality.

---

# Data Grids

Enterprise applications commonly use

AG Grid

MUI Data Grid

PrimeReact DataTable

Handsontable

TanStack Table

Observe

Virtual Scrolling

Grouping

Column Resize

Column Reorder

Pinning

Aggregation

Filtering

Selection

---

# Forms

Observe

Field Count

Required Fields

Validation

Sections

Groups

Dynamic Fields

Submit

Reset

Cancel

Draft

Save

Do not submit forms unless required for discovery.

---

# Search Components

Observe

Global Search

Local Search

Autocomplete

Suggestions

Recent Searches

Live Search

Advanced Search

Search Scope

Placeholder

---

# Filter Components

Observe

Status Filter

Date Filter

Role Filter

Category Filter

Checkbox Filter

Multi Select

Range Filter

Tag Filter

Advanced Filter

Reset

Apply

---

# Calendar Components

Observe

Daily View

Weekly View

Monthly View

Agenda

Timeline

Scheduling

Availability

Drag and Drop

Events

Appointments

---

# Scheduler Components

Observe

Timeline

Resource Allocation

Shift Planning

Task Assignment

Roster

Availability

Drag and Drop

Calendar Integration

This component is common in workforce applications.

---

# Upload Components

Observe

Browse

Drag and Drop

Progress

Allowed Types

Preview

Delete

Retry

Multiple Upload

---

# Download Components

Observe

Export

Download

CSV

Excel

PDF

Print

Email

Share

---

# Wizard Components

Observe

Steps

Progress

Back

Next

Finish

Validation

Step Indicators

Branching

---

# Charts

Observe

Interactive

Static

Legend

Tooltip

Zoom

Pan

Filter

Download

Drill Down

---

# Accessibility

Observe

ARIA Labels

Tab Order

Focus Indicator

Keyboard Support

Screen Reader Labels

Accessible Name

Required Indicator

Do not validate WCAG.

Only observe.

---

# Dynamic Components

Observe

Lazy Loaded Components

Infinite Scroll

Virtual Lists

Conditional Rendering

Expandable Sections

Animated Components

Progressive Loading

---

# Duplicate Components

The same component may appear on many pages.

Record each occurrence.

Do not assume identical purpose.

Context determines meaning.

---

# Confidence

High

Direct observation

Medium

Strong evidence

Low

Weak evidence

Unknown

Insufficient evidence

Assign confidence to every discovered component.

---

# Output

Generate

Component Name

Component Category

Parent Container

Parent Page

Purpose

Observed States

Available Actions

Accessibility Indicators

Relationships

Confidence

Unknown Areas

---

# Success Criteria

The Test Strategy Agent should understand

every interactive element available to the user,

its purpose,

its relationships,

and how users interact with it,

without reopening the application.

---

# Final Principle

Applications are built from components.

Understand the components,

and the application becomes understandable.

Observe.

Classify.

Relate.

Document.

Never assume.