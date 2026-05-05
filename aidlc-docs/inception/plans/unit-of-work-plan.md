# Unit of Work Plan: Skill2Hire - Placement Prediction AI Web App

## Purpose
Decompose the Skill2Hire system into manageable units of work for parallel development and clear ownership boundaries.

---

## Context

### From Execution Plan
The execution plan identified **4 potential units**:
1. **ML Pipeline** - Dataset generation, model training, evaluation
2. **Backend API** - Flask endpoints, business logic, Supabase integration
3. **Frontend** - UI components, forms, visualizations, resume upload
4. **DevOps** - Docker, GitHub Actions, deployment configuration

### From Application Design
**21 components** organized in hybrid layered/feature-based architecture:
- Presentation Layer: 1 component
- API Layer: 5 components
- Business Logic Layer: 6 components
- ML Layer: 2 components
- Data Access Layer: 1 component
- Infrastructure Layer: 4 components
- Utilities: 2 components

### Project Type
**Greenfield** - New project with no existing codebase

---

## Unit of Work Plan

### Phase 1: Define Unit Boundaries

- [x] **1.1 Identify Units of Work**
  - [x] Define ML Pipeline unit scope and responsibilities
  - [x] Define Backend API unit scope and responsibilities
  - [x] Define Frontend unit scope and responsibilities
  - [x] Define DevOps unit scope and responsibilities

- [x] **1.2 Map Components to Units**
  - [x] Assign each of the 21 components to appropriate units
  - [x] Ensure no component is orphaned
  - [x] Verify component assignments align with unit responsibilities

### Phase 2: Define Unit Dependencies

- [x] **2.1 Identify Inter-Unit Dependencies**
  - [x] Map dependencies between ML Pipeline and Backend API
  - [x] Map dependencies between Backend API and Frontend
  - [x] Map dependencies between all units and DevOps
  - [x] Identify shared resources and integration points

- [x] **2.2 Create Dependency Matrix**
  - [x] Document which units depend on which
  - [x] Specify dependency types (build-time, runtime, deployment)
  - [x] Identify critical path dependencies

### Phase 3: Map Stories to Units (If Stories Exist)

- [x] **3.1 Review User Stories**
  - [x] Check if user stories were generated
  - [x] If no stories, skip to Phase 4

- [x] **3.2 Assign Stories to Units** (If stories exist)
  - [x] SKIPPED - No user stories generated

### Phase 4: Define Code Organization (Greenfield)

- [x] **4.1 Determine Deployment Model**
  - [x] Single monolithic deployment vs multiple deployable units
  - [x] Directory structure for chosen model
  - [x] Module organization within units

- [x] **4.2 Document Code Structure**
  - [x] Define directory layout
  - [x] Specify file organization patterns
  - [x] Document naming conventions

### Phase 5: Generate Unit Artifacts

- [x] **5.1 Generate unit-of-work.md**
  - [x] Document all units with names, purposes, and responsibilities
  - [x] List components assigned to each unit
  - [x] Include code organization strategy (greenfield)

- [x] **5.2 Generate unit-of-work-dependency.md**
  - [x] Create dependency matrix showing unit relationships
  - [x] Document integration points and shared resources
  - [x] Specify dependency types and critical paths

- [x] **5.3 Generate unit-of-work-story-map.md** (If stories exist)
  - [x] SKIPPED - No user stories, map components directly

### Phase 6: Validation

- [x] **6.1 Validate Unit Boundaries**
  - [x] Ensure units have clear, non-overlapping responsibilities
  - [x] Verify all components are assigned
  - [x] Check for appropriate unit size and complexity

- [x] **6.2 Validate Dependencies**
  - [x] Check for circular dependencies
  - [x] Verify integration points are well-defined
  - [x] Ensure dependencies are manageable

---

## Decomposition Questions

Please answer the following questions to guide the unit decomposition strategy.

### Question 1: Unit Decomposition Approach
How should the system be decomposed into units of work?

A) **4 Separate Units** - ML Pipeline, Backend API, Frontend, DevOps as independent units
B) **3 Units** - Combine Backend API + ML Pipeline into single backend unit
C) **2 Units** - Combine Backend + ML + DevOps into backend, Frontend separate
D) **Single Unit** - Monolithic application with logical modules
E) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 2: ML Pipeline Unit Scope
What should the ML Pipeline unit include?

A) **Full ML Lifecycle** - Dataset generation, preprocessing, training, evaluation, model versioning
B) **Training Only** - Assume dataset exists, focus on training and evaluation
C) **Minimal** - Just model training scripts, manual dataset creation
D) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 3: Backend API Unit Scope
Should the Backend API unit include ML model inference?

A) **Yes - Integrated** - Backend loads and uses ML models directly (MLModelManager in backend)
B) **No - Separate** - ML Pipeline exposes inference API, Backend calls it
C) **Hybrid** - Backend loads models but ML Pipeline handles training
D) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 4: Frontend Unit Independence
How independent should the Frontend unit be from Backend?

A) **Fully Independent** - Frontend can be developed/deployed separately, uses API contract
B) **Loosely Coupled** - Frontend depends on Backend for development, but separate deployment
C) **Tightly Coupled** - Frontend served by Backend (Flask templates or static files)
D) Other (please describe after [Answer]: tag below)

[Answer]: c

---

### Question 5: DevOps Unit Scope
What should the DevOps unit include?

A) **Full CI/CD** - Docker, GitHub Actions, deployment scripts, infrastructure config
B) **Deployment Only** - Docker and deployment scripts, CI/CD separate
C) **Minimal** - Just Dockerfile, manual deployment
D) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 6: Shared Components Placement
Where should shared components (Logger, ConfigManager, CacheManager) reside?

A) **Backend Unit** - All shared infrastructure in Backend, Frontend uses API
B) **Separate Shared Module** - Create shared/common unit for utilities
C) **Duplicated** - Each unit has its own implementation
D) **Backend + Frontend Split** - Backend has server-side shared, Frontend has client-side shared
E) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 7: Database Access
How should database access be organized across units?

A) **Backend Only** - Only Backend API unit accesses Supabase directly
B) **Backend + ML Pipeline** - Both Backend and ML Pipeline access database
C) **All Units** - Frontend, Backend, ML Pipeline all access Supabase
D) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 8: Development Sequence
What order should units be developed in?

A) **Sequential** - ML Pipeline → Backend API → Frontend → DevOps
B) **Parallel** - All units developed simultaneously with integration points defined
C) **Backend-First** - Backend + ML Pipeline → Frontend → DevOps
D) **ML-First** - ML Pipeline → Backend + Frontend parallel → DevOps
E) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 9: Integration Testing Strategy
How should integration between units be tested?

A) **Per-Unit Integration Tests** - Each unit tests its integration points
B) **Dedicated Integration Test Suite** - Separate test suite for cross-unit integration
C) **End-to-End Tests Only** - Full system tests cover integration
D) **Hybrid** - Per-unit integration tests + E2E tests
E) Other (please describe after [Answer]: tag below)

[Answer]: d

---

### Question 10: Code Organization (Greenfield)
What directory structure should be used?

A) **Monorepo with Separate Directories** - Single repo, separate dirs for each unit
B) **Multi-Repo** - Separate repository for each unit
C) **Flat Structure** - Single directory with modules for each unit
D) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 11: Deployment Model
How should the units be deployed?

A) **Single Container** - All units in one Docker container
B) **Multiple Containers** - Separate container per unit
C) **Hybrid** - Backend + ML in one container, Frontend separate
D) Other (please describe after [Answer]: tag below)

[Answer]: c

---

### Question 12: Story Assignment (If Stories Exist)
Since User Stories stage was skipped, how should work be organized?

A) **Use Requirements as Stories** - Treat each functional requirement as a story
B) **Create Implicit Stories** - Derive stories from requirements for unit mapping
C) **Skip Story Mapping** - Map components directly to units without story layer
D) Other (please describe after [Answer]: tag below)

[Answer]: c

---

## Instructions

1. **Answer all questions** by filling in the letter choice (A, B, C, D, E) after each `[Answer]:` tag
2. **For "Other" choices**, provide a detailed description of your preferred approach
3. **Consider the requirements** and application design when making decisions
4. **Think about development workflow**, team structure, and deployment strategy
5. **Let me know when done** so I can analyze your answers and proceed with generation

---

**Status**: Awaiting user input

