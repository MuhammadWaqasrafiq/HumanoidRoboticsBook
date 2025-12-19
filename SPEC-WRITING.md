# Specification Writing Guide

This guide explains how to write specifications for new chapters, features, or content additions to the Physical AI & Humanoid Robotics book using the **Spec-First Development** approach.

## 📋 Why Spec-First?

From our project constitution:

> **Core Principle I**: Every piece of content, chapter, and feature MUST originate from an approved spec in the `/specs` directory.

Specs ensure:
- **Clarity**: Explicit learning objectives and success criteria before writing
- **Consistency**: All chapters follow the same quality standards
- **Traceability**: Link implementation back to requirements
- **Quality**: Validate completeness before content creation begins

## 🗂️ Spec Structure

All specs live in `/specs/<feature-id>-<feature-name>/` and include:

### Required Files

1. **`spec.md`** - Feature specification (what to build)
2. **`plan.md`** - Implementation plan (how to build it)
3. **`tasks.md`** - Task breakdown (execution steps)

### Optional Files

4. **`research.md`** - Research findings and technical decisions
5. **`data-model.md`** - Content entities and relationships
6. **`contracts/`** - Chapter schemas and validation rules
7. **`checklists/`** - Quality validation checklists

## 📝 Writing a Spec (spec.md)

### Template Structure

```markdown
# Feature Specification: [Chapter/Feature Name]

**Feature Branch**: `<branch-name>`
**Created**: YYYY-MM-DD
**Status**: Draft | Approved | Implemented

## Overview

[1-2 sentence summary of what this chapter/feature delivers]

## User Scenarios & Testing

### User Story 1 - [Title] (Priority: P1/P2/P3)

[Description of what the reader accomplishes]

**Why this priority**: [Justification]

**Independent Test**: [How to verify this works standalone]

**Acceptance Scenarios**:
1. **Given** [context], **When** [action], **Then** [outcome]
2. ...

## Requirements

### Functional Requirements

- **FR-001**: Content MUST include [specific requirement]
- **FR-002**: All code examples MUST be tested on [platform]
- ...

### Non-Functional Requirements

- **NFR-001**: Chapter MUST meet Flesch-Kincaid grade 8-10 readability
- **NFR-002**: All diagrams MUST be in Mermaid.js format
- ...

## Success Criteria

- **SC-001**: Reader can [measurable outcome] in under [time/attempts]
- **SC-002**: [Quantifiable metric] achieves [threshold]
- ...

## Key Entities

- **Entity Name**: [Description and attributes]
- ...

## Constraints

- Chapter length: [target word count or page count]
- Required diagrams: [minimum number]
- Code examples: [minimum number, languages]
- ...

## Out of Scope

[Explicitly list what is NOT included]

## Risks

1. **Risk**: [Description]
   - **Mitigation**: [How to address]

## Notes

[Any additional context or considerations]
```

### Example: Chapter Specification

```markdown
# Feature Specification: Chapter 10 - VLA Models

**Feature Branch**: `010-vla-models`
**Created**: 2025-12-04
**Status**: Draft

## Overview

Chapter 10 teaches readers to integrate Vision-Language-Action models into their humanoid robots, enabling natural language command execution.

## User Scenarios & Testing

### User Story 1 - Deploy VLA Pipeline (Priority: P1)

A reader implements the complete VLA stack enabling their humanoid to interpret visual scenes and execute natural language commands like "Pick up the red cup."

**Why this priority**: Core capability of "Physical AI" - connecting language to actions

**Independent Test**: Reader deploys OpenVLA-7B, inputs "Pick up red cup" command, robot successfully performs task with 80%+ success rate on 20 test scenarios

**Acceptance Scenarios**:
1. **Given** OpenVLA-7B installed, **When** reader inputs natural language command, **Then** system generates correct action sequence
2. **Given** 12GB VRAM constraint, **When** using 8-bit quantization, **Then** model runs with <3 second inference latency
3. **Given** 20 test commands, **When** executing full pipeline, **Then** achieves 16+ successful completions (80%)

## Requirements

### Functional Requirements

- **FR-001**: Chapter MUST cover OpenVLA-7B as primary model with Octo and RT-2-X as alternatives
- **FR-002**: Chapter MUST include working code example for model loading and inference
- **FR-003**: Chapter MUST provide quantization guide for VRAM-constrained systems
- **FR-004**: All code examples MUST be tested on Ubuntu 22.04 with RTX 4070 Ti (12GB VRAM)

### Non-Functional Requirements

- **NFR-001**: Chapter target length: 4,000-6,000 words
- **NFR-002**: Minimum 4-6 Mermaid.js diagrams (VLA architecture, model comparison, inference flow)
- **NFR-003**: Embedded quiz with 7-10 questions
- **NFR-004**: Estimated reading time: 3-4 hours

## Success Criteria

- **SC-001**: Reader successfully loads OpenVLA-7B and performs inference on test image+command
- **SC-002**: Reader achieves <3 second end-to-end latency for voice → VLA → action pipeline
- **SC-003**: Reader scores 80%+ on embedded quiz

## Key Entities

- **VLAModel**: name, size, VRAM requirement, latency, license, repository URL
- **CodeExample**: language, file path, expected output, dependencies
- **Diagram**: type (architecture/flow/comparison), Mermaid.js code, alt text

## Constraints

- Total chapter assets: <50 MB
- Code examples: Minimum 3 (model loading, inference, quantization)
- External dependencies: Must be open-source and freely available
- No cloud-only solutions (cloud as optional fallback only)

## Out of Scope

- Custom VLA model training (reference external resources)
- Proprietary VLA models (RT-1, PaLM-E) - mention but don't implement
- Production deployment patterns (focus on educational lab environment)
- Multi-robot coordination (single humanoid only)

## Risks

1. **Risk**: OpenVLA-7B API changes after publication
   - **Mitigation**: Pin specific version in requirements, maintain "Updates" page

2. **Risk**: Model requires >12GB VRAM despite quantization
   - **Mitigation**: Provide Octo-Base lightweight alternative (<6GB VRAM)

3. **Risk**: VLA research moves faster than publication timeline
   - **Mitigation**: Focus on principles, mark "2026 SOTA" sections clearly

## Notes

- Research Phase 0 R3 findings inform model selection
- Integrate with Chapter 11 (voice pipeline) and Chapter 13 (capstone)
- Troubleshooting Bible should include VLA-specific errors (10+ entries)
```

## ✅ Spec Quality Checklist

Before marking spec as "Approved":

### Completeness
- [ ] All user stories have priorities (P1/P2/P3)
- [ ] Each story has independent test criteria
- [ ] Acceptance scenarios use Given/When/Then format
- [ ] Success criteria are measurable (numbers, percentages, time limits)
- [ ] All [NEEDS CLARIFICATION] markers resolved

### Clarity
- [ ] No ambiguous terms ("fast", "good", "many")
- [ ] Specific platforms/versions mentioned (Ubuntu 22.04, ROS 2 Iron)
- [ ] Quantifiable thresholds stated (80% success rate, <3s latency)
- [ ] Out of scope explicitly defined

### Testability
- [ ] Every requirement can be verified through testing or inspection
- [ ] Success criteria directly map to user story outcomes
- [ ] Acceptance scenarios are concrete and executable

### Alignment
- [ ] Follows project constitution principles
- [ ] Consistent with existing chapters (tone, structure, quality)
- [ ] Integrates with broader book narrative

## 🔄 Spec Workflow

### 1. Draft Spec

Create `specs/<feature-id>-<name>/spec.md` with:
- Status: **Draft**
- All required sections filled
- [NEEDS CLARIFICATION] markers for unknowns

### 2. Review & Refine

- Run `/sp.clarify` to identify underspecified areas
- Resolve clarifications with stakeholders
- Update spec with decisions

### 3. Approve Spec

- Complete quality checklist
- Mark status: **Approved**
- Commit to git on feature branch

### 4. Create Plan

- Run `/sp.plan` to generate implementation plan
- Review plan.md for architecture and phasing
- Identify ADR candidates for significant decisions

### 5. Generate Tasks

- Run `/sp.tasks` to create task breakdown
- Review tasks.md for completeness
- Begin implementation

### 6. Mark Implemented

- After all tasks complete
- Update status: **Implemented**
- Link to deployed content (chapter URL)

## 📐 Best Practices

### User Stories

✅ **Good**: "A reader implements balance controller keeping humanoid stable during push perturbations (recovery within 1.5 seconds)"

❌ **Bad**: "A reader understands balance control"

**Why**: First is testable and measurable, second is vague

### Success Criteria

✅ **Good**: "SC-001: Reader completes workstation setup in under 4 hours (verified by beta tester)"

❌ **Bad**: "SC-001: Workstation setup is easy"

**Why**: First has quantifiable metric and verification method

### Requirements

✅ **Good**: "FR-003: All code examples MUST be tested on Ubuntu 22.04 + ROS 2 Iron + Isaac Sim 2025.1+"

❌ **Bad**: "FR-003: Code examples should work on most systems"

**Why**: First specifies exact platform, second is ambiguous

### Constraints

✅ **Good**: "Total chapter assets: <50 MB, Code examples: Minimum 3"

❌ **Bad**: "Keep chapter reasonably sized with enough examples"

**Why**: First is measurable, second is subjective

## 🔗 Integration with Tasks

Specs connect to implementation through task organization:

```
spec.md
  └─ User Story 1 (P1)
      └─ tasks.md: Phase 3 (US1 tasks)
          ├─ T023: Research task
          ├─ T024-T026: Implementation tasks
          └─ Checkpoint: US1 complete
  └─ User Story 2 (P2)
      └─ tasks.md: Phase 4 (US2 tasks)
          ...
```

Each user story in spec.md maps to a phase in tasks.md, enabling independent development and testing.

## 📚 Examples

See existing specs:
- `/specs/001-physical-ai-book/spec.md` - Book-level specification
- `/specs/001-physical-ai-book/plan.md` - Implementation architecture
- `/specs/001-physical-ai-book/tasks.md` - 194-task breakdown

## 🆘 Getting Help

- **Questions**: Open GitHub Discussion
- **Spec review**: Tag maintainers in PR
- **Template issues**: Report in GitHub Issues

---

**Remember**: "Weeks of coding can save you hours of planning" - invest time in clear specs upfront!
