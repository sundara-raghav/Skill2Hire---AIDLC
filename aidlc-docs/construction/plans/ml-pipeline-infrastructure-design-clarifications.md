# Infrastructure Design Clarifications: ML Pipeline Unit

## Overview

This document addresses ambiguities and conflicts detected in the infrastructure design answers.

**Unit**: ml-pipeline  
**Date**: 2026-05-05  
**Status**: Awaiting Clarifications

---

## Detected Ambiguities

### Ambiguity 1: Training Trigger Frequency (Q6)

**Question**: What triggers will initiate training runs?

**Your Answer**: B) Push to main branch only

**Conflict**: The NFR Requirements document states "frequent retraining (daily or on every code push)" which suggests both push triggers AND scheduled daily triggers.

**Clarification Needed**: Should we include a daily scheduled trigger in addition to push triggers?

**Options**:
- A) Keep push-only trigger (your answer) - Training only happens when code is pushed
- B) Add daily schedule trigger - Training happens on push AND daily at midnight
- C) Daily schedule only - Training happens daily regardless of pushes

**Recommendation**: Option B aligns with NFR requirements ("daily or on push") and ensures models are retrained regularly even without code changes.

[Answer]: b

---

### Ambiguity 2: Training Artifact Preservation (Q17 vs Q8)

**Question Q8**: What logging infrastructure will capture training logs?  
**Your Answer Q8**: A) File-based logging (training.log) committed to Git

**Question Q17**: What artifact storage will preserve training artifacts for debugging?  
**Your Answer Q17**: D) No artifact preservation (logs only)

**Conflict**: Q8 commits logs to Git (persistent), but Q17 says "no artifact preservation". This creates inconsistency about what gets preserved.

**Clarification Needed**: What artifacts should be preserved?

**Options**:
- A) Commit logs to Git, no other artifacts (Q8 answer takes precedence)
- B) Commit logs + reports to Git, no intermediate artifacts
- C) Use GitHub Actions artifacts (90-day retention) for logs/reports, nothing in Git
- D) No artifact preservation at all (logs only in GitHub Actions, not committed)

**Recommendation**: Option B - Commit logs and evaluation reports to Git for permanent history, skip intermediate artifacts.

[Answer]: c

---

### Ambiguity 3: Parallel Training Infrastructure (Q20)

**Question**: What infrastructure supports parallel model training?

**Your Answer**: C) Multiple CI/CD runners in parallel

**Conflict**: The NFR Design document explicitly states "Process Pool Parallelization Pattern" using "Joblib multiprocessing on single machine (use all CPU cores)". Multiple CI/CD runners would be a different approach.

**Clarification Needed**: How should parallel training be implemented?

**Options**:
- A) Joblib multiprocessing on single GitHub Actions runner (NFR Design approach)
- B) Multiple GitHub Actions runners in parallel (your answer) - Each runner trains one model
- C) Hybrid - Joblib on single runner, but allow multiple workflow runs in parallel

**Recommendation**: Option A aligns with NFR Design and is simpler. Multiple runners adds complexity and may not be faster (overhead of runner startup).

**Technical Note**: 
- Option A: Single runner, 4 models train in parallel using joblib (3-4x speedup)
- Option B: 4 runners, each trains 1 model (potential speedup, but runner startup overhead ~30s)

[Answer]: c

---

## Clarification Summary

Once all clarifications are resolved, this section will summarize the final infrastructure decisions.

[To be completed after clarifications are provided]

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-05-05
- **Status**: Awaiting Clarifications
- **Next**: Update infrastructure-design-plan.md with resolved answers

