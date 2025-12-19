---
id: 001
title: AI/Spec-Driven Book Constitution Creation
stage: constitution
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: hamza
command: /sp.constitution
labels: ["constitution", "project-setup", "governance", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

/sp.constitution
Project: AI/Spec-Driven Book Creation – Full book written with Docusaurus, Spec-Kit Plus, and Claude Code, deployed to GitHub Pages
Project codename: project1
Book delivery format: Static website built with Docusaurus v3+, deployed via GitHub Pages
Repository template: Spec-Kit Plus[](https://github.com/panaversity/spec-kit-plus/)

Core principles:
- Spec-first development: Every piece of content, chapter, and feature must originate from an approved spec in the /specs directory
- AI-native workflow: All prose, code examples, diagrams (Mermaid), and frontmatter are primarily generated or refined by Claude Code (or equivalent frontier model), then human-reviewed and committed
- Maximum truth-seeking: Technical explanations must be precise, up-to-date (2025–2026 best practices), and reflect real-world usability
- Progressive enhancement: Content must be readable and useful even with JavaScript disabled; Docusaurus features (search, dark mode, versioning) are enhancements, not requirements
- Open-source excellence: Zero proprietary lock-in, permissive licensing (MIT or CC-BY-4.0 where applicable), and easy forking/contribution

Key standards:
- Writing style: Clear, engaging, professional yet approachable (Flesch-Kincaid grade 8–10)
- Tone: Helpful mentor who assumes reader has intermediate programming knowledge but is new to AI-native workflows
- Code examples: Must be runnable, tested with latest Node.js/LTS, and include both TypeScript and JavaScript variants where meaningful
- Diagrams: Exclusively Mermaid.js (live editable)
- Citations & references: Use BibTeX + Citation.js when needed; link directly to official docs, research papers (arXiv, ACL anthology, NeurIPS, etc.), or canonical GitHub repos
- Frontmatter: Every .mdx file must use valid Docusaurus frontmatter (title, description, sidebar_position, keywords, hide_table_of_contents, etc.)
- Accessibility: WCAG 2.1 AA compliant (alt text for all images/diagrams, proper heading hierarchy, sufficient color contrast)
- Versioning: Main branch always reflects latest stable book; drafts live in dated spec branches

Constraints:
- Primary tools: Docusaurus 3+, Spec-Kit Plus, Claude Code (or Grok-4/Claude-3.5+), GitHub Actions for CI/CD
- No external hosting dependencies except GitHub Pages (free tier)
- No paid fonts, icons, or assets (use Google Fonts, Font Awesome Free, or Docusaurus built-ins only)
- Total repository size: < 500 MB (including images and generated site)
- Build time on GitHub Actions: < 8 minutes
- Lighthouse scores (mobile): Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95

Success criteria:
- GitHub Pages site is live and passes validation (no 404s, proper CNAME if custom domain used)
- All specs in /specs directory are marked as "approved" or "implemented"
- Zero dead links (checked via Lychee or Docusaurus link checker)
- Full-text search works instantly via Algolia DocSearch (free) or local search
- At least 95 % of prose passes final human review for clarity and accuracy
- Repository contains a complete CONTRIBUTING.md and SPEC-WRITING.md derived from Spec-Kit Plus templates
- At least one reader (external) can follow the book end-to-end and successfully replicate the AI-native workflow on their own machine

Deliverables:
- Fully functional Docusaurus book at https://<username>.github.io/project1/ (or custom domain)
- Complete spec history showing AI → human refinement loop
- Final "Book Published" announcement post on X/Hacker News with link

## Response snapshot

Created project constitution version 1.0.0 for AI/Spec-Driven Book Creation project (codename: project1).

Constitution includes seven core principles:
1. Spec-First Development - All content must originate from approved specs
2. AI-Native Workflow - AI tools generate content, humans review for accuracy
3. Maximum Truth-Seeking - Technical explanations must be precise and current
4. Progressive Enhancement - Content accessible without JavaScript
5. Open-Source Excellence - MIT/CC-BY-4.0 licensing, zero proprietary lock-in
6. Accessibility & Standards - WCAG 2.1 AA compliance required
7. Performance & Constraints - Strict resource and performance budgets

Added comprehensive sections:
- Development Workflow (5-phase content creation process)
- Documentation Standards (writing style, tone, code examples, diagrams)
- Testing & Validation (code testing, link validation, accessibility audits)
- Quality Gates (6 gates that must pass before merge)
- Governance (amendment process, compliance enforcement, continuous improvement)

All existing templates (plan-template.md, spec-template.md, tasks-template.md) were reviewed and confirmed to align with new constitution principles. No template updates required.

## Outcome

- ✅ Impact: Project constitution established with clear governance, principles, and quality standards
- 🧪 Tests: N/A (constitution is a governance document)
- 📁 Files: Created/updated .specify/memory/constitution.md (version 1.0.0)
- 🔁 Next prompts: Create initial spec for book structure, setup Docusaurus project, configure GitHub Pages deployment
- 🧠 Reflection: Constitution provides strong foundation for AI-native book creation with clear quality gates and accessibility requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, principles aligned with project goals
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Monitor constitution compliance during first feature implementation
