# Knowledge Base 04
# React Web Architecture Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to recognize, understand, and explore applications built using React.

The objective is not to identify every implementation detail.

The objective is to understand React application behavior well enough to create an accurate Application Blueprint.

This document applies only to React Web Applications.

React Native applications are covered separately.

---

# Primary Objective

When a React application is detected, the agent should understand

• Application structure

• Navigation model

• Component hierarchy

• Rendering behavior

• Forms

• CRUD modules

• State indicators

• Routing

• Lazy loading

• Dynamic rendering

without making implementation assumptions.

---

# React Philosophy

React applications are component-driven.

A page is not a single document.

A page is a hierarchy of reusable components.

The same component may appear across multiple pages.

Never assume identical components represent different functionality.

Likewise, never assume visually different components have different purposes.

Always observe behavior.

---

# Typical React Application Structure

A React application generally contains

Application Shell

↓

Router

↓

Layout

↓

Page

↓

Sections

↓

Reusable Components

↓

UI Elements

Discovery should follow this hierarchy.

---

# Application Shell

The Application Shell is normally persistent.

Examples

Navigation Bar

Sidebar

Footer

Notifications

Theme Switcher

Profile Menu

Search

Language Selector

These rarely change during navigation.

Identify them first.

---

# Page Structure

Most pages consist of

Header

↓

Toolbar

↓

Filters

↓

Content

↓

Pagination

↓

Footer

Observe the role of each section.

---

# React Routing

React commonly uses client-side routing.

Typical libraries

React Router

TanStack Router

Next.js Router

Remix Router

Hash Router

Observe

Route changes

URL updates

History behavior

Navigation transitions

Nested routes

Dynamic routes

Protected routes

Unknown routes

404 pages

Do not infer routes.

Record only observed routes.

---

# Common Route Patterns

Examples

/dashboard

/login

/users

/users/create

/users/edit

/users/{id}

/reports

/settings

/profile

/admin

Do not manually construct routes.

Only record reachable routes.

---

# Nested Routes

React applications frequently use nested routing.

Example

Dashboard

↓

Employees

↓

Employee Details

↓

Attendance

↓

Shift History

Record hierarchy.

Do not flatten nested routes.

---

# Protected Routes

Some routes require authentication.

Indicators include

Redirect to Login

403

401

Access Denied

Permission Dialog

Record

Protected Route

Required Authentication

Permission Indicator

---

# Dynamic Routes

Dynamic routes contain parameters.

Examples

/employee/102

/order/ABC123

/project/77

Do not assume parameter meaning.

Record

Route Template

Observed Example

Confidence

---

# Component Philosophy

Every page is composed of reusable components.

Examples

Button

Card

Modal

Dialog

Table

Accordion

Tabs

Tree

Sidebar

Drawer

Form

Chart

Timeline

Calendar

List

Toast

Snackbar

Components should be identified individually.

---

# Component Classification

Components should be grouped.

Navigation Components

Display Components

Input Components

Layout Components

Feedback Components

Visualization Components

Action Components

Utility Components

This classification assists downstream testing.

---

# Material UI Indicators

Observe indicators

MuiButton

MuiDialog

MuiTable

MuiGrid

MuiCard

MuiTextField

MuiAutocomplete

MuiSelect

MuiDrawer

MuiTabs

MuiSnackbar

MuiTooltip

Presence suggests Material UI.

Do not guarantee implementation.

---

# Ant Design Indicators

Observe

ant-btn

ant-table

ant-form

ant-select

ant-modal

ant-drawer

ant-tabs

ant-card

ant-tree

ant-layout

Record evidence.

---

# Tailwind Indicators

Possible clues

Utility classes

flex

grid

gap

justify-

items-

rounded

shadow

text-

bg-

p-

m-

Tailwind is a styling framework.

It does not define functionality.

---

# ShadCN Indicators

Observe

Popover

Command

Sheet

Dialog

AlertDialog

DropdownMenu

ContextMenu

HoverCard

Toast

NavigationMenu

Tabs

Accordion

Presence indicates ShadCN patterns.

---

# PrimeReact Indicators

Possible components

DataTable

TreeTable

Calendar

Dropdown

Dialog

OverlayPanel

Sidebar

Accordion

PanelMenu

Stepper

Tree

OrganizationChart

---

# Dashboard Discovery

Dashboards commonly contain

Cards

Charts

Statistics

Notifications

Recent Activity

Tasks

Quick Actions

KPIs

Shortcuts

Widgets

Treat each widget as an independent discovery target.

---

# Table Discovery

React applications heavily rely on tables.

Observe

Columns

Sorting

Filtering

Pagination

Infinite Scroll

Bulk Selection

Export

Search

Inline Editing

Actions

Expandable Rows

Tables usually represent CRUD modules.

---

# Form Discovery

Observe

Single Step Forms

Multi Step Forms

Dynamic Forms

Conditional Fields

Autocomplete

Dependent Dropdowns

Date Pickers

Time Pickers

Masked Inputs

Uploads

Rich Text Editors

Validation

Do not submit unless necessary.

---

# CRUD Recognition

Typical CRUD indicators

Create Button

Add Button

New Button

Edit Icon

Delete Icon

Duplicate

Clone

Archive

Restore

Export

Import

Approval

Record every operation.

---

# Search Recognition

Search may appear as

Global Search

Local Search

Quick Search

Autocomplete

Filter Search

Advanced Search

Observe

Placeholder

Trigger

Search Scope

Live Search

Delayed Search

---

# Filter Recognition

Observe

Dropdown Filters

Checkbox Filters

Tag Filters

Date Filters

Status Filters

Role Filters

Advanced Filters

Multi Select

Reset

Apply

---

# Pagination Recognition

Common types

Numbered

Infinite Scroll

Load More

Cursor Based

Previous Next

Virtual Scroll

Record pagination type.

---

# Modal Recognition

React commonly uses

Dialog

Drawer

Side Sheet

Confirmation

Wizard

Overlay

Popup

Record

Trigger

Purpose

Contained Components

---

# Notification Recognition

Observe

Snackbar

Toast

Alert

Banner

Inline Message

Status Badge

Success

Warning

Error

Information

Record trigger when visible.

---

# Loading Recognition

React applications often render

Skeleton

Spinner

Linear Progress

Circular Progress

Placeholder Cards

Shimmer

Loading Text

Observe loading behavior.

---

# Lazy Loading

React often loads components dynamically.

Indicators

Late appearing components

Loading placeholders

Chunk loading

Suspense fallback

Delayed rendering

Record observations.

---

# Infinite Scroll

Observe

Automatic loading

Sentinel loading

Lazy rendering

Virtualized list

Scroll threshold

Do not scroll endlessly.

---

# Error Boundaries

Possible indicators

Unexpected Error

Retry Button

Reload

Crash Message

Fallback Component

React Error Overlay

Record visible evidence.

---

# React Hook Form Indicators

Possible evidence

Field validation

Instant validation

Error messages

Controlled components

Dirty state

Touched state

Observe behavior only.

---

# Accessibility

Observe

ARIA Labels

Keyboard Navigation

Tab Order

Focus Indicator

Accessible Names

Semantic HTML

Do not validate WCAG.

Only observe.

---

# Performance Indicators

Observe

Initial render delay

Lazy loading

Page transition

Skeleton usage

Large table rendering

Virtual scrolling

Do not benchmark.

---

# Common React Mistakes to Avoid

Do not assume components are unique.

Do not infer business logic.

Do not inspect implementation source code.

Do not fabricate routes.

Do not assume state management library.

Do not guess hidden pages.

Observe only.

---

# Discovery Deliverables

Produce structured information for

React Indicators

Observed Routes

Pages

Components

CRUD Modules

Forms

Tables

Navigation

Loading Behavior

Accessibility Indicators

Performance Indicators

Unknown Areas

Confidence

---

# Success Criteria

A downstream Test Strategy Agent should understand

how the React application is organized,

what components exist,

where workflows begin,

what modules exist,

and how users navigate

without reopening the application.

---

# Final Principle

React applications are collections of reusable components.

Discover relationships.

Discover behavior.

Discover hierarchy.

Never discover implementation code.

Never assume functionality.

Observe.

Classify.

Structure.

Deliver.