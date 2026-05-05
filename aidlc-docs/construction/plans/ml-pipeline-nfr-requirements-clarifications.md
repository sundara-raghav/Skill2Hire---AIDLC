# NFR Requirements Clarifications: ML Pipeline Unit

## Purpose
Resolve conflicts and ambiguities detected in NFR requirements plan answers.

---

## Clarifications Required

### Clarification 1: Training Failure Handling Conflict (Q8)

**Issue**: Your answer conflicts with the functional design.

**Your Answer**: Q8 - "A) Fail Fast" - Stop entire pipeline, alert developer

**Functional Design**: The business logic model (Section 7.1) and business rules (RULE-EH-001) already define error handling as "Continue on error - Skip failed model, continue with others"

**Question**: Do you want to:

A) **Keep Functional Design** - Use "Continue on error" as already defined (recommended for resilience)
B) **Override to Fail Fast** - Change functional design to fail fast on any model training error
C) **Hybrid** - Fail fast on critical errors (data generation, preprocessing), continue on model-specific errors

[Answer]: c

---

### Clarification 2: Dependency Pinning vs Reproducibility Conflict (Q11 & Q18)

**Issue**: Your answers are contradictory.

**Your Answer Q11**: "D) No Pinning" - Use latest versions
**Your Answer Q18**: "A) Critical" - Must be able to reproduce exact results (fixed random seeds, version pinning)

**Problem**: Critical reproducibility REQUIRES exact version pinning. Without pinning scikit-learn versions, model training results will vary as dependencies update, making exact reproducibility impossible.

**Question**: Which is your priority?

A) **Reproducibility** - Change Q11 to "A) Exact Pinning" to support critical reproducibility
B) **Latest Versions** - Change Q18 to "B) Important" or "C) Not Critical" to allow version flexibility
C) **Compromise** - Use "B) Minor Version Pinning" for Q11 (allows patches, blocks breaking changes)

[Answer]: c

---

## Instructions

1. Answer both clarification questions
2. Provide letter choice (A, B, C) after each `[Answer]:` tag
3. Type **"done"** when you've completed both clarifications

---

**Status**: Awaiting clarification
