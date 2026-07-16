# Knowledge Base 14
# Performance Observation

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to observe and document visible performance characteristics of an application during exploration.

Performance observation is limited to identifying visible behaviors that may influence downstream testing.

This agent does not execute performance tests.

This agent does not benchmark application speed.

This agent does not calculate performance metrics.

This agent only records observable performance characteristics.

---

# Objective

Observe

Application Startup

Navigation Speed

Rendering Behavior

Loading Indicators

Lazy Loading

Data Loading

UI Responsiveness

Asynchronous Operations

Generate a Performance Observation Blueprint.

---

# Performance Philosophy

Performance observation is passive.

The Planner Agent observes how the application behaves naturally.

It never intentionally stresses the application.

It never generates artificial load.

It never compares timing against requirements.

Only visible observations are recorded.

---

# Observation Lifecycle

Application Starts

↓

Resources Load

↓

UI Renders

↓

User Interaction

↓

Loading

↓

Rendering

↓

Completion

↓

Document Observation

---

# Startup Observation

Observe

Application Launch

Splash Screen

Loading Screen

Initial Render

Progress Indicator

Skeleton

Logo Animation

Startup Messages

Blank Screen

White Screen

Black Screen

Record startup sequence.

---

# Initial Rendering

Observe

Immediate Render

Delayed Render

Progressive Render

Skeleton Loading

Spinner

Placeholder Cards

Incremental Rendering

Blank Sections

Lazy Rendering

---

# Navigation Performance

Observe

Menu Navigation

Page Transition

Tab Switching

Drawer Opening

Dialog Opening

Overlay Rendering

Route Transition

History Navigation

Do not measure milliseconds.

Only record perceived behavior.

---

# Component Rendering

Observe

Cards

Tables

Charts

Calendars

Forms

Lists

Images

Dashboards

Large Components

Virtual Components

Record rendering order.

---

# Data Loading

Observe

Loading Spinner

Skeleton

Placeholder

Loading Text

Progress Bar

Partial Loading

Complete Loading

No Indicator

Record user-visible behavior.

---

# Lazy Loading

Observe

Delayed Components

Infinite Scroll

Deferred Rendering

Dynamic Imports

Chunk Loading

Images Loading

Charts Loading

Document observed behavior.

---

# Progressive Loading

Observe

Header Loads First

Navigation Loads First

Content Loads Later

Widgets Load Independently

Cards Load Sequentially

Tables Load Later

Charts Load Last

Document rendering order.

---

# Background Operations

Observe

Silent Refresh

Background Fetch

Auto Refresh

Polling

Notification Updates

Realtime Updates

Synchronization

Only observe visible effects.

---

# User Interaction Responsiveness

Observe

Button Feedback

Menu Response

Dropdown Opening

Dialog Opening

Drawer Opening

Search Response

Filter Response

Sorting Response

Record user perception.

---

# Table Performance

Observe

Large Tables

Pagination

Virtual Scroll

Infinite Scroll

Load More

Expandable Rows

Grouped Rows

Document observable rendering.

---

# Search Performance

Observe

Instant Search

Delayed Search

Search Spinner

Suggestions

Live Search

Search Completion

Search Reset

---

# Filter Performance

Observe

Filter Application

Reset

Loading

Dependent Filters

Multiple Filters

Dynamic Results

---

# Form Performance

Observe

Field Rendering

Validation Feedback

Dynamic Fields

Section Expansion

Wizard Progress

Form Submission Indicator

Do not submit forms unnecessarily.

---

# Chart Rendering

Observe

Chart Appears

Animation

Progressive Rendering

Legend

Tooltip

Drill Down

Loading Placeholder

---

# File Operations

Observe

Upload Progress

Download Progress

Import Progress

Export Progress

Retry

Completion

Cancellation

---

# Notification Timing

Observe

Toast Appears

Toast Disappears

Loading Notification

Success Notification

Failure Notification

Progress Notification

---

# Refresh Behavior

Observe

Manual Refresh

Auto Refresh

Realtime Update

Background Refresh

Partial Refresh

Full Page Refresh

---

# Loading Indicators

Observe

Spinner

Skeleton

Progress Bar

Linear Progress

Circular Progress

Placeholder

Shimmer

Loading Text

Document where indicators appear.

---

# Offline Indicators

Observe

Offline Banner

Reconnect

Retry

Network Warning

Cached Content

Offline Page

Only document visible behavior.

---

# Browser Indicators

Observe

Tab Loading

Title Changes

Favicon Changes

Progress Indicators

Loading Cursor

---

# Performance Confidence

High

Direct observation.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

---

# Unknown Performance

If behavior cannot be observed

Return

Unknown

Never estimate timings.

Never fabricate delays.

---

# Output

Generate

Startup Behavior

Rendering Pattern

Loading Indicators

Navigation Behavior

Component Rendering

Lazy Loading

Progressive Rendering

Background Operations

Search Behavior

Filter Behavior

Refresh Behavior

Offline Indicators

Performance Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not benchmark page speed.

Do not estimate response time.

Do not compare against SLA.

Do not perform load testing.

Do not simulate concurrent users.

Do not intentionally slow the application.

Do not measure CPU or memory.

Only observe visible behavior.

---

# Success Criteria

The downstream Test Strategy Agent should understand

how the application presents loading,

how users perceive responsiveness,

where asynchronous operations occur,

and where performance-sensitive interactions exist,

without reopening the application.

---

# Final Principle

Performance observation is not performance testing.

Observe visible behavior.

Document user perception.

Preserve evidence.

Leave benchmarking to downstream agents.