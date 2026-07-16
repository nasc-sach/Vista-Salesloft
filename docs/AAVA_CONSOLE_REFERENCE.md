# AAVA Console Reference

**Version:** 1.0  
**Last Updated:** 2024  
**Purpose:** Complete reference for the AAVA Console multi-agent testing workflow

---

## Table of Contents

1. [Overview](#overview)
2. [Multi-Agent Workflow](#multi-agent-workflow)
3. [Blueprint Flow](#blueprint-flow)
4. [Planner Agent](#planner-agent)
5. [Test Strategy Agent](#test-strategy-agent)
6. [Scenario Generation Agent](#scenario-generation-agent)
7. [Tool Contract Patterns](#tool-contract-patterns)
8. [Agent Communication Protocol](#agent-communication-protocol)
9. [Core Principles](#core-principles)
10. [Application Blueprint Structure](#application-blueprint-structure)

---

## Overview

AAVA Console is a multi-agent system for evidence-based test planning and scenario generation. It uses a structured workflow where specialized agents collaborate through **immutable handoffs** and **structured markdown blueprints**.

### Key Features

- **Evidence-Based Discovery**: All outputs grounded in observable evidence
- **No Inference Policy**: Agents never guess or assume
- **Structured Blueprints**: Markdown-based, versioned, self-contained
- **Validator Tools**: Each agent validates completeness and traceability
- **Immutable Handoffs**: Upstream artifacts are never modified downstream

---

## Multi-Agent Workflow

### Workflow Stages

```
┌─────────────────────┐
│ Input Collection    │
│ Agent               │
└──────────┬──────────┘
           │ User Inputs + Initial Requirements
           ▼
┌─────────────────────┐
│ Planner Agent       │ ◄── Browser Exploration (bs)
│                     │ ◄── Technology Detection (cs)
│                     │ ◄── Auth Discovery (ds)
└──────────┬──────────┘
           │ Application Blueprint (IMMUTABLE)
           ▼
┌─────────────────────┐
│ Test Strategy       │ ◄── Strategy Validator (es)
│ Agent               │ ◄── Traceability Validator (fs)
└──────────┬──────────┘
           │ Testing Strategy Blueprint (IMMUTABLE)
           ▼
┌─────────────────────┐
│ Scenario Generation │ ◄── Scenario Validator (gs)
│ Agent               │ ◄── Traceability Validator (hs)
└──────────┬──────────┘
           │ Scenario Specification Blueprint
           ▼
┌─────────────────────┐
│ Automation/         │
│ Execution           │
└─────────────────────┘
```

### Stage Responsibilities

| Stage | Input | Output | Key Responsibility |
|-------|-------|--------|-------------------|
| **Input Collection** | User requirements | Structured inputs | Gather URL, scope, priorities |
| **Planner** | URL + requirements | Application Blueprint | Discover app structure, tech, auth, workflows |
| **Test Strategy** | Application Blueprint | Testing Strategy Blueprint | Define test objectives, areas, priorities |
| **Scenario Generation** | Testing Strategy Blueprint | Scenario Specification Blueprint | Create detailed, traceable test scenarios |
| **Automation** | Scenario Specification | Executable tests | Generate Playwright tests |

---

## Blueprint Flow

### 1. Application Blueprint (Planner Output)

**Purpose:** Structured markdown describing the application's architecture, modules, pages, workflows, authentication, and navigation.

**Schema Location:** `playwright/planner-agent/vista-planner-kb/18_Application_Blueprint_Modeling.md`

**Key Sections:**
- Application Identity
- Technology Stack
- Authentication Mechanisms
- Navigation Structure
- Business Modules
- Pages
- Components
- Forms
- CRUD Entities
- Workflows
- Dialogs/Overlays
- Network Observations
- Performance Observations
- Evidence
- Confidence Levels
- Unknown Areas

**Immutability:** Once created, the Application Blueprint is **read-only** for downstream agents.

---

### 2. Testing Strategy Blueprint (Test Strategy Output)

**Purpose:** Evidence-backed testing approach derived from the Application Blueprint.

**Key Sections:**
- Test Objectives (traced to business modules)
- Test Areas (traced to pages/workflows)
- Priority Classification
- Coverage Matrix
- Risk Assessment
- Testing Approach
- Evidence References

**Validation:**
- Completeness against Application Blueprint
- Traceability to Application Blueprint
- Consistency and readiness

**Immutability:** Once validated, the Testing Strategy Blueprint is **read-only** for downstream agents.

---

### 3. Scenario Specification Blueprint (Scenario Generation Output)

**Purpose:** Detailed, automation-ready test scenarios with complete traceability.

**Key Sections:**
- Scenario ID (unique identifier)
- Scenario Name
- Objective (from Testing Strategy)
- Preconditions
- Test Data
- Steps (detailed actions)
- Expected Behavior
- Validation Points
- Variants (positive, negative, edge cases)
- Traceability (Scenario → Strategy → Application → Business Purpose)

**Validation:**
- Completeness against Testing Strategy
- Full traceability chain
- Automation readiness
- Test data clarity

---

## Planner Agent

**Location:** `playwright/planner-agent/planner-agent-prompt.md`

### Role

The Planner Agent is responsible for discovering and documenting the application structure through systematic exploration. It produces the **Application Blueprint**.

### Responsibilities

1. Navigate the application systematically
2. Identify technology stack and frameworks
3. Discover authentication mechanisms
4. Map navigation structure
5. Document business modules, pages, components
6. Identify forms, CRUD entities, workflows
7. Record network and performance observations
8. Maintain evidence for all observations
9. Mark unknowns explicitly

### Tools Available

#### 1. Browser Exploration Tool (bs)

**Location:** `playwright/planner-agent/tool-prompts/bs.md`

**Role:** Execute browser actions and return observable evidence only.

**NOT:**
- AI planner
- Analyzer
- Tester
- Business analyst

**Available Actions:**
- `navigate(url)` - Navigate to URL
- `click(selector)` - Click element
- `scroll(direction, amount)` - Scroll page
- `hover(selector)` - Hover over element
- `wait(duration)` - Wait for specified time
- `screenshot(name)` - Capture screenshot

**Input Parameters:**
- **Main Input:** URL (required)
- **Optional Inputs:** Action sequence, wait conditions

**Output Contract:**
```markdown
## Browser Observation
- **Action Executed:** [action description]
- **Observable Result:** [what changed/appeared]
- **DOM Elements:** [visible elements]
- **Network Activity:** [requests observed]
- **Screenshots:** [references]
- **Timestamp:** [ISO 8601]
```

**Constraints:**
- Observe only, never interpret
- No business logic analysis
- No test generation
- No recommendations
- Report exact DOM state

**Final Rule:** Observe only. Never infer.

---

#### 2. Technology Detection Tool (cs)

**Location:** `playwright/planner-agent/tool-prompts/cs.md`

**Role:** Detect technologies, frameworks, and libraries based on observable indicators.

**Input Parameters:**

**Main Input:** URL (required)

**Optional Dropdown Inputs:**

1. **Observation Scope:**
   - Current Page (default)
   - Initial Load
   - Visible Page Area
   - Navigation Trail

2. **Viewport:**
   - Current Viewport (default)
   - Desktop (1920x1080)
   - Mobile (375x667)

3. **Wait Strategy:**
   - Immediate (default)
   - Page Loaded
   - Element Visible
   - Dialog Visible

**Technologies Detected:**
- **Frontend Frameworks:** React, Angular, Vue, Svelte, Next.js, Nuxt.js
- **Build Tools:** Vite, Webpack, Rollup, Parcel
- **UI Libraries:** Material UI, Ant Design, Bootstrap, Tailwind
- **State Management:** Redux, MobX, Zustand, Pinia
- **API Patterns:** GraphQL, REST, WebSocket, gRPC
- **PWA Features:** Service Workers, Manifest

**Output Contract:**
```markdown
## Technology Detection
- **Technology:** [name]
- **Observed Indicator:** [what was seen]
- **Evidence:** [specific artifact]
- **Confidence:** [High/Medium/Low]
```

**Constraints:**
- Only report technologies with observable evidence
- Never infer from file names alone
- Unknown is preferred over guessing
- Confidence must match evidence strength

**Final Rule:** Observe only. Never infer.

---

#### 3. Authentication Discovery Tool (ds)

**Location:** `playwright/planner-agent/tool-prompts/ds.md`

**Role:** Discover authentication mechanisms and patterns through observation.

**Input Parameters:**

**Main Input:** URL (required)

**Optional Dropdown Input:**

**Observation Focus:**
- Current Page (default)
- Login Screen
- Protected Area
- Session State
- Visible Auth UI

**Authentication Patterns Detected:**
- **Login Mechanisms:** Username/Password, Email/Password, SSO, OAuth, SAML
- **MFA/2FA:** OTP, SMS, Email verification, Authenticator app
- **Session Management:** Cookies, JWT, Local Storage, Session Storage
- **Credential Fields:** Input types, labels, placeholders
- **Protected Routes:** Redirects, 401/403 responses
- **Session Expiration:** Timeout warnings, auto-logout

**Output Contract:**
```markdown
## Authentication Observation
- **Observation:** [what was observed]
- **Location:** [where it was found]
- **Visible Element:** [DOM details]
- **Current URL:** [page URL]
- **Timestamp:** [ISO 8601]
- **Confidence:** [High/Medium/Low]
```

**Constraints:**
- Never validate credentials
- Never attempt brute force
- Never infer auth beyond visible UI
- Never test session manipulation
- Report only observable mechanisms

**Final Rule:** Observe only. Never infer beyond visible elements.

---

### Planner Agent Knowledge Base

#### Application Blueprint Modeling

**Location:** `playwright/planner-agent/vista-planner-kb/18_Application_Blueprint_Modeling.md`

**Key Concepts:**

1. **Business Modules** - Parent containers grouping related functionality
2. **Pages** - Individual views that belong to modules
3. **Components** - UI elements that belong to pages
4. **Forms** - Data input patterns
5. **CRUD Entities** - Create, Read, Update, Delete operations
6. **Workflows** - Multi-step processes spanning multiple pages
7. **Dialogs/Overlays** - Modal UI patterns

**Evidence Requirements:**
- Every observation must cite source (URL, screenshot, DOM selector)
- Confidence levels must match evidence strength
- Unknowns are first-class citizens

**Structure Example:**
```markdown
## Business Module: [Name]
**Purpose:** [Observable purpose]
**Entry Point:** [URL or navigation path]
**Evidence:** [Reference]

### Page: [Name]
**URL Pattern:** [pattern]
**Observable Elements:** [list]
**Evidence:** [Reference]

#### Component: [Name]
**Type:** [button/form/table/etc]
**Behavior:** [observable behavior]
**Evidence:** [Reference]
```

---

#### Agent Communication and Handoff Protocol

**Location:** `playwright/planner-agent/vista-planner-kb/21_Agent_Communication_and_Handoff_Protocol.md`

**Key Principles:**

1. **Structured Information, Not Conversation**
   - Agents communicate via structured markdown
   - No prose explanations
   - No conversational elements

2. **Immutable Handoffs**
   - Planner output is READ-ONLY for downstream agents
   - Test Strategy output is READ-ONLY for Scenario Generation
   - Agents extend, never modify

3. **Completeness Requirements**
   - Every handoff must be self-contained
   - No external references required
   - All context included

4. **Deterministic**
   - Same input → Same output
   - No random elements
   - Reproducible

5. **Versioned**
   - Planner Version
   - Blueprint Version
   - Schema Version
   - Discovery Status

6. **Evidence-Backed**
   - Every claim must have evidence
   - Unknown is preferred over guessing
   - Confidence levels required

**Required Metadata:**
```markdown
## Metadata
- **Planner Version:** [version]
- **Blueprint Version:** [version]
- **Schema Version:** [version]
- **Discovery Status:** [Complete/Partial/In-Progress]
- **Generated At:** [ISO 8601 timestamp]
```

**Unknowns as First-Class Citizens:**
```markdown
## Unknown Areas
- **Unknown:** [what is unknown]
- **Reason:** [why it's unknown]
- **Impact:** [how it affects downstream]
- **Discovery Required:** [Yes/No]
```

**Security Constraints:**
- Never transfer passwords
- Never transfer tokens
- Never transfer PII
- Never transfer session cookies

---

## Test Strategy Agent

**Location:** `playwright/test-strategy-agent/test-strategy-agent-prompt.md`

### Role

The Test Strategy Agent translates the Application Blueprint into a comprehensive, evidence-backed testing strategy. It produces the **Testing Strategy Blueprint**.

### Responsibilities

1. Analyze the Application Blueprint
2. Define test objectives traced to business modules
3. Identify test areas traced to pages/workflows
4. Prioritize testing efforts
5. Create coverage matrix
6. Assess risks
7. Document testing approach
8. Validate completeness and traceability

### Tools Available

#### 1. Testing Strategy Validator Tool (es)

**Location:** `playwright/test-strategy-agent/tool-prompts/es.md`

**Role:** Validate Testing Strategy Blueprint against Application Blueprint.

**Input Parameters:**
- **Application Blueprint:** [complete blueprint from Planner]
- **Testing Strategy Blueprint:** [current strategy being validated]

**Validation Checks:**

1. **Coverage Validation**
   - Every business module has test objectives
   - Every page has test areas
   - Every workflow has test coverage
   - Every form has validation tests

2. **Traceability Validation**
   - Every test objective traces to business module
   - Every test area traces to page or workflow
   - Evidence references are valid

3. **Readiness Validation**
   - All required sections present
   - No placeholder content
   - Confidence levels assigned
   - Unknowns documented

4. **Consistency Validation**
   - No contradictions
   - Terminology matches Application Blueprint
   - Priority alignment

**Output Contract:**
```markdown
## Validation Result
**ValidationStatus:** [PASSED/FAILED]
**ValidationSummary:** [one-line summary]

## Detected Issues
### Critical Issues
- [issue description]
- [traceability gap]

### Warnings
- [potential issue]
- [missing coverage]

## Readiness Status
**Ready for Handoff:** [Yes/No]
**Blocking Issues:** [count]
**Required Actions:** [list]
```

**Constraints:**
- Never generate strategy content
- Never modify input blueprints
- Only validate, never repair
- Unknown is acceptable if documented

**Final Rule:** Validate only. Never generate strategy.

---

#### 2. Strategy Traceability Validator Tool (fs)

**Location:** `playwright/test-strategy-agent/tool-prompts/fs.md`

**Role:** Validate that Testing Strategy Blueprint traces back to Application Blueprint.

**Input Parameters:**
- **Application Blueprint:** [complete blueprint from Planner]
- **Testing Strategy Blueprint:** [current strategy being validated]

**Traceability Checks:**

1. **Forward Traceability**
   - Test Objective → Business Module
   - Test Area → Page/Workflow
   - Test Priority → Application Priority

2. **Backward Traceability**
   - Business Module → Test Objective (coverage)
   - Page → Test Area (coverage)
   - Workflow → Test Scenario (coverage)

3. **Reference Validation**
   - All module references exist in Application Blueprint
   - All page references exist in Application Blueprint
   - All workflow references exist in Application Blueprint

4. **Evidence Chain**
   - Test objectives cite Application Blueprint evidence
   - Test areas cite observable elements
   - Coverage gaps documented as unknowns

**Output Contract:**
```markdown
## Traceability Validation Result
**TraceabilityStatus:** [PASSED/FAILED]
**TraceabilitySummary:** [one-line summary]

## Traceability Matrix
| Test Objective | → | Business Module | Status |
|----------------|---|-----------------|--------|
| [objective]    | → | [module]        | ✓/✗    |

## Broken References
- **Test Objective:** [name]
  - **References:** [module]
  - **Issue:** [not found in Application Blueprint]

## Coverage Gaps
- **Business Module:** [name]
  - **Issue:** [no test objectives defined]

## Readiness Status
**Ready for Handoff:** [Yes/No]
**Blocking Issues:** [count]
```

**Constraints:**
- Never generate strategy content
- Never modify references
- Never repair broken references
- Only validate traceability

**Final Rule:** Validate traceability only. Never generate or repair.

---

## Scenario Generation Agent

**Location:** `playwright/scenario-generation-agent/scenario-agent-prompt.md`

### Role

The Scenario Generation Agent creates detailed, automation-ready test scenarios from the Testing Strategy Blueprint. It produces the **Scenario Specification Blueprint**.

### Responsibilities

1. Analyze Testing Strategy Blueprint
2. Create detailed test scenarios for each test area
3. Define preconditions and test data
4. Specify step-by-step actions
5. Define expected behavior and validation points
6. Generate scenario variants (positive, negative, edge cases)
7. Maintain complete traceability chain
8. Validate scenario completeness and automation readiness

### Tools Available

#### 1. Scenario Specification Validator Tool (gs)

**Location:** `playwright/scenario-generation-agent/tool-prompts/gs.md`

**Role:** Validate Scenario Specification Blueprint against Testing Strategy Blueprint.

**Input Parameters:**
- **Application Blueprint:** [complete blueprint from Planner]
- **Testing Strategy Blueprint:** [complete strategy from Test Strategy Agent]
- **Scenario Specification Blueprint:** [current scenarios being validated]

**Validation Checks:**

1. **Completeness Validation**
   - Every test area has scenarios
   - Every test objective has coverage
   - All required scenario sections present
   - Test data specified
   - Expected behavior defined

2. **Consistency Validation**
   - Terminology matches Testing Strategy
   - Steps are unambiguous
   - Validation points are clear
   - No contradictions

3. **Quality Validation**
   - Scenarios are atomic (single objective)
   - Steps are detailed enough for automation
   - Test data is concrete
   - Expected behavior is observable
   - Variants cover key paths

4. **Automation Readiness**
   - Selectors or identifiers specified
   - Actions are executable
   - Expected outcomes are verifiable
   - No manual intervention required

**Output Contract:**
```markdown
## Scenario Validation Result
**ValidationStatus:** [PASSED/FAILED]
**ValidationSummary:** [one-line summary]

## Completeness Issues
### Missing Scenarios
- **Test Area:** [name]
- **Issue:** [no scenarios defined]

### Incomplete Scenarios
- **Scenario ID:** [id]
- **Issue:** [missing test data / missing expected behavior]

## Quality Issues
### Ambiguous Steps
- **Scenario ID:** [id]
- **Step:** [step description]
- **Issue:** [not specific enough for automation]

### Unclear Validation
- **Scenario ID:** [id]
- **Issue:** [expected behavior not observable]

## Automation Readiness
**Ready for Automation:** [Yes/No]
**Blocking Issues:** [count]
**Required Actions:** [list]
```

**Constraints:**
- Never generate scenarios
- Never modify scenarios
- Only validate, never repair
- Unknown is acceptable if documented

**Final Rule:** Validate only. Never generate scenarios.

---

#### 2. Scenario Traceability Validator Tool (hs)

**Location:** `playwright/scenario-generation-agent/tool-prompts/hs.md`

**Role:** Validate complete traceability through entire testing lifecycle.

**Input Parameters:**
- **Application Blueprint:** [complete blueprint from Planner]
- **Testing Strategy Blueprint:** [complete strategy from Test Strategy Agent]
- **Scenario Specification Blueprint:** [current scenarios being validated]

**Traceability Checks:**

1. **Full Chain Validation**
   - Scenario → Test Area → Page/Workflow → Business Module
   - Scenario → Test Objective → Business Module
   - Scenario → Application Evidence

2. **Forward Traceability**
   - Every scenario references a test area
   - Every test area references a page or workflow
   - Every page/workflow belongs to a business module

3. **Backward Traceability**
   - Every test area has scenarios
   - Every test objective has scenario coverage
   - Every business module has scenario coverage

4. **Evidence Chain**
   - Scenario steps reference Application Blueprint elements
   - Expected behavior aligns with observable evidence
   - Test data aligns with discovered forms/inputs

**Output Contract:**
```markdown
## Traceability Validation Result
**TraceabilityStatus:** [PASSED/FAILED]
**TraceabilitySummary:** [one-line summary]

## Complete Traceability Chain
| Scenario | → | Test Area | → | Page/Workflow | → | Business Module | → | Business Purpose |
|----------|---|-----------|---|---------------|---|-----------------|---|------------------|
| [id]     | → | [area]    | → | [page]        | → | [module]        | → | [purpose]        |

## Broken Traceability
### Scenario Without Test Area
- **Scenario ID:** [id]
- **Issue:** [references non-existent test area]

### Test Area Without Application Element
- **Test Area:** [name]
- **Issue:** [references non-existent page/workflow]

## Coverage Gaps
### Test Areas Without Scenarios
- **Test Area:** [name]
- **From Strategy:** [reference]
- **Issue:** [no scenarios defined]

### Test Objectives Without Scenario Coverage
- **Test Objective:** [name]
- **From Strategy:** [reference]
- **Issue:** [no scenarios trace to this objective]

## Readiness Status
**Ready for Automation:** [Yes/No]
**Blocking Issues:** [count]
**Traceability Completeness:** [percentage]
```

**Constraints:**
- Never generate scenarios
- Never modify references
- Never repair broken traceability
- Only validate the complete chain

**Final Rule:** Validate traceability only. Never generate or repair.

---

## Tool Contract Patterns

All AAVA Console tools follow a standardized contract pattern to ensure consistency and predictability.

### Standard Tool Structure

```markdown
# Tool Name

## Role
[One-line description of tool purpose]

## NOT (Anti-Responsibilities)
- [What this tool is NOT]
- [What this tool does NOT do]

## Input Parameters

### Main Input
- **[Parameter Name]:** [description] (required)

### Optional Dropdown Inputs
1. **[Parameter Name]:**
   - Option 1 (default)
   - Option 2
   - Option 3

## Responsibilities
[What the tool observes or validates]

## Constraints
[Hard limits on tool behavior]

## Output Contract
[Exact output structure]

## Final Rule
[Absolute constraint, typically "Observe only. Never infer."]
```

### Tool Categories

#### 1. Exploration Tools

**Purpose:** Discover and observe application characteristics

**Examples:**
- Browser Exploration Tool (bs)
- Technology Detection Tool (cs)
- Authentication Discovery Tool (ds)

**Common Constraints:**
- Observe only
- Never interpret
- Never infer
- Report exact state

**Output:** Structured evidence

---

#### 2. Validator Tools

**Purpose:** Validate blueprint completeness and quality

**Types:**

**A. Specification Validators**
- Validate current blueprint against upstream blueprint
- Check completeness, consistency, quality
- Report issues and readiness

**Examples:**
- Testing Strategy Validator (es)
- Scenario Specification Validator (gs)

**B. Traceability Validators**
- Validate traceability chain
- Check forward and backward references
- Report coverage gaps

**Examples:**
- Strategy Traceability Validator (fs)
- Scenario Traceability Validator (hs)

**Common Constraints:**
- Never generate content
- Never modify inputs
- Never repair issues
- Only validate

**Output:** Validation report with status and issues

---

### Input Parameter Patterns

#### Main Input
Always required, typically a URL or blueprint reference.

```markdown
### Main Input
- **URL:** Application URL to explore (required)
```

#### Optional Dropdown Inputs
Predefined options with a default value.

```markdown
### Optional Dropdown Inputs

1. **Observation Scope:**
   - Current Page (default)
   - Initial Load
   - Visible Page Area
   - Navigation Trail

2. **Viewport:**
   - Current Viewport (default)
   - Desktop (1920x1080)
   - Mobile (375x667)
```

**Benefits:**
- Consistent UX across all tools
- Clear defaults
- Bounded input space
- No free-form text confusion

---

### Output Contract Patterns

#### Observation Output
```markdown
## [Observation Type]
- **Observed:** [what was seen]
- **Evidence:** [source of observation]
- **Timestamp:** [ISO 8601]
- **Confidence:** [High/Medium/Low]
```

#### Validation Output
```markdown
## Validation Result
**ValidationStatus:** [PASSED/FAILED]
**ValidationSummary:** [one-line summary]

## Detected Issues
### Critical Issues
- [issue description]

### Warnings
- [potential issue]

## Readiness Status
**Ready for Handoff:** [Yes/No]
**Blocking Issues:** [count]
```

#### Traceability Output
```markdown
## Traceability Validation Result
**TraceabilityStatus:** [PASSED/FAILED]
**TraceabilitySummary:** [one-line summary]

## Traceability Matrix
| Source | → | Target | Status |
|--------|---|--------|--------|
| [item] | → | [item] | ✓/✗    |

## Broken References
- [reference description]

## Coverage Gaps
- [gap description]
```

---

## Agent Communication Protocol

### Communication Principles

#### 1. Structured Information, Not Conversation

**DO:**
```markdown
## Business Module: User Management
**Purpose:** Manage user accounts and permissions
**Entry Point:** /admin/users
**Evidence:** Screenshot #42, DOM analysis
```

**DON'T:**
```markdown
I found a user management section that seems to handle user accounts.
It looks like it's accessible from the admin panel.
```

---

#### 2. Immutable Handoffs

**Rule:** Upstream artifacts are READ-ONLY for downstream agents.

**Planner Agent Output:**
```markdown
## Business Module: Inventory
**Pages:**
- /inventory/list
- /inventory/details/:id
```

**Test Strategy Agent (CORRECT):**
```markdown
## Test Objective: Validate Inventory Management
**Source Module:** Inventory (from Application Blueprint)
**Test Areas:**
- Inventory List Page (/inventory/list)
- Inventory Details Page (/inventory/details/:id)
```

**Test Strategy Agent (INCORRECT):**
```markdown
## Business Module: Inventory Management [MODIFIED UPSTREAM CONTENT]
**Pages:**
- /inventory/list
- /inventory/details/:id
- /inventory/reports [ADDED NEW PAGE]
```

**Downstream Extension Pattern:**
```markdown
## [Downstream Section]
**Extends:** [Upstream Section Reference]
**Additional Details:** [new information]
**Does Not Modify:** [upstream section name]
```

---

#### 3. Completeness Requirements

Every handoff must be **self-contained** with all necessary context.

**Required Metadata:**
```markdown
## Metadata
- **Planner Version:** 1.0.0
- **Blueprint Version:** 1.0.0
- **Schema Version:** 2024.1
- **Discovery Status:** Complete
- **Generated At:** 2024-01-15T10:30:00Z
- **Agent:** Planner Agent
```

**Required Sections:**
- Application Identity
- Technology Stack (if applicable)
- Main Content (modules, strategy, scenarios)
- Evidence References
- Confidence Levels
- Unknown Areas

---

#### 4. Deterministic Output

Same input must produce same output.

**Prohibited:**
- Random elements
- Timestamps in generated identifiers
- Non-deterministic ordering
- Session-dependent content

**Allowed:**
- Observation timestamps (documenting when observed)
- Discovery date (documenting when discovered)
- Version numbers
- Deterministic IDs (hash-based, sequence-based)

---

#### 5. Versioned Handoffs

Every blueprint must include version information.

```markdown
## Version Information
- **Blueprint Schema:** 2024.1
- **Agent Version:** Planner Agent 1.0.0
- **Compatibility:** Test Strategy Agent >= 1.0.0
```

**Version Changes:**
- **Major:** Breaking schema changes
- **Minor:** Backward-compatible additions
- **Patch:** Bug fixes, clarifications

---

#### 6. Evidence-Backed Claims

Every claim requires evidence.

**CORRECT:**
```markdown
## Page: Dashboard
**URL:** /dashboard
**Observable Elements:**
- Navigation menu (DOM: nav.main-menu)
- User avatar (DOM: img.avatar)
- Logout button (DOM: button#logout)
**Evidence:** Screenshot #12, DOM snapshot #4
**Confidence:** High
```

**INCORRECT:**
```markdown
## Page: Dashboard
**URL:** /dashboard
**Description:** The dashboard page contains navigation and user info.
```

---

#### 7. Unknowns as First-Class Citizens

Unknown is preferred over guessing.

```markdown
## Unknown Areas

### Unknown: Backend API Architecture
**Reason:** Network requests are obfuscated
**Impact:** Cannot determine REST vs GraphQL vs other
**Discovery Required:** Yes
**Recommendation:** Use network inspection tool with auth

### Unknown: Session Timeout Duration
**Reason:** Not observed during exploration
**Impact:** Cannot plan session expiration tests
**Discovery Required:** Yes
**Recommendation:** Monitor session over extended period
```

**Downstream Handling:**
```markdown
## Test Strategy: Session Management
**Note:** Session timeout duration unknown (ref: Application Blueprint, Unknown #2)
**Approach:** Test observable session mechanisms only
**Coverage Limitation:** Cannot test timeout scenarios
```

---

### Security Constraints

**Never Transfer:**
- Passwords (entered or observed)
- API tokens
- Session cookies
- Personal Identifiable Information (PII)
- Credit card numbers
- Private keys

**Instead, Document:**
```markdown
## Authentication Observation
**Credential Fields Observed:**
- Username field (DOM: input[name="username"])
- Password field (DOM: input[type="password"])
**Note:** No credentials were entered or stored
**Evidence:** Screenshot #8 (credentials redacted)
```

---

### Handoff Validation

Before accepting a handoff, downstream agents should validate:

1. **Metadata Present:** All required metadata included
2. **Schema Version Compatible:** Can parse the blueprint schema
3. **Evidence References Valid:** All evidence is accessible
4. **No Missing Required Sections:** All mandatory sections present
5. **Unknowns Documented:** Gaps are explicitly marked

**Validation Failure Response:**
```markdown
## Handoff Validation Failed
**Agent:** Test Strategy Agent
**Received From:** Planner Agent
**Issue:** Missing Technology Stack section
**Status:** Cannot proceed
**Required Action:** Planner must complete Application Blueprint
```

---

## Core Principles

### 1. Evidence-Based Only

**Principle:** All outputs must be grounded in observable evidence.

**Implementation:**
- Every claim cites a source (URL, screenshot, DOM selector)
- Every observation includes timestamp
- Every detection includes confidence level

**Example:**
```markdown
## Technology: React
**Observed Indicator:** window.React object present
**Evidence:** 
  - Global object inspection
  - <div id="root"> element present
  - react.development.js in network tab
**Confidence:** High
```

---

### 2. Observe, Don't Interpret

**Principle:** Report what is seen, not what it means.

**DO:**
```markdown
## Observable Element
**DOM:** button.primary (text: "Submit Order")
**Location:** Bottom right of form
**Click Behavior:** Form submission, redirect to /orders/confirmation
```

**DON'T:**
```markdown
## Element Analysis
**Interpretation:** This button completes the checkout process
**Business Logic:** It validates the cart and processes payment
```

---

### 3. Unknown is Preferred Over Guessing

**Principle:** Admitting unknowns is better than inferring.

**DO:**
```markdown
## Authentication Mechanism
**Observed:** Login form with username/password
**Unknown:** Whether SSO is supported (no visible SSO buttons)
**Confidence:** Medium (only basic auth observed)
```

**DON'T:**
```markdown
## Authentication Mechanism
**Observed:** Login form with username/password
**Conclusion:** Application only supports basic authentication
**Confidence:** High
```

---

### 4. Structured Markdown for All Blueprints

**Principle:** Use consistent markdown structure for all artifacts.

**Benefits:**
- Machine-parseable
- Human-readable
- Version-controllable
- Diffable
- Deterministic

**Structure Requirements:**
- ATX-style headers (`##` not `===`)
- Consistent heading levels
- Bullet points for lists
- Tables for matrices
- Code blocks for technical details

---

### 5. Confidence + Evidence Required

**Principle:** Every observation must include both confidence level and supporting evidence.

**Confidence Levels:**

| Level | Criteria |
|-------|----------|
| **High** | Direct observation, multiple evidence sources, unambiguous |
| **Medium** | Indirect observation, single evidence source, some ambiguity |
| **Low** | Inferred from context, limited evidence, high ambiguity |

**Example:**
```markdown
## Framework Detection: Next.js
**Confidence:** High
**Evidence:**
  1. _next directory in network requests
  2. __NEXT_DATA__ script tag in DOM
  3. next/link components in React tree
  4. Server-side rendering observed
```

---

### 6. Immutable Handoffs Between Agents

**Principle:** Once an agent produces an artifact, downstream agents treat it as read-only.

**Why:**
- Maintains clear responsibility boundaries
- Prevents contradictions
- Enables parallel work
- Supports reproducibility
- Simplifies debugging

**Extension Pattern:**
```markdown
## Test Strategy Extension
**Extends:** Application Blueprint → Business Module: Inventory
**Does Not Modify:** Application Blueprint
**Adds:** Test objectives, test areas, priority
```

---

## Application Blueprint Structure

**Location:** `playwright/planner-agent/vista-planner-kb/18_Application_Blueprint_Modeling.md`

### Complete Structure

```markdown
# Application Blueprint

## Metadata
- **Planner Version:** [version]
- **Blueprint Version:** [version]
- **Schema Version:** [version]
- **Discovery Status:** [Complete/Partial/In-Progress]
- **Generated At:** [ISO 8601 timestamp]
- **Application URL:** [base URL]

## Application Identity
- **Application Name:** [discovered or provided name]
- **Application Type:** [Web App / SPA / PWA / Multi-page]
- **Primary Domain:** [domain]
- **Discovery Date:** [date]

## Technology Stack

### Frontend Technologies
- **Framework:** [React/Angular/Vue/etc]
  - **Version:** [if detectable]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

### Build Tools
- **Tool:** [Vite/Webpack/etc]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

### UI Libraries
- **Library:** [Material UI/Bootstrap/etc]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

### State Management
- **Library:** [Redux/MobX/etc]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

### API Patterns
- **Pattern:** [REST/GraphQL/WebSocket]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

## Authentication

### Authentication Mechanisms
- **Type:** [Username/Password | SSO | OAuth]
  - **Location:** [URL or navigation path]
  - **Observable Elements:** [form fields, buttons]
  - **Evidence:** [screenshot, DOM reference]
  - **Confidence:** [High/Medium/Low]

### Session Management
- **Type:** [Cookie | JWT | Local Storage]
  - **Evidence:** [observation]
  - **Confidence:** [High/Medium/Low]

### Protected Routes
- **Route Pattern:** [pattern]
  - **Redirect Behavior:** [observed behavior]
  - **Evidence:** [observation]

## Navigation Structure

### Primary Navigation
- **Type:** [Top Nav | Side Nav | Mega Menu]
  - **Location:** [DOM selector]
  - **Items:** [list of menu items]
  - **Evidence:** [screenshot reference]

### Secondary Navigation
- **Type:** [Breadcrumbs | Tabs | Sub-menus]
  - **Location:** [DOM selector]
  - **Evidence:** [screenshot reference]

## Business Modules

### Module: [Module Name]
**Purpose:** [Observable purpose based on navigation labels and page content]
**Entry Point:** [URL or navigation path]
**Evidence:** [screenshot, DOM reference]
**Confidence:** [High/Medium/Low]

#### Page: [Page Name]
**URL Pattern:** [URL or pattern]
**Purpose:** [Observable purpose]
**Observable Elements:**
  - [Element type]: [description] (DOM: [selector])
  - [Element type]: [description] (DOM: [selector])
**Evidence:** [screenshot, DOM snapshot]
**Confidence:** [High/Medium/Low]

##### Component: [Component Name]
**Type:** [Button | Form | Table | Card | etc]
**Location:** [DOM selector]
**Behavior:** [Observable behavior]
**Evidence:** [screenshot, interaction result]
**Confidence:** [High/Medium/Low]

##### Form: [Form Name]
**Location:** [DOM selector]
**Fields:**
  - **Field:** [name] (Type: [text/email/number], Required: [Yes/No])
  - **Field:** [name] (Type: [select], Options: [list])
**Validation:** [Observable validation behavior]
**Submit Behavior:** [What happens on submit]
**Evidence:** [screenshot, DOM snapshot]
**Confidence:** [High/Medium/Low]

#### Workflow: [Workflow Name]
**Purpose:** [Observable purpose]
**Steps:**
  1. **Step:** [description] (Page: [page], URL: [url])
  2. **Step:** [description] (Page: [page], URL: [url])
**Entry Point:** [starting URL or trigger]
**Exit Point:** [ending URL or result]
**Evidence:** [screenshots of each step]
**Confidence:** [High/Medium/Low]

#### CRUD Entity: [Entity Name]
**Observable Operations:**
  - **Create:** [URL, form location, evidence]
  - **Read:** [URL, display location, evidence]
  - **Update:** [URL, form location, evidence]
  - **Delete:** [URL, trigger location, evidence]
**Data Fields:** [Observable fields]
**Evidence:** [screenshots, DOM snapshots]
**Confidence:** [High/Medium/Low]

### Module: [Module Name]
[Repeat structure for each business module]

## Dialogs and Overlays

### Dialog: [Dialog Name]
**Type:** [Modal | Drawer | Popover | Toast]
**Trigger:** [What causes it to appear]
**Location:** [Where it appears]
**Content:** [Observable content]
**Actions:** [Available buttons/actions]
**Evidence:** [screenshot]
**Confidence:** [High/Medium/Low]

## Network Observations

### API Endpoint: [Endpoint]
**Method:** [GET/POST/PUT/DELETE]
**URL Pattern:** [pattern]
**Triggered By:** [user action or page]
**Response Type:** [JSON/XML/HTML]
**Evidence:** [network log reference]
**Confidence:** [High/Medium/Low]

## Performance Observations

### Load Time
**Page:** [page name]
**Load Time:** [observed time]
**Evidence:** [performance measurement]

### Interactive Elements
**Element:** [element name]
**Response Time:** [observed time]
**Evidence:** [observation]

## Evidence

### Screenshots
- **Screenshot #1:** [description, page, timestamp]
- **Screenshot #2:** [description, page, timestamp]

### DOM Snapshots
- **Snapshot #1:** [description, page, timestamp]
- **Snapshot #2:** [description, page, timestamp]

### Network Logs
- **Log #1:** [description, endpoint, timestamp]
- **Log #2:** [description, endpoint, timestamp]

## Confidence Levels

### High Confidence Areas
- [Area]: [reason for high confidence]

### Medium Confidence Areas
- [Area]: [reason for medium confidence]

### Low Confidence Areas
- [Area]: [reason for low confidence]

## Unknown Areas

### Unknown: [Description]
**Reason:** [Why it's unknown]
**Impact:** [How it affects testing/downstream agents]
**Discovery Required:** [Yes/No]
**Recommendation:** [How to discover this information]

### Unknown: [Description]
[Repeat for each unknown]

## Discovery Completeness

**Overall Status:** [Complete / Partial / In-Progress]
**Coverage:** [Percentage or description]
**Limitations:** [What wasn't explored and why]
```

---

### Key Structure Principles

#### Hierarchical Organization
- Business Modules (parent)
  - Pages (child of module)
    - Components (child of page)
    - Forms (child of page)
  - Workflows (child of module, span multiple pages)
  - CRUD Entities (child of module)

#### Evidence Chain
Every section must reference evidence:
- Screenshots
- DOM snapshots
- Network logs
- Interaction results

#### Confidence Levels
Every observation must include confidence:
- **High:** Direct, unambiguous observation
- **Medium:** Indirect or partially ambiguous observation
- **Low:** Inferred from limited evidence

#### Unknown Documentation
Gaps in knowledge are explicitly documented:
- What is unknown
- Why it's unknown
- Impact on downstream work
- How to discover it

---

## Quick Reference

### Agent Workflow Summary

| Agent | Input | Output | Key Tools |
|-------|-------|--------|-----------|
| **Planner** | URL + Requirements | Application Blueprint | bs (browser), cs (tech), ds (auth) |
| **Test Strategy** | Application Blueprint | Testing Strategy Blueprint | es (validator), fs (traceability) |
| **Scenario Generation** | Testing Strategy Blueprint | Scenario Specification Blueprint | gs (validator), hs (traceability) |

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Exploration** | bs, cs, ds | Discover and observe application |
| **Specification Validation** | es, gs | Validate blueprint completeness and quality |
| **Traceability Validation** | fs, hs | Validate traceability chain |

### Blueprint Hierarchy

```
Application Blueprint (Immutable)
  ↓
Testing Strategy Blueprint (Immutable)
  ↓
Scenario Specification Blueprint
  ↓
Executable Test Code
```

### Core Constraints

1. **Evidence-based only** - No inference
2. **Observe, don't interpret** - Report facts
3. **Unknown preferred** - Don't guess
4. **Structured markdown** - Consistent format
5. **Confidence required** - Every observation
6. **Immutable handoffs** - Never modify upstream

### Validation Status

| Status | Meaning |
|--------|---------|
| **PASSED** | Ready for handoff to next agent |
| **FAILED** | Blocking issues must be resolved |

### Confidence Levels

| Level | Criteria |
|-------|----------|
| **High** | Direct observation, multiple sources, unambiguous |
| **Medium** | Indirect observation, single source, some ambiguity |
| **Low** | Inferred from context, limited evidence, high ambiguity |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial comprehensive reference document |

---

## Related Documentation

- Planner Agent Prompt: `playwright/planner-agent/planner-agent-prompt.md`
- Test Strategy Agent Prompt: `playwright/test-strategy-agent/test-strategy-agent-prompt.md`
- Scenario Generation Agent Prompt: `playwright/scenario-generation-agent/scenario-agent-prompt.md`
- Application Blueprint Modeling: `playwright/planner-agent/vista-planner-kb/18_Application_Blueprint_Modeling.md`
- Agent Communication Protocol: `playwright/planner-agent/vista-planner-kb/21_Agent_Communication_and_Handoff_Protocol.md`

---

**End of AAVA Console Reference**