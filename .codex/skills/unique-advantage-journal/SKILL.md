---
name: unique-advantage-journal
description: Structured workflow for formally recording clarified personal cases or hypothesis notes, maintaining the unique-advantage archive, and reviewing archived evidence with a fixed three-point definition. Use when the user explicitly wants to save a case or note, confirms that an explored case is ready to be written, wants archive maintenance through the recording workflow, or wants a pattern review across archived entries. If the user mainly wants to talk through a messy new case first, use $unique-advantage-explorer before this skill.
---

# Unique Advantage Journal

## Overview

Use this skill to turn clarified material into a consistent archive and to keep all archive work anchored to one fixed definition of personal unique advantage.

Default to the user's language. If the user writes in Chinese, think and answer in Chinese unless asked otherwise.

This skill is an archive writer, not the default place for open-ended exploration. If the user has not clearly asked to record something and the case is still messy, stay light and route the conversation to `$unique-advantage-explorer`.

## Fixed Definition

Treat the user's unique advantage as defined by exactly three criteria:

- long-term sustainability: the user can keep doing this kind of work over time
- faster learning: the user reaches competence faster than most people on similar tasks
- better results with external validation: the output is stronger and reality confirms it through trust, selection, feedback, responsibility, ranking, payment, or repeated requests

Do not add extra "core definition" factors. Interest, historical accumulation, context, environment, and resources may be mentioned only as evidence or background, not as new definition criteria.

## Workspace Files

Read [references/workspace-files.md](references/workspace-files.md) when creating, repairing, or updating the workspace protocol and archive.

If the current workspace already contains `strength-system/protocol.md`, `strength-system/cases/`, `strength-system/hypotheses/`, `strength-system/reviews.md`, and `strength-system/case-index.json`, read the protocol and use the index as the fast summary before substantive analysis. Open individual case files only when details matter.

If the workspace still uses the legacy single-file archive `strength-system/case-library.md` as the source of truth, migrate it first by running `.codex/skills/unique-advantage-cleaner/scripts/manage_case_library.py migrate-legacy --file strength-system/case-library.md --root strength-system --index strength-system/case-index.json`.

If the files are missing and the user wants to start or continue the system, create them using the standard structure from the reference file.

## Workflow

### 1. Confirm Archival Intent

- Use this skill when the user explicitly wants to record, save, add, or formalize something.
- A case being clear enough is not the same as the user consenting to archive it.
- If the case is still messy and the user mainly wants understanding, route to `$unique-advantage-explorer`.
- If intent is almost clear but one brief confirmation would remove ambiguity, ask that one confirmation question.

### 2. Classify the Material

Classify each new item after any minimal clarification:

- factual case: a real event with actions, outcomes, or external feedback
- mixed case: part real event, part interpretation or future speculation
- hypothesis note: mostly preference, imagination, prediction, or self-description without a concrete completed event

Do not treat all three as the same kind of evidence.

### 3. Ask Only Archive-Critical Follow-Up Questions

- Ask at most one to three short follow-up questions when a missing fact would block reliable classification, scoring, or writing.
- Prioritize questions about:
  - what actually happened
  - what the user specifically did
  - what concrete outcome followed
  - what external validation appeared
- Prefer facts over abstract introspection.
- If deeper reflection is needed, pause the archive flow and suggest `$unique-advantage-explorer`.

### 4. Decide Whether It Enters the Formal Archive

Use this gate:

- formal case entry: there is a real event plus at least some factual basis for one or more of the three criteria
- hypothesis note: the content is useful, but it is mainly about preference, imagined behavior, or future intent
- hold and clarify: the content might become a formal case after one or two concrete follow-up answers

When evidence is too thin, prefer a short clarification round or a return to exploration over premature scoring.

### 5. Produce the Structured Record

- Convert each clarified item into the fixed record format from the reference file.
- Keep the factual summary tight and avoid embellishment.
- Score each of the three criteria on a `0-2` scale:
  - `0`: no usable evidence yet
  - `1`: partial or mixed evidence
  - `2`: strong evidence
- Add one short preliminary judgment:
  - `strong signal`
  - `possible signal`
  - `insufficient evidence`

For hypothesis notes, store them in the separate hypothesis section without formal scores.

### 6. Update the Archive

- Write each new formal case to its own file under `strength-system/cases/NNN.md`.
- Write each new hypothesis note to its own file under `strength-system/hypotheses/NNN.md`.
- Preserve existing entries; do not rewrite past judgments unless the user explicitly asks for a review or correction.
- When appropriate, add a brief cross-reference to related earlier cases.
- Treat `strength-system/cases/`, `strength-system/hypotheses/`, and `strength-system/reviews.md` as the source of truth.
- After any archive change, run `.codex/skills/unique-advantage-cleaner/scripts/manage_case_library.py reindex --root strength-system --index strength-system/case-index.json`.

### 7. Review Patterns

- When the user asks for a review, compare multiple entries instead of reasoning from one memorable story.
- Read `strength-system/case-index.json` first for a compact view, then open only the relevant files under `strength-system/cases/` or `strength-system/hypotheses/` when details matter.
- Base strong conclusions mainly on formal case entries, not hypothesis notes.
- Use hypothesis notes as prompts for future evidence collection, not as proof.
- Look for repeated high scores in the same kinds of tasks, not one-off wins.
- Keep the conclusion conservative: evidence first, interpretation second.

## Handoff Rules

- Move from `$unique-advantage-explorer` to this skill when the case is clear and the user agrees to archive it.
- Move from this skill back to `$unique-advantage-explorer` when the conversation is still mainly about understanding the case rather than recording it.
- Mention the other skill explicitly when routing so the next step is obvious.

## Output Rules

- For a new archive action, produce:
  - a short acknowledgment
  - the archive decision: formal case, hypothesis note, or hold and clarify
  - one to three short follow-up questions only when they are truly needed
  - the structured record
  - the three scores when the entry qualifies as a formal case
  - a concise confirmation that the archive and index were updated after writing
- For a review request, produce:
  - repeated patterns
  - strongest candidate advantage directions
  - weak or missing evidence
- Do not silently write files just because the case seems ready; wait for explicit consent.
- Avoid long motivational essays or prolonged consulting-style back-and-forth inside this skill.

## Lightweight Prompts to Offer the User

`Please use $unique-advantage-journal to formally record this clarified case into my archive.`

`If this case still needs to be talked through first, please use $unique-advantage-explorer before recording it.`
