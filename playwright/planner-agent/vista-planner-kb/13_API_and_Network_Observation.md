# Knowledge Base 13
# API and Network Observation

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to observe and document network activity and API communication occurring during application exploration.

The objective is to understand how the frontend communicates with backend services.

This knowledge is used only for application discovery.

Do not inspect sensitive information.

Do not modify requests.

Do not replay requests.

Do not fuzz endpoints.

Do not perform API testing.

Only observe network activity generated naturally while exploring the application.

---

# Objective

Discover

Network Requests

API Endpoints

Communication Pattern

Request Types

Response Types

Authentication Indicators

Realtime Communication

Third-party Integrations

Generate a Network Blueprint.

---

# Philosophy

Applications communicate continuously.

Pages are only one part of the system.

Every interaction may generate one or more backend requests.

Observe communication.

Do not interfere with communication.

---

# Observation Lifecycle

Application Loads

↓

Network Requests

↓

User Interaction

↓

Additional Requests

↓

Response

↓

UI Update

↓

Document Observation

---

# Network Categories

Observe

Document Requests

Stylesheets

JavaScript

Images

Fonts

XHR

Fetch

GraphQL

WebSocket

Server Sent Events

Beacon

Manifest

Service Worker

Media

Record each category.

---

# Request Methods

Observe

GET

POST

PUT

PATCH

DELETE

OPTIONS

HEAD

Unknown

Never infer request purpose.

---

# Endpoint Discovery

Record

Endpoint Path

Method

Observed Purpose

Status Code

Content Type

Frequency

Visibility

Never modify endpoint names.

Never guess undocumented endpoints.

---

# Request Timing

Observe

Application Startup

Authentication

Navigation

Form Open

Search

Filter

Sorting

Pagination

Submission

Export

Import

Logout

Record what action generated the request.

---

# Response Categories

Observe

JSON

HTML

Text

Binary

CSV

PDF

Image

Unknown

Never inspect confidential payloads.

---

# Status Codes

Observe

200

201

202

204

301

302

304

400

401

403

404

409

422

429

500

502

503

504

Record only observed codes.

---

# GraphQL Observation

Possible indicators

/graphql

Query

Mutation

Subscription

Apollo

Relay

Observe

Operation Name

Request Type

Response Type

Never inspect schema.

---

# REST Observation

Observe

Collection Endpoints

Resource Endpoints

Nested Resources

Pagination

Filtering

Sorting

Record only visible evidence.

---

# WebSocket Observation

Observe

Connection Established

Messages

Reconnect

Disconnect

Heartbeat

Streaming Updates

Realtime Notifications

Record observable behavior only.

---

# Authentication Indicators

Observe

Authorization Header Exists

Cookie Based Session

Bearer Token

Refresh Request

Login Request

Logout Request

Session Refresh

Do not inspect token values.

Never expose sensitive information.

---

# File Operations

Observe

Upload

Download

Import

Export

Progress

Retry

Completion

File Type

Do not inspect uploaded files.

---

# Third-Party Services

Observe

Analytics

Maps

Authentication

Payments

Notifications

Monitoring

Logging

Feature Flags

Cloud Storage

Chat Widgets

Record provider names if visible.

---

# API Relationships

Associate requests with

Page

↓

Component

↓

Action

↓

Network Request

↓

Response

Preserve relationships.

---

# Performance Indicators

Observe

Large Request

Slow Response

Repeated Requests

Burst Requests

Polling

Caching

Lazy Loading

Streaming

Only observe.

Do not benchmark.

---

# Duplicate Requests

Some requests repeat.

Determine

Initial Request

Repeated Request

Polling

Retry

Refresh

Do not document unnecessary duplicates.

---

# Security Indicators

Observe

HTTPS

Secure Cookies

CORS Errors

Mixed Content

Content Security Policy

Certificate Warnings

Only document visible indicators.

---

# Unknown Requests

If request purpose cannot be determined

Purpose

Unknown

Never invent endpoint functionality.

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

---

# Output

Generate

Request Method

Endpoint

Observed Purpose

Trigger

Response Type

Status Code

Communication Type

Authentication Indicator

Third-party Service

Relationships

Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not inspect confidential payloads.

Do not expose authentication tokens.

Do not replay requests.

Do not modify traffic.

Do not infer backend implementation.

Do not guess API contracts.

Do not classify requests solely by URL.

Always relate requests to observable user actions.

---

# Success Criteria

The downstream Test Strategy Agent should understand

which user interactions generate backend communication,

what communication patterns exist,

where API boundaries appear,

and how network activity relates to business workflows,

without reopening the application.

---

# Final Principle

The frontend reveals how it communicates.

Observe communication.

Associate it with user interactions.

Preserve evidence.

Never interfere with network traffic.

Never inspect sensitive information.

Only discover.