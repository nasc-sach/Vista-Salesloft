# Knowledge Base 06
# Authentication Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to identify, classify, and document authentication mechanisms within an application.

Authentication is the gateway to the application.

Its responsibility is to determine how users establish identity before accessing protected resources.

The objective is discovery only.

Never validate authentication.

Never bypass authentication.

Never brute force credentials.

Never perform security testing.

---

# Objective

Discover

Authentication Type

Authentication Flow

Authentication Components

Session Management

Role Indicators

Access Restrictions

Authentication States

Authentication Dependencies

Produce a structured authentication blueprint.

---

# Authentication Philosophy

Authentication is not just the Login page.

Authentication begins before login and continues until logout.

Observe the complete authentication lifecycle.

---

# Authentication Lifecycle

Application Launch

↓

Authentication Detection

↓

Identity Collection

↓

Credential Validation

↓

Session Creation

↓

Authorization

↓

Application Access

↓

Session Refresh

↓

Logout

Observe this lifecycle whenever possible.

---

# Authentication Entry Points

Authentication may begin from

Login Page

Landing Page

Protected Route

Popup Dialog

Modal Window

SSO Redirect

Embedded Login

Mobile Login Screen

Magic Link

Invitation Link

Deep Link

Record every observed entry point.

---

# Authentication Types

Possible authentication mechanisms include

Username and Password

Email and Password

Phone Number

OTP

Magic Link

Single Sign-On (SSO)

OAuth

OpenID Connect

SAML

Biometric

PIN

QR Login

Device Authentication

Social Login

API Token

Unknown

Only report observed authentication types.

---

# Credential Inputs

Observe available credential fields.

Examples

Username

Email

Password

Employee ID

Phone Number

Access Code

PIN

OTP

Security Question

Organization

Tenant

Workspace

Project

Do not infer hidden fields.

---

# Authentication Controls

Observe

Login Button

Continue Button

Next Button

Remember Me

Forgot Password

Show Password

Hide Password

Register

Sign Up

Guest Login

Skip

Back

Cancel

Logout

Session Expired

Record available controls.

---

# Multi-Step Authentication

Some applications separate authentication into multiple screens.

Example

Email

↓

Next

↓

Password

↓

OTP

↓

Dashboard

Record every authentication step.

---

# Single Sign-On

Possible providers

Microsoft

Google

GitHub

Apple

Okta

Azure AD

Auth0

Ping Identity

OneLogin

Custom SSO

Record visible provider names.

Do not inspect configuration.

---

# OAuth Indicators

Observe

Continue with Google

Continue with Microsoft

Continue with GitHub

Authorize

Consent Screen

Redirect URI

OAuth Callback

Token Redirect

Only document observed behavior.

---

# Multi-Factor Authentication

Possible indicators

OTP

Authenticator App

Push Notification

SMS

Email Verification

Backup Code

Security Key

Biometric

QR Code

Record

Trigger

Method

Position in workflow

---

# Password Features

Observe

Password Visibility Toggle

Password Strength

Requirements

Minimum Length

Complexity Rules

Hints

Validation

Password Expiration

Do not intentionally violate password rules.

---

# Registration

Observe if registration exists.

Identify

Registration Page

Required Fields

Verification

Terms Acceptance

Email Confirmation

Phone Confirmation

Invitation Requirement

Do not create accounts unless instructed.

---

# Password Recovery

Observe

Forgot Password

Reset Password

Recovery Email

Recovery SMS

Security Questions

Verification Link

Reset Success

Record workflow only.

---

# Session Discovery

Observe

Session Creation

Session Timeout

Session Expiration

Auto Logout

Idle Timeout

Remember Me

Persistent Session

Concurrent Sessions

Only observe.

---

# Logout Discovery

Observe

Logout Button

Profile Menu

Session End

Confirmation Dialog

Automatic Logout

Redirect After Logout

Record logout location.

---

# Authentication States

Determine current application state.

Possible states

Unauthenticated

Authenticating

Authenticated

Session Expired

Access Denied

Guest User

Partially Authenticated

Unknown

---

# Permission Indicators

Observe

Access Denied

Unauthorized

Forbidden

Hidden Menu

Disabled Controls

Missing Modules

Restricted Buttons

Restricted Pages

These indicate authorization boundaries.

---

# User Role Indicators

Possible roles

Administrator

Manager

Supervisor

Employee

Viewer

Approver

Operator

Guest

Unknown

Only use visible evidence.

Never infer organization structure.

---

# Authentication Errors

Observe

Invalid Credentials

Incorrect Password

Account Locked

Expired Password

Invalid OTP

Session Expired

Network Error

Access Denied

Do not intentionally trigger errors.

Only record observed errors.

---

# Security Observations

Observe

HTTPS

Secure Cookies

Remember Me

Logout

Session Timeout

MFA

Password Visibility

Account Selection

Do not perform penetration testing.

---

# Browser Storage Indicators

Observe existence of

Cookies

Session Storage

Local Storage

Authentication Tokens

Refresh Indicators

Only observe metadata.

Never inspect sensitive values.

---

# Authentication Navigation

Determine

Where authentication begins

Where authentication ends

First authenticated page

Protected routes

Public routes

Logout destination

---

# Authentication Confidence

High

Direct observation.

Medium

Strong evidence.

Low

Weak evidence.

Unknown

Insufficient evidence.

---

# Unknown Authentication

If authentication cannot be determined

Return

Authentication Type

Unknown

Never fabricate authentication mechanisms.

---

# Output

Produce

Authentication Type

Authentication Flow

Credential Inputs

Authentication Controls

Session Behavior

Permission Indicators

Role Indicators

Protected Routes

Public Routes

Authentication Confidence

Unknown Areas

---

# Success Criteria

The downstream Test Strategy Agent should understand

how users authenticate,

where authentication begins,

where it ends,

what restrictions exist,

and what authentication mechanisms were observed

without reopening the application.

---

# Final Principle

Authentication is the entrance to the application.

Observe the entrance.

Understand the journey.

Document the flow.

Never validate credentials.

Never test security.

Never bypass authentication.

Only discover.