# Knowledge Base 03
# Prioritization and Risk Framework

---

# Purpose

This knowledge base defines the methodology for prioritizing recommendations and assessing implementation risk.

The Recommendation Agent transforms technical analysis into an ordered implementation plan.

Prioritization should always be evidence-driven.

Recommendations should never be ordered arbitrarily.

---

# Objective

Receive

Execution Analysis Blueprint

↓

Evaluate Recommendations

↓

Assess Priority

↓

Assess Risk

↓

Assess Implementation Value

↓

Generate Ordered Recommendations

↓

Generate Recommendation Blueprint

---

# Philosophy

Not every recommendation deserves immediate attention.

Recommendations should be ordered according to

Business Value

Technical Importance

Operational Risk

Implementation Benefit

Confidence

Recommendations should maximize engineering impact while minimizing operational risk.

---

# Prioritization Lifecycle

Execution Analysis Blueprint

↓

Recommendation Generation

↓

Priority Assessment

↓

Risk Assessment

↓

Recommendation Ordering

↓

Implementation Roadmap

↓

Recommendation Blueprint

---

# Priority Levels

Every recommendation shall receive one priority.

Critical

High

Medium

Low

Informational

Priority should remain evidence-driven.

---

# Critical Priority

Assign Critical when

Application unavailable.

Core business workflow blocked.

Security vulnerability identified.

Authentication completely unavailable.

Database unavailable.

Infrastructure failure affects production.

Deployment blocked.

Major business outage.

Critical recommendations should normally be implemented immediately.

---

# High Priority

Assign High when

Major business workflow degraded.

High user impact.

Repeated execution failures.

High operational risk.

Shared dependency failure.

Large regression impact.

Performance significantly degraded.

High priority recommendations should be scheduled as soon as practical.

---

# Medium Priority

Assign Medium when

Localized workflow affected.

Limited user impact.

Single feature degraded.

Moderate operational risk.

Configuration improvements.

Automation improvements.

Medium priority recommendations should be planned.

---

# Low Priority

Assign Low when

Minor workflow affected.

Limited operational benefit.

Documentation improvements.

Code quality improvements.

Maintainability improvements.

Low priority recommendations may be implemented opportunistically.

---

# Informational Priority

Assign Informational when

No immediate action required.

Observation useful for awareness.

Monitoring improvement suggested.

Future optimization opportunity.

Knowledge sharing recommendation.

---

# Business Risk Assessment

Assess

Business Criticality

Operational Risk

Customer Impact

Revenue Impact

Compliance Risk

Deployment Risk

Support Impact

Business Risk Levels

Critical

High

Medium

Low

Minimal

Risk should remain proportional.

---

# Technical Risk Assessment

Assess

Application Stability

Architecture Stability

Infrastructure Stability

Deployment Stability

Data Integrity

Security

Performance

Scalability

Maintainability

Only assess evidence-supported risks.

---

# Implementation Effort

Estimate implementation effort.

Possible levels

Very Low

Low

Medium

High

Very High

Effort represents relative implementation complexity.

Do not estimate time.

Do not estimate deadlines.

---

# Recommendation Value

Assess expected value.

Examples

Improves Stability

Improves Reliability

Improves Maintainability

Improves Performance

Improves Security

Improves Monitoring

Improves Testing

Improves Deployment

Improves User Experience

Recommendations may provide multiple values.

---

# Recommendation Ordering

Recommendations should be ordered using

Priority

↓

Business Risk

↓

Technical Risk

↓

Confidence

↓

Implementation Effort

↓

Recommendation Value

Never order randomly.

---

# Dependency Assessment

Identify recommendation dependencies.

Examples

Infrastructure improvements

↓

API improvements

↓

Application improvements

↓

Automation improvements

Recommendations should respect logical implementation order.

---

# Quick Wins

Identify recommendations that

Require low implementation effort

Provide high engineering value

Reduce operational risk

Improve reliability

Quick wins should be highlighted.

---

# Strategic Improvements

Identify recommendations that

Improve long-term architecture

Reduce technical debt

Improve scalability

Improve maintainability

Improve engineering practices

Strategic improvements should remain separate from immediate fixes.

---

# Preventive Value

Assess whether recommendations

Reduce recurrence.

Improve observability.

Improve automation quality.

Improve deployment confidence.

Improve resilience.

Preventive improvements should be explicitly identified.

---

# Unknown Handling

If analysis confidence is

Low

or

Unknown

Reduce recommendation priority when appropriate.

Recommend

Further Investigation

instead of speculative implementation.

Never fabricate certainty.

---

# Traceability

Every recommendation priority shall reference

Execution Analysis Blueprint

↓

Failure Analysis

↓

Root Cause

↓

Business Impact

↓

Technical Impact

↓

Confidence

↓

Supporting Evidence

Priority without traceability should never exist.

---

# Validation

Before completion verify

Priority assigned.

Business Risk assigned.

Technical Risk assigned.

Implementation Effort assigned.

Recommendation Value assigned.

Recommendation Ordering complete.

Dependencies identified.

Quick Wins identified when applicable.

Strategic Improvements identified when applicable.

Unknown Areas preserved.

---

# Common Mistakes

Do not assign Critical without evidence.

Do not ignore implementation effort.

Do not ignore confidence.

Do not exaggerate business risk.

Do not ignore dependencies.

Do not recommend speculative work.

Do not remove uncertainty.

---

# Success Criteria

Engineering teams should understand

What should be done first.

Why it should be done first.

Which recommendations provide immediate value.

Which recommendations require strategic planning.

Which recommendations require further investigation.

without reviewing the Execution Analysis Blueprint.

---

# Final Principle

Priority determines implementation order.

Risk determines urgency.

Confidence determines certainty.

Effort determines feasibility.

Value determines importance.

The Recommendation Agent should balance all five dimensions to produce an implementation roadmap that is practical, evidence-driven, and aligned with engineering priorities.