# Knowledge Base 09
# Form Discovery

---

# Purpose

This knowledge base teaches the Application Discovery Planner Agent how to discover, classify, understand, and document forms within an application.

Forms are the primary interface through which users create, update, search, configure, approve, or submit business data.

Your responsibility is to identify forms and document their observable structure and behavior.

Never validate business rules.

Never intentionally submit invalid data.

Never infer backend validation.

Never assume hidden fields.

Only document observable evidence.

---

# Objective

Discover

Form Type

Business Purpose

Fields

Sections

Validation Indicators

Actions

Dependencies

Submission Flow

Navigation Flow

Accessibility Indicators

Produce a structured Form Blueprint.

---

# Form Philosophy

Every form exists to collect, modify, or search information.

A form is more than a collection of fields.

A form represents a business interaction.

Always identify

Why the form exists

What data it collects

How users interact

How users leave the form

---

# Discovery Lifecycle

Locate Form

↓

Determine Purpose

↓

Identify Sections

↓

Identify Fields

↓

Identify Validation

↓

Identify Actions

↓

Identify Dependencies

↓

Identify Submission Flow

↓

Generate Form Blueprint

---

# Form Categories

Every form belongs to one primary category.

Create

Update

Search

Login

Registration

Configuration

Approval

Import

Export

Wizard

Filter

Profile

Settings

Feedback

Survey

Contact

Unknown

Assign only one primary category.

---

# Form Types

Common form structures include

Single Page Form

Multi-Step Form

Wizard

Popup Form

Drawer Form

Inline Form

Expandable Form

Tabbed Form

Floating Form

Embedded Form

Modal Form

Record the observed type.

---

# Form Purpose

Determine why the form exists.

Examples

Create Employee

Edit Employee

Generate Roster

Assign Shift

Approve Request

Create Project

Login

Search Records

Configure Settings

Reset Password

Import CSV

Export Report

Only use observable evidence.

---

# Form Structure

Observe

Header

Description

Sections

Groups

Containers

Collapsible Panels

Tabs

Stepper

Footer

Action Area

Preserve structure.

---

# Field Categories

Identify every field.

Text

Textarea

Password

Email

Phone

Number

Currency

Percentage

URL

Date

Time

Date Time

Checkbox

Radio

Dropdown

Multi Select

Autocomplete

Lookup

File Upload

Image Upload

Color Picker

Slider

Toggle

Rich Text Editor

Code Editor

Hidden Field

Read Only Field

Unknown

---

# Field Properties

Observe

Label

Placeholder

Required

Optional

Read Only

Disabled

Default Value

Maximum Length

Minimum Length

Character Counter

Description

Tooltip

Helper Text

Never infer hidden constraints.

---

# Required Fields

Determine

Required

Optional

Unknown

Common indicators

*

Required label

Validation message

ARIA Required

Color indicator

Document only visible evidence.

---

# Field Groups

Fields are commonly organized.

Examples

Personal Information

Contact Information

Address

Employment

Shift Details

Project Information

Billing

Permissions

Emergency Contact

Settings

Preserve grouping.

---

# Conditional Fields

Some fields appear only after interaction.

Examples

Selecting Employee Type

↓

Additional Fields

Selecting Country

↓

State

↓

City

Selecting Shift Type

↓

Time Selection

Observe trigger conditions.

---

# Dynamic Forms

Indicators

Fields appear dynamically

Fields disappear

Sections collapse

Real-time calculations

Conditional validation

AJAX updates

Progressive disclosure

Document observable behavior.

---

# Validation Indicators

Observe

Required indicator

Inline validation

Error text

Warning text

Success message

Character count

Password strength

Input mask

Tooltip

Do not intentionally trigger errors.

---

# Input Masks

Observe

Phone

Date

Currency

Percentage

Postal Code

Employee ID

National ID

Tax ID

Time

Record observed formatting.

---

# Lookup Fields

Observe

Autocomplete

Search Lookup

Popup Lookup

Remote Search

Recent Selection

Dependent Lookup

Document interaction pattern.

---

# Date Components

Observe

Single Date

Date Range

Calendar

Month Picker

Year Picker

Time Picker

Date Time Picker

Week Picker

Recurring Date

---

# File Upload

Observe

Browse

Drag and Drop

Allowed Types

Maximum Size

Multiple Files

Preview

Delete

Progress

Retry

---

# Rich Text Editors

Observe

Formatting

Lists

Images

Tables

Links

Attachments

Mentions

Code Block

---

# Form Actions

Observe

Save

Submit

Cancel

Reset

Clear

Delete

Update

Next

Previous

Finish

Approve

Reject

Assign

Publish

Generate

Export

Import

Close

Every action should be documented.

---

# Submission Flow

Observe

Submit Button

Confirmation

Loading

Redirect

Success Message

Failure Message

Navigation After Submission

Do not intentionally submit production data.

---

# Navigation Flow

Determine

Entry Page

Exit Page

Cancel Destination

Success Destination

Back Navigation

Wizard Navigation

---

# Form States

Observe

Empty

Pre-filled

Read Only

Editable

Disabled

Loading

Submitting

Saved

Draft

Archived

Locked

Unknown

---

# Accessibility

Observe

Label Association

Tab Order

Keyboard Navigation

ARIA Labels

Focus Indicators

Required Indicators

Helper Text

Do not validate accessibility.

Only observe.

---

# Form Relationships

Every form belongs to

Application

↓

Module

↓

Page

↓

Form

↓

Sections

↓

Fields

↓

Actions

Preserve hierarchy.

---

# Form Confidence

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

# Unknown Forms

If purpose cannot be determined

Category

Unknown

Purpose

Unknown

Never invent business purpose.

---

# Output

Generate

Form Name

Form Category

Business Purpose

Parent Module

Parent Page

Sections

Fields

Required Fields

Optional Fields

Actions

Validation Indicators

Conditional Fields

Submission Flow

Navigation Flow

Accessibility Indicators

Observed States

Confidence

Unknown Areas

---

# Success Criteria

The downstream Test Strategy Agent should understand

what the form is,

why it exists,

what information it collects,

how users interact with it,

what actions are available,

and where the workflow continues,

without reopening the application.

---

# Common Discovery Mistakes

Do not classify every dialog as a form.

Do not assume every input belongs to one form.

Do not infer backend validation rules.

Do not invent required fields.

Do not intentionally submit destructive forms.

Do not merge multiple forms into one.

Always document forms independently.

---

# Final Principle

A form is a business interaction.

Understand its purpose.

Understand its structure.

Understand its flow.

Observe.

Document.

Never validate.

Never assume.