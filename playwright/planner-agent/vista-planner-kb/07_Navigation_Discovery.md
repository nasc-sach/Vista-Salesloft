# Knowledge Base 07
# Navigation Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to discover, understand, classify, and document application navigation.

Navigation represents the architectural structure of the application.

Every navigation element may expose one or more business modules.

Your responsibility is to understand how users move through the application.

Never assume hidden navigation exists.

Never fabricate routes.

Only document observable navigation.

---

# Objective

Discover

Navigation Model

Navigation Hierarchy

Navigation Components

Navigation Relationships

Navigation Entry Points

Navigation Exit Points

Protected Navigation

Dynamic Navigation

Navigation Dependencies

Produce a complete navigation blueprint.

---

# Navigation Philosophy

Navigation is not a menu.

Navigation is the complete system that allows users to move between application capabilities.

Every application has navigation.

Navigation may be

Visible

Hidden

Dynamic

Conditional

Role Based

Contextual

Discover every observable navigation path.

---

# Navigation Discovery Lifecycle

Identify Navigation

↓

Classify Navigation

↓

Map Hierarchy

↓

Identify Modules

↓

Identify Relationships

↓

Identify Restrictions

↓

Generate Navigation Tree

Never reverse this order.

---

# Navigation Types

Applications may contain one or more navigation systems.

Top Navigation

Side Navigation

Bottom Navigation

Hamburger Menu

Drawer

Floating Navigation

Context Menu

Profile Menu

Settings Menu

Breadcrumb

Wizard Navigation

Tabs

Accordion

Mega Menu

Tree Navigation

Card Navigation

Dashboard Navigation

Quick Links

Search Navigation

Shortcut Navigation

Command Palette

Record every observed navigation type.

---

# Navigation Entry Points

Determine where navigation begins.

Examples

Landing Page

Dashboard

Login

Home

Sidebar

Top Bar

Profile

Search

Quick Actions

Record every entry point.

---

# Navigation Components

Observe

Navigation Bar

Sidebar

Menu Items

Dropdown Menus

Nested Menus

Breadcrumbs

Tabs

Drawer

Accordion

Cards

Tiles

Links

Buttons

Floating Buttons

Icons

Search

Profile Menu

Notifications

Settings

Help

Support

Logout

Language Selector

Theme Toggle

Every component should be documented.

---

# Navigation Hierarchy

Navigation should always be represented hierarchically.

Example

Dashboard

    Employees

        Employee List

        Employee Details

        Attendance

        Shift History

    Roster

        Weekly

        Monthly

        Holiday Planner

    Reports

        Daily

        Weekly

        Monthly

Flattening hierarchy loses valuable architectural information.

Always preserve parent-child relationships.

---

# Module Discovery

Each primary navigation item usually represents a business module.

Examples

Dashboard

Employees

Roster

Attendance

Approvals

Tasks

Reports

Settings

Notifications

Administration

Calendar

Analytics

Billing

Projects

AI Assistant

Do not rename modules.

Use names visible in the application.

---

# Primary Navigation

Primary navigation usually represents the highest business level.

Examples

Dashboard

Projects

Employees

Reports

Settings

These should be treated as top-level modules.

---

# Secondary Navigation

Secondary navigation exists inside modules.

Example

Employees

↓

Employee List

Departments

Attendance

Shift Assignment

History

Secondary navigation should remain attached to its parent module.

---

# Tertiary Navigation

Some enterprise applications contain deeply nested navigation.

Example

Projects

↓

Project A

↓

Sprint

↓

Task

↓

Subtask

↓

Comments

Record full navigation depth.

---

# Breadcrumb Discovery

Observe

Home

>

Employees

>

Attendance

>

Shift Details

Breadcrumbs reveal page hierarchy.

Always record breadcrumb structure.

---

# Tab Navigation

Tabs often separate logical features.

Examples

General

Details

History

Audit

Attachments

Permissions

Settings

Tabs should never be treated as separate modules unless navigation changes.

---

# Accordion Navigation

Observe

Expandable Sections

Collapsible Sections

Nested Lists

Panel Navigation

Document hierarchy.

---

# Card Navigation

Modern dashboards often use cards as navigation.

Examples

Employee Management

Roster Planner

Analytics

Leave Requests

Card navigation is equivalent to menu navigation.

---

# Search Navigation

Search can also become navigation.

Examples

Global Search

Command Search

Quick Search

Search Results

Autocomplete

Record search-driven navigation.

---

# Context Navigation

Some navigation appears only after interaction.

Examples

Three Dot Menu

Right Click Menu

Overflow Menu

Hover Menu

Profile Menu

Explore context menus only once.

Avoid duplicate exploration.

---

# Role-Based Navigation

Navigation may change depending on user permissions.

Observe

Hidden Menus

Disabled Menus

Read-only Menus

Administrator Menus

Manager Menus

Employee Menus

Guest Menus

Never infer missing roles.

Document visible evidence only.

---

# Dynamic Navigation

Some menus appear only after

Selecting a record

Opening a dialog

Hovering

Expanding a tree

Changing a tab

Completing authentication

Document trigger conditions.

---

# Navigation Relationships

Determine

Parent Page

Child Page

Sibling Page

Related Page

Cross Navigation

Navigation Loop

These relationships help downstream workflow generation.

---

# Navigation Direction

Observe

Forward Navigation

Backward Navigation

Home Navigation

Cancel Navigation

Breadcrumb Navigation

Redirect Navigation

Modal Navigation

Drawer Navigation

Document transition direction.

---

# Navigation Triggers

Navigation may occur through

Menu

Button

Link

Card

Row Click

Table Action

Floating Button

Wizard

Shortcut

Keyboard

Search Result

Record trigger type.

---

# Navigation Restrictions

Observe

Authentication Required

Permission Required

Disabled Menu

Hidden Option

Unavailable Route

Maintenance Mode

Document observable restrictions.

---

# Duplicate Navigation

Multiple navigation paths may reach the same page.

Example

Dashboard

↓

Employees

OR

Global Search

↓

Employee Details

Record every observed path.

Do not merge navigation paths.

---

# Navigation Confidence

High

Direct observation.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

Always assign confidence.

---

# Unknown Navigation

If navigation cannot be determined

Return

Unknown

Never fabricate routes.

Never guess hidden pages.

---

# Navigation Completion

Navigation discovery is complete when

No unexplored menus remain.

No unexplored tabs remain.

No unexplored drawers remain.

No unexplored context menus remain.

No additional reachable pages remain.

OR

Access restrictions prevent further exploration.

---

# Output

Generate

Navigation Model

Navigation Hierarchy

Modules

Parent Child Relationships

Entry Points

Exit Points

Navigation Components

Role Restrictions

Dynamic Navigation

Duplicate Paths

Unknown Areas

Confidence

---

# Success Criteria

Another AI agent should be able to reconstruct the application's navigation hierarchy without reopening the application.

The generated navigation model should represent the logical structure of the application rather than a flat list of pages.

---

# Final Principle

Navigation is the architectural skeleton of the application.

Discover every path.

Preserve every relationship.

Never flatten hierarchy.

Never invent hidden routes.

Observe.

Map.

Structure.

Deliver.