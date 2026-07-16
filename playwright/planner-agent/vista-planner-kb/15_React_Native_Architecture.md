# Knowledge Base 15
# React Native Architecture Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to recognize, understand, and document React Native applications.

Unlike React Web applications, React Native applications use native mobile components, mobile navigation patterns, gestures, and device capabilities.

The Planner Agent should understand these application structures without relying on implementation details.

This knowledge base applies only to React Native applications.

---

# Objective

Discover

Application Structure

Navigation

Screens

Components

Forms

Lists

Native Features

Platform Specific Behavior

Business Modules

Generate a React Native Application Blueprint.

---

# React Native Philosophy

React Native applications are screen-driven rather than page-driven.

Unlike web applications

Page

↓

Route

↓

Browser

React Native applications use

Screen

↓

Navigator

↓

Native Stack

↓

Native Components

Always think in terms of Screens.

Never Pages.

---

# Discovery Lifecycle

Application Launch

↓

Splash Screen

↓

Authentication

↓

Navigation

↓

Screens

↓

Components

↓

Business Workflows

↓

Generate Blueprint

---

# Application Structure

Typical hierarchy

Application

↓

Navigator

↓

Screen

↓

Section

↓

Component

↓

Interaction

Always preserve hierarchy.

---

# Navigation Types

Observe

Stack Navigation

Bottom Tabs

Top Tabs

Drawer Navigation

Native Stack

Nested Navigation

Modal Navigation

Deep Links

Authentication Stack

Unknown

Record observed navigation.

---

# Screen Discovery

For every screen determine

Screen Name

Purpose

Parent Navigator

Entry Point

Exit Point

Primary Actions

Visible Components

Business Module

Unknown Areas

---

# Navigation Indicators

Observe

Back Button

Tab Bar

Drawer

Hamburger

Header

Floating Action Button

Bottom Navigation

Swipe Navigation

Deep Link

Record navigation relationships.

---

# Native Components

Observe

Button

Text

TextInput

Image

ScrollView

FlatList

SectionList

Pressable

TouchableOpacity

TouchableHighlight

TouchableWithoutFeedback

Switch

Slider

ActivityIndicator

SafeAreaView

Modal

KeyboardAvoidingView

RefreshControl

WebView

Unknown

Document observed components.

---

# Lists

React Native commonly uses

FlatList

SectionList

VirtualizedList

Infinite Scroll

Grouped List

Searchable List

Refreshable List

Observe

Scrolling

Pagination

Refresh

Grouping

Selection

---

# Forms

Observe

Text Fields

Password

Dropdown

Date Picker

Time Picker

Toggle

Checkbox

Radio

File Picker

Camera Picker

Gallery Picker

Signature

OTP

Keyboard Type

Return Key

Validation

Do not submit forms unnecessarily.

---

# Device Features

Observe

Camera

Microphone

Location

Bluetooth

Contacts

Notifications

Biometric Authentication

Gallery

Files

Clipboard

QR Scanner

NFC

Phone

Email

Maps

Only document observable usage.

Never request permissions unnecessarily.

---

# Gestures

Observe

Tap

Double Tap

Long Press

Swipe

Pinch

Zoom

Drag

Drop

Pull To Refresh

Scroll

Horizontal Swipe

Vertical Swipe

Only document visible interactions.

---

# Platform Behaviors

Observe

Android Specific

iOS Specific

Shared Behavior

Orientation Changes

Safe Area

Keyboard Behavior

Status Bar

Navigation Bar

Theme

Dark Mode

Document observable differences.

---

# Native Dialogs

Observe

Permission Dialog

Action Sheet

Bottom Sheet

Share Dialog

Date Picker

Time Picker

Alert

Confirmation

Native File Picker

Camera Picker

Document trigger and purpose.

---

# Offline Behavior

Observe

Offline Banner

Retry

Reconnect

Cached Data

Sync

Pending Upload

Document visible behavior only.

---

# Push Notifications

Observe

Notification Permission

Foreground Notification

Background Notification

Badge

Deep Link

Notification Center

Only document visible behavior.

---

# Deep Links

Observe

Application launched from link

Screen opened

Parameters

Navigation path

Document observed deep links.

---

# Authentication

Observe

Login

Biometric

OTP

Magic Link

SSO

PIN

Session

Logout

Use KB-06 for authentication details.

---

# Performance Indicators

Observe

Splash Duration

Loading Screen

Screen Transition

Lazy Rendering

Image Loading

Infinite Scroll

Refresh

Do not benchmark.

---

# Accessibility

Observe

Screen Reader Labels

Large Text Support

Focus Order

Touch Target

VoiceOver

TalkBack

Only observe.

---

# Unknown Components

If a component cannot be identified

Category

Unknown

Confidence

Unknown

Never invent native components.

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

Assign confidence to every observation.

---

# Output

Generate

Application Structure

Navigation

Screens

Business Modules

Native Components

Forms

Lists

Device Features

Gestures

Platform Behavior

Offline Behavior

Push Notification Indicators

Deep Link Indicators

Accessibility Indicators

Confidence

Unknown Areas

---

# Common Discovery Mistakes

Do not classify screens as web pages.

Do not assume Android and iOS behave identically.

Do not request device permissions unnecessarily.

Do not infer hidden device capabilities.

Do not inspect native source code.

Do not assume every gesture is available.

Do not invent deep links.

Only document observable behavior.

---

# Success Criteria

The downstream Test Strategy Agent should understand

how the React Native application is organized,

how users navigate,

what screens exist,

what native capabilities are used,

and how business workflows operate,

without reopening the application.

---

# Final Principle

React Native applications are mobile-first.

Think in Screens.

Think in Navigators.

Think in Native Components.

Observe.

Classify.

Relate.

Document.

Never assume.