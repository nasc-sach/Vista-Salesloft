# Knowledge Base 12
# Dialog and Overlay Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to discover, classify, understand, and document dialogs, overlays, drawers, sheets, popups, and temporary interaction surfaces within an application.

Dialogs are not pages.

Dialogs represent temporary interaction spaces used to complete business operations without changing application context.

Your responsibility is to identify these interactions and document their observable behavior.

Never infer hidden functionality.

Never assume modal behavior.

Only document observable evidence.

---

# Objective

Discover

Overlay Type

Business Purpose

Trigger

Lifecycle

Components

Actions

Navigation Impact

Relationship to Parent Page

Generate a structured Overlay Blueprint.

---

# Overlay Philosophy

An overlay temporarily interrupts or extends the current page.

Unlike pages,

overlays

• appear

• collect information

• perform actions

• disappear

The user remains within the same workflow.

---

# Overlay Lifecycle

Trigger

↓

Overlay Appears

↓

User Interaction

↓

Validation

↓

Confirmation

↓

Completion

↓

Overlay Closes

↓

Parent Page Updates

Observe every stage.

---

# Overlay Categories

Every overlay belongs to one primary category.

Dialog

Modal

Drawer

Side Sheet

Bottom Sheet

Popover

Tooltip

Context Menu

Dropdown Panel

Floating Panel

Lightbox

Confirmation Dialog

Wizard Dialog

Fullscreen Dialog

Overlay Window

Unknown

Assign only one primary category.

---

# Dialog Discovery

Observe

Title

Description

Body

Footer

Primary Action

Secondary Action

Close Button

Escape Support

Outside Click Behavior

Size

Position

Document observable behavior.

---

# Modal Discovery

Determine

Blocking

Non-Blocking

Dismissible

Persistent

Centered

Fullscreen

Scrollable

Nested

Modal Stack

Unknown

---

# Drawer Discovery

Observe

Left Drawer

Right Drawer

Bottom Drawer

Persistent Drawer

Temporary Drawer

Mini Drawer

Overlay Drawer

Width

Resizable

Closable

---

# Side Sheet Discovery

Observe

Appearance

Width

Entry Animation

Dismiss Action

Contained Components

Primary Actions

Navigation Impact

---

# Bottom Sheet Discovery

Common in responsive applications.

Observe

Expanded

Collapsed

Draggable

Scrollable

Action Buttons

Dismiss

---

# Popover Discovery

Observe

Trigger

Anchor Component

Displayed Information

Dismiss Trigger

Actions

Nested Components

---

# Tooltip Discovery

Observe

Trigger

Hover

Focus

Click

Displayed Information

Delay

Dismiss

Do not spend excessive exploration time.

---

# Context Menu Discovery

Observe

Trigger

Right Click

Three Dot Menu

Overflow

Available Actions

Role Restrictions

Nested Menus

---

# Dropdown Panel Discovery

Observe

Trigger

Displayed Options

Grouping

Search

Multi Select

Lazy Loading

Scrolling

---

# Confirmation Dialogs

Common examples

Delete

Archive

Deactivate

Publish

Submit

Approve

Reject

Logout

Observe

Confirmation Message

Buttons

Warning

Icons

Cancellation

---

# Wizard Dialogs

Observe

Step Count

Navigation

Previous

Next

Finish

Validation

Review

Confirmation

---

# Fullscreen Dialogs

Observe

Toolbar

Navigation

Close

Sections

Actions

Embedded Forms

---

# Overlay Triggers

Observe

Button

Icon

Card

Menu

Table Action

Keyboard Shortcut

Floating Button

Context Menu

System Event

Notification

Record trigger source.

---

# Overlay Components

Document

Forms

Buttons

Inputs

Tables

Lists

Cards

Tabs

Accordions

Date Pickers

Uploads

Search

Filters

Charts

Progress

Everything inside the overlay.

---

# Overlay Actions

Observe

Save

Submit

Cancel

Close

Delete

Archive

Approve

Reject

Assign

Upload

Download

Import

Export

Reset

Retry

Generate

Every action should be documented.

---

# Overlay States

Observe

Hidden

Opening

Visible

Loading

Validation

Submitting

Success

Failure

Closing

Closed

Unknown

---

# Overlay Navigation

Determine

Parent Page

Opening Trigger

Navigation Block

Return Destination

Refresh Behavior

Focus Return

---

# Overlay Relationships

Every overlay belongs to

Application

↓

Module

↓

Page

↓

Trigger Component

↓

Overlay

↓

Contained Components

↓

Actions

Preserve relationships.

---

# Nested Overlays

Some applications display overlays inside overlays.

Example

Employee List

↓

Edit Drawer

↓

Assign Department Dialog

↓

Confirmation Dialog

Record complete hierarchy.

---

# Overlay Validation

Observe

Inline Errors

Warnings

Success Messages

Required Fields

Confirmation

Progress

Do not intentionally trigger validation.

---

# Accessibility

Observe

Focus Trap

Keyboard Navigation

Escape Support

Close Button

ARIA Dialog

Accessible Labels

Initial Focus

Focus Return

Only observe.

Do not validate.

---

# Responsive Behavior

Observe

Desktop

Tablet

Mobile

Fullscreen

Drawer Conversion

Bottom Sheet Conversion

Different Layout

Record only visible behavior.

---

# Permission Indicators

Observe

Disabled Actions

Hidden Buttons

Restricted Dialog

Access Denied

Read Only Overlay

Unknown

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

Assign confidence.

---

# Unknown Overlay

If purpose cannot be determined

Category

Unknown

Never invent behavior.

---

# Output

Generate

Overlay Name

Overlay Category

Business Purpose

Parent Page

Trigger

Contained Components

Actions

States

Navigation Impact

Accessibility Indicators

Responsive Behavior

Permission Indicators

Relationships

Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not classify dialogs as pages.

Do not ignore temporary overlays.

Do not merge drawers with pages.

Do not assume confirmation dialogs always delete data.

Do not ignore nested overlays.

Do not flatten overlay hierarchy.

---

# Success Criteria

The downstream Test Strategy Agent should understand

every temporary interaction surface,

its purpose,

its relationship to workflows,

its available actions,

and its navigation impact,

without reopening the application.

---

# Final Principle

Not every business interaction happens on a page.

Many critical operations happen inside temporary interfaces.

Treat overlays as first-class application components.

Observe.

Classify.

Relate.

Document.

Never assume.