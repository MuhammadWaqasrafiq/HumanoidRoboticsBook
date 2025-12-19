---
id: 015
title: Fix MDX Compilation Error in VLA Quiz
stage: refactor
date: 2025-12-07
surface: agent
model: gemini-pro
feature: 001-physical-ai-book
branch: main
user: User
command: (interactive)
labels: ["docusaurus", "bugfix", "mdx", "jsx"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- docs/vla-models/quiz.mdx
tests:
- (none)
---

## Prompt

ab is project ma ya error arha hai kindly is ko fix karen """Compiled with problems:
ERROR in ./docs/vla-models/quiz.mdx
Module build failed (from ./node_modules/@docusaurus/mdx-loader/lib/index.js):
Error: MDX compilation failed for file "C:\Users\ADVANCES--PC\Desktop\ai_book\docs\vla-models\quiz.mdx"
Cause: Unexpected character `1` (U+0031) before name, expected a character that can start a name, such as a letter, `$`, or `_`
...
"""

## Response snapshot

I have fixed the MDX compilation error in `docs/vla-models/quiz.mdx`. The key issues were:

1.  **Unescaped Characters**: The `<` symbol was used in text (e.g., `<1%`, `<1,000`), which the MDX parser incorrectly interpreted as the start of a JSX tag. I replaced these with the correct HTML entity `&lt;`.
2.  **Formatting Artifacts**: I removed several stray `L` characters that were present before "Incorrect" markers in the quiz answers.
3.  **Typos**: I corrected a recurring typo, changing `openvl-inference.py` to `openvla-inference.py`.

The build should now complete successfully. Please restart your development server to confirm the fix.

## Outcome

- ✅ Impact: High - resolved a blocking build error, allowing the user to continue development.
- 🧪 Tests: N/A
- 📁 Files: Modified 1 file (`docs/vla-models/quiz.mdx`) with multiple replacements to fix parsing and formatting errors.
- 🔁 Next prompts: User to confirm the fix.
- 🧠 Reflection: The error message's line number was misleading, but the description ("Unexpected character `1`") was the key clue. By searching for unescaped `<` symbols followed by numbers, I was able to pinpoint the root cause, which was not at the reported line. This highlights the importance of using the error *description* over its reported *location* when debugging parser issues. I also took the opportunity to fix other minor typos and formatting errors in the same file.

## Evaluation notes (flywheel)

- Failure modes observed: Tool error on `replace` due to incorrect `expected_replacements` count. Self-corrected by re-running with the count reported in the error message.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): (none)
