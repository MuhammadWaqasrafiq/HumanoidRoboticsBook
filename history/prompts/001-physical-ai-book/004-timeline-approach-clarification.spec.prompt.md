---
id: 004
title: Timeline Approach Clarification and Adjustment
stage: spec
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-physical-ai-book
branch: 001-physical-ai-book
user: hamza
command: /sp.clarify
labels: ["clarification", "timeline", "hackathon", "completion-driven", "scope-preservation"]
links:
  spec: specs/001-physical-ai-book/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-physical-ai-book/spec.md
  - specs/001-physical-ai-book/plan.md
tests:
  - Timeline Constraints section validation (spec.md)
  - Timeline Overview section validation (plan.md)
  - Phase milestone consistency check (all 4 phases updated)
---

## Prompt

User clarification sequence (3 messages):

**Message 1**: "The timeline you created for me has a problem. I only have 2 days to write this book, but you made a 90-day plan. Please correct it."

**Message 2**: "The timeline you created is too long. I received this project for a hackathon, and I want to complete it as quickly as possible. Please correct both the specified timeline and the plan so that we do not follow a day-by-day schedule. Instead, I will do as much work as I can in one day, and if anything is left, I'll continue on the second day. If it still isn't finished, I'll complete it on the third day."

**Message 3 (Final Intent)**: "We will keep everything in the specification and plan the same, except for the timeline. We won't follow a fixed timeline anymore. Instead, we will work every day until the project is complete. So please adjust the timeline accordingly in both the specification and the plan."

## Response snapshot

Addressed timeline concern through three-stage clarification process:

**Stage 1: Source Clarification**
- Explained that 90-day timeline came from user's original `/sp.specify` input (not arbitrary decision)
- Original spec explicitly stated: "Timeline (aggressive hackathon-ready): Spec approval: Day 0 (today), First 6 chapters draft: +21 days, Full first draft: +60 days, Public beta launch: +75 days, Final polished version: +90 days"

**Stage 2: Hackathon MVP Analysis**
- Asked clarifying question about hackathon deliverable target
- Presented 4 options (A: MVP Prototype, B: Working Prototype, C: Full Book Fast-Track, D: Hybrid Approach)
- Recommended Option B: Working Prototype with 3-4 chapters + 1 impressive VLA demo

**Stage 3: User Intent Resolution (CRITICAL)**
- User clarified: Keep FULL scope (13 chapters + 3 appendices + capstone) unchanged
- Change approach: Fixed calendar dates → Completion-driven sprint (work daily until done)
- Updated both spec.md and plan.md:

**spec.md changes** (Timeline Constraints section, lines 283-296):
```markdown
**Approach**: Completion-driven sprint (work continuously until project complete, no fixed calendar deadlines)

**Phases** (completed sequentially, duration flexible based on daily progress):
- **Phase 1 - Foundation**: Chapters 01-06 (ROS 2 + simulation fundamentals)
- **Phase 2 - Core Robotics**: Chapters 07-09 (perception, locomotion, manipulation)
- **Phase 3 - Intelligence Layer**: Chapters 10-12 (VLA models, voice pipeline, sim-to-real)
- **Phase 4 - Synthesis & Polish**: Chapter 13 + Appendices A, B, C + capstone project + final audit

**Started**: 2025-12-04 (spec approval)
**Target Completion**: When all success criteria met (estimated 1-3 months intensive work, actual duration varies)

**Daily Workflow**: Work on highest-priority incomplete phase until done, then advance to next phase. No fixed daily targets.
```

**plan.md changes** (8 sections updated):
1. Timeline Overview section - Replaced 90-day Gantt chart with phase sequencing Mermaid diagram, removed all calendar dates
2. Phase 1 milestones - Changed from "Day 0-21" to "complete in order, no fixed dates"
3. Phase 2 milestones - Changed from "Day 22-45" to "complete in order, no fixed dates"
4. Phase 3 milestones - Changed from "Day 46-70" to "complete in order, no fixed dates"
5. Phase 4 milestones - Changed from "Day 71-90" to "complete in order, no fixed dates"
6. Risk mitigation - Changed trigger from "Day 75 MVP" to "scope fatigue or quality degradation"
7. Estimated effort - Changed from "90 days" to "55-80 working days (1-3 months depending on work intensity)"
8. Notes section - Updated final note to reflect completion-driven approach

**Key Design Decision**: Preserved full scope while making timeline flexible (user explicitly requested this approach over scope reduction)

## Outcome

- ✅ Impact: Successfully resolved timeline concern while preserving full project scope; transformed fixed-date 90-day plan into flexible completion-driven sprint approach suitable for hackathon-style intensive work
- 🧪 Tests: All timeline references verified consistent across spec.md and plan.md; no calendar dates remain except project start (2025-12-04)
- 📁 Files: Updated spec.md (Timeline Constraints section), plan.md (8 sections including all 4 phase milestones)
- 🔁 Next prompts: `/sp.tasks` to generate detailed task breakdown based on updated completion-driven plan
- 🧠 Reflection: Important clarification revealed user intent was not scope reduction (hackathon MVP) but timeline flexibility (completion-driven). Original 90-day estimate came from user's `/sp.specify` input, not arbitrary planning decision. Resolution preserves full ambition while removing calendar pressure.

## Evaluation notes (flywheel)

- Failure modes observed: Initial misunderstanding - assistant attempted to resolve as scope reduction problem when user actually wanted timeline approach change (calendar-driven → completion-driven)
- Graders run and results (PASS/FAIL):
  - Timeline Consistency Check: PASS (all calendar dates removed except start date, all phases now "complete in order, no fixed dates")
  - Scope Preservation Check: PASS (full scope maintained: 13 chapters + 3 appendices + capstone project)
  - User Intent Alignment: PASS (user explicitly confirmed: "keep everything in the specification and plan the same, except for the timeline")
  - Overall: CLARIFICATION RESOLVED, READY FOR TASK GENERATION
- Prompt variant (if applicable): Three-stage clarification process (source explanation → MVP options → final resolution)
- Next experiment (smallest change to try): During `/sp.tasks` generation, consider whether task breakdown should include estimated effort per task (hours/days) to help user track daily progress in completion-driven approach, or if effort estimates would create unwanted calendar pressure

