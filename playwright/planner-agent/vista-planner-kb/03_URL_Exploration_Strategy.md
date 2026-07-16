# Knowledge Base 03
# URL Exploration Strategy

---

# Purpose

This document defines the exploration strategy that the Application Discovery Planner Agent must use when starting from a single Frontend URL.

The objective is to maximize application understanding while minimizing unnecessary navigation, duplicate exploration, and missed features.

Every application, regardless of technology stack, should be explored using this strategy.

---

# Objective

Starting from

Frontend URL

discover

• Application Entry Point

• Authentication

• Navigation

• Business Modules

• Pages

• Workflows

• UI Components

• Forms

• CRUD Operations

• Observable APIs

• Technology Indicators

The agent should gradually build an Application Blueprint.

---

# Exploration Principles

Always explore safely.

Never perform destructive actions.

Never intentionally modify production data.

Never attempt privilege escalation.

Never brute force authentication.

Never execute unknown operations.

Observe first.

Interact only when necessary.

---

# Exploration Lifecycle

Receive URL

↓

Open Application

↓

Wait for Initial Load

↓

Collect Global Information

↓

Discover Entry Screen

↓

Discover Navigation

↓

Discover Modules

↓

Discover Pages

↓

Discover Workflows

↓

Discover Components

↓

Generate Blueprint

---

# Stage 1
# Initial Page Load

After opening the URL

Collect

Current URL

Final Redirect URL

Page Title

Meta Description

Language

Viewport

Theme

Application Icon

Manifest

Browser Console Status

Loading Time

Loading Indicators

Application Availability

Never interact immediately.

Allow the page to stabilize.

---

# Stage 2
# Detect Initial State

Determine which initial state exists.

Possible states

Login Screen

Dashboard

Landing Page

Splash Screen

Loading Screen

Maintenance Page

Error Page

Unauthorized Screen

Session Expired Screen

Guest Home

Record the detected state.

---

# Stage 3
# Observe Global Layout

Before clicking anything

Understand the page structure.

Identify

Header

Footer

Sidebar

Navigation Drawer

Floating Navigation

Content Area

Widget Area

Notification Area

User Profile

Search Bar

Settings

Help

Breadcrumb

Theme Toggle

Language Switcher

These components usually remain consistent across the application.

---

# Stage 4
# Determine Navigation Strategy

Applications usually expose navigation in one of the following ways.

Top Navigation

Left Sidebar

Bottom Navigation

Drawer

Hamburger Menu

Grid Menu

Card Dashboard

Search Driven

Wizard Driven

Single Page

Tab Based

Module Selector

Discover the navigation model before exploring pages.

---

# Stage 5
# Breadth First Exploration

Always use Breadth First Search (BFS).

Correct

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

Return to Employees

↓

Explore deeper

Wrong

Dashboard

↓

Employees

↓

Employee Details

↓

Employee History

↓

Employee Audit

↓

Employee Timeline

This causes entire modules to be missed.

---

# Stage 6
# Navigation Queue

Maintain an exploration queue.

Every newly discovered page should enter the queue.

Pseudo Example

Queue

Dashboard

Employees

Roster

Reports

Settings

Completed pages should never be revisited unless necessary.

---

# Stage 7
# Page Visit Rules

Every page should be visited only once.

While visiting collect

Page Name

Route

Navigation Source

Parent Module

Visible Components

Primary Actions

Available Forms

Available Tables

Search

Filters

Sorting

Dialogs

Permissions

Workflows

Exit Navigation

Do not repeatedly inspect identical pages.

---

# Stage 8
# Dynamic Navigation

Some navigation appears only after interaction.

Examples

Expand Sidebar

Profile Menu

Context Menu

Accordion

Overflow Menu

Three Dot Menu

Hover Menu

Drawer

Explore dynamic navigation after static navigation.

---

# Stage 9
# Authentication Awareness

If authentication exists

Determine

Login Required

Already Logged In

Session Expired

Access Denied

Permission Restricted

Guest Mode

Only authenticate when credentials are supplied.

Never guess credentials.

Never retry indefinitely.

---

# Stage 10
# Modal Exploration

Applications often hide functionality inside

Dialogs

Side Sheets

Popup Windows

Confirmation Dialogs

Date Pickers

Dropdown Panels

Explore them only if they reveal new information.

Avoid unnecessary repetition.

---

# Stage 11
# Form Exploration

When a form is encountered

Observe

Purpose

Fields

Required Fields

Optional Fields

Buttons

Validation Messages

Autocomplete

Lookup

Uploads

Date Inputs

Dynamic Sections

Never submit forms unless exploration requires it.

---

# Stage 12
# Table Exploration

When a table exists

Observe

Columns

Pagination

Sorting

Filtering

Bulk Actions

Row Actions

Export

Search

Selection

Context Menu

Tables usually indicate CRUD operations.

---

# Stage 13
# Workflow Entry Points

Identify where workflows begin.

Examples

Login

Create

Edit

Delete

Assign

Approve

Reject

Publish

Export

Import

Download

Upload

Schedule

Generate

Do not execute complete workflows.

Only identify entry points.

---

# Stage 14
# Technology Clues

Observe indicators including

React

React Native

Next.js

Vite

Angular

Vue

Material UI

Ant Design

Bootstrap

Tailwind

ShadCN

PrimeReact

Redux

React Router

GraphQL

REST

WebSocket

Service Worker

PWA Manifest

These observations help downstream agents.

---

# Stage 15
# Observable APIs

Observe

XHR

Fetch

GraphQL

REST Calls

WebSocket

Server Events

Do not inspect payload contents beyond what is necessary.

Record

Endpoint

Method

Purpose

Response Type

Frequency

Visibility

---

# Stage 16
# Duplicate Prevention

Before exploring

Check

Has this page already been visited?

Has this workflow already been identified?

Has this navigation already been explored?

Avoid duplicate observations.

---

# Stage 17
# Exploration Depth

Maximum recommended depth

Navigation

Unlimited until exhausted

Workflow

Three interaction levels

Nested Components

Two levels

Dialogs

One level unless new workflows appear

Avoid infinite exploration.

---

# Stage 18
# Handling Unknown Areas

If access is restricted

Record

Restricted Module

Permission Required

Discovery Status

Reason

Confidence

Never fabricate hidden functionality.

---

# Stage 19
# Exploration Completion

Exploration completes when

No new navigation exists

No unexplored pages remain

Maximum depth reached

Session expires

Application unavailable

Exploration interrupted

Always preserve collected discoveries.

---

# Best Practices

Always prefer navigation over guessing routes.

Always prefer visible evidence.

Always discover breadth before depth.

Always classify before summarizing.

Always record confidence.

Always preserve partial discoveries.

Never lose collected information.

---

# Common Mistakes

Do not repeatedly visit the same page.

Do not click every button without purpose.

Do not ignore hidden navigation.

Do not skip authentication discovery.

Do not stop after reaching the dashboard.

Do not assume similar pages behave identically.

Do not infer business workflows.

---

# Success Criteria

The Application Discovery Planner Agent should produce an application blueprint covering

Authentication

Navigation

Modules

Pages

Forms

CRUD Operations

Workflows

Components

Technology Indicators

Observable APIs

Unknown Areas

Discovery Confidence

without requiring another agent to reopen the application merely to understand its structure.

---

# Final Principle

Explore with discipline.

Discover systematically.

Collect evidence.

Avoid assumptions.

Produce reusable knowledge.