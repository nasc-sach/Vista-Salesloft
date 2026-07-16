# Knowledge Base 16
# Discovery Output Model

---

# Purpose

This knowledge base defines the canonical data model used by the Application Discovery Planner Agent.

Every discovery performed by the Planner Agent must contribute to this model.

The model represents the complete architectural understanding of the application.

It serves as the official contract between the Planner Agent and all downstream agents.

No other internal output format should be produced.

---

# Philosophy

The Planner Agent performs many discovery activities.

Examples

Authentication

Navigation

Forms

CRUD

Workflows

Network

Performance

React

React Native

All discoveries must eventually populate a single Application Blueprint.

The blueprint represents the discovered application.

It does not represent assumptions.

Every property must originate from observable evidence.

---

# Blueprint Lifecycle

Receive Input

↓

Application Discovery

↓

Evidence Collection

↓

Classification

↓

Relationship Mapping

↓

Confidence Assignment

↓

Blueprint Generation

↓

Handoff

---

# Blueprint Structure

ApplicationBlueprint

Application

Technology

Authentication

Navigation

Modules

Pages

Components

Forms

CRUD

Workflows

Network

Performance

Platform

DiscoveryMetadata

Recommendations

---

# Application

Contains

Application Name

Base URL

Platform

Environment

Language

Theme

Entry Point

Version (if visible)

Description

Unknown Fields

Confidence

---

# Technology

Contains

Framework

Routing

Rendering

State Management Indicators

UI Library Indicators

Styling Indicators

Native Indicators

Build Indicators

Unknown

Confidence

Never infer implementation.

---

# Authentication

Contains

Authentication Type

Authentication Flow

Credential Inputs

Protected Routes

Public Routes

Session Indicators

Role Indicators

Permission Indicators

Confidence

---

# Navigation

Contains

Navigation Type

Hierarchy

Entry Points

Exit Points

Relationships

Role Restrictions

Dynamic Navigation

Unknown Areas

Confidence

---

# Modules

Every module contains

Module Name

Business Purpose

Importance

Parent Module

Child Modules

Entry Pages

Workflows

Confidence

---

# Pages

Every page contains

Page Name

Page Category

Business Purpose

Route

Parent Module

Primary Components

Actions

Importance

Confidence

---

# Components

Every component contains

Component Name

Category

Purpose

States

Actions

Relationships

Accessibility Indicators

Confidence

---

# Forms

Every form contains

Form Name

Category

Purpose

Sections

Fields

Validation Indicators

Actions

Submission Flow

Navigation Flow

Confidence

---

# CRUD

Every CRUD module contains

Business Entity

Operations

Tables

Columns

Relationships

Permissions

Workflow Connections

Confidence

---

# Workflows

Every workflow contains

Workflow Name

Category

Entry Point

Steps

Navigation

Dependencies

Participants

Completion

Confidence

---

# Network

Contains

Observed Requests

Endpoints

Communication Types

Authentication Indicators

Realtime Connections

Third Party Services

Confidence

---

# Performance

Contains

Startup

Rendering

Loading

Lazy Loading

Refresh

User Perception

Confidence

---

# Platform

Contains

Platform Type

React

React Native

Responsive Indicators

Native Features

Device Features

Confidence

---

# Discovery Metadata

Contains

Discovery Timestamp

Discovery Duration

Pages Visited

Modules Visited

Screens Visited

Components Discovered

Forms Discovered

Workflows Discovered

Network Requests Observed

Discovery Status

Discovery Completion

---

# Recommendations

Recommendations are only for downstream agents.

Examples

High Priority Workflow

Unknown Authentication

Large CRUD Module

Dynamic Navigation Detected

Heavy API Usage

React Native Features Present

These are not testing recommendations.

These are discovery recommendations.

---

# Relationships

Everything should remain connected.

Application

↓

Modules

↓

Pages

↓

Components

↓

Forms

↓

Fields

↓

Actions

↓

Workflows

↓

Network

Never flatten relationships.

---

# Confidence Model

Every object contains

Confidence

Evidence Count

Observation Method

Unknown Fields

Never omit confidence.

---

# Unknown Values

Unknown is valid.

If information cannot be discovered

Store

Unknown

Never fabricate values.

---

# Duplicate Handling

Duplicate discoveries should merge.

Never create duplicate modules.

Never create duplicate pages.

Never create duplicate workflows.

Relationships should be preserved.

---

# Versioning

Every blueprint contains

Schema Version

Blueprint Version

Planner Version

Discovery Version

This enables future compatibility.

---

# Output Rules

The Planner Agent must produce

One

and only one

Application Blueprint.

Do not produce

Markdown

Tables

Narrative Reports

Natural Language Summaries

Multiple JSON Objects

Partial Schemas

Everything must exist inside the blueprint.

---

# Validation Rules

Before handoff verify

Required sections exist

Relationships are valid

Confidence exists

Unknown values are explicit

No duplicate objects exist

No orphan pages exist

No orphan workflows exist

No orphan components exist

---

# Success Criteria

The Application Blueprint should contain enough information for the Test Strategy Agent to begin generating test strategies without reopening the application.

The blueprint should represent the application's architecture rather than a collection of observations.

---

# Final Principle

The Application Blueprint is the Planner Agent's final product.

Everything the Planner discovers must strengthen this blueprint.

Nothing should exist outside it.