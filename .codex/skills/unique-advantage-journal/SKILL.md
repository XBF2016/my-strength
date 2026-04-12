---
name: unique-advantage-journal
description: Structured workflow for recording real-life personal cases, updating a persistent archive, and analyzing a user's unique advantage with a fixed three-point definition. Use when the user wants to dictate a new case, review accumulated evidence, discuss whether an experience reflects their unique advantage, or keep a long-term strength journal inside Codex.
---

# Unique Advantage Journal

## Overview

Use this skill to turn raw spoken cases into a consistent archive and to keep all analysis anchored to one fixed definition of personal unique advantage.

Default to the user's language. If the user writes in Chinese, think and answer in Chinese unless asked otherwise.

## Fixed Definition

Treat the user's unique advantage as defined by exactly three criteria:

- long-term sustainability: the user can keep doing this kind of work over time
- faster learning: the user reaches competence faster than most people on similar tasks
- better results with external validation: the output is stronger and reality confirms it through trust, selection, feedback, responsibility, ranking, payment, or repeated requests

Do not add extra "core definition" factors. Interest, historical accumulation, context, environment, and resources may be mentioned only as evidence or background, not as new definition criteria.

## Workspace Files

Read [references/workspace-files.md](references/workspace-files.md) when creating, repairing, or updating the workspace protocol and case library.

If the current workspace already contains `strength-system/protocol.md`, `strength-system/case-library.md`, and `strength-system/case-index.json`, read the protocol and use the index as the fast summary before substantive analysis.

If the files are missing and the user wants to start or continue the system, create them using the standard structure from the reference file.

## Workflow

### 1. Anchor the Conversation

- Keep the discussion centered on the three-point definition.
- If the conversation drifts into broader success theory, bring it back to the user's unique advantage unless the user explicitly asks to widen scope.
- Distinguish facts, evidence, and preliminary interpretation.

### 2. Start With Consultant-Style Listening

- Let the user finish the first narration before forcing structure.
- Reflect back the core of what you heard in one compact summary.
- Separate three layers in your own reasoning:
  - what objectively happened
  - how the user interpreted it
  - what the user felt, wanted, or imagined
- Do not rush into scoring before this separation is clear.

### 3. Ask Only the Highest-Leverage Clarifying Questions

- Ask at most one to three short follow-up questions when they materially change evidence quality.
- Prioritize questions about:
  - concrete actions
  - concrete outcomes
  - external feedback
  - repeated pattern vs one-off event
- Do not interrogate the user when the factual core is already strong enough.

### 4. Classify the Input First

Classify each new user input after the initial listening and any short clarification:

- factual case: a real event with actions, outcomes, or external feedback
- mixed case: part real event, part interpretation or future speculation
- hypothesis note: mostly preference, imagination, prediction, or self-description without a concrete completed event

Do not treat all three as the same kind of evidence.

### 5. Intake a New Case

- Let the user speak naturally or follow the lightweight prompt.
- Ask only the minimum follow-up needed to make the record usable. Prefer questions about concrete facts over abstract introspection.
- Pull out:
  - what happened
  - what the user actually did
  - how sustainable it felt
  - where learning speed showed up
  - what concrete outcome and external validation appeared

For a mixed case, extract the factual core first and ask for one or two missing concrete details if they matter.

For a hypothesis note, do not write a formal case entry yet unless the user explicitly wants a low-evidence note preserved.

### 6. Decide Whether It Enters the Formal Archive

Use this gate:

- formal case entry: there is a real event plus at least some factual basis for one or more of the three criteria
- hypothesis note: the content is useful, but it is mainly about preference, imagined behavior, or future intent
- hold and clarify: the content might become a formal case after one or two concrete follow-up answers

When evidence is too thin, prefer a short clarification round over premature scoring.

### 7. Produce the Structured Record

- Convert each spoken case into the fixed record format from the reference file.
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

### 8. Update the Archive

- Append the new record to `strength-system/case-library.md`.
- Preserve existing entries; do not rewrite past judgments unless the user explicitly asks for a review or correction.
- When appropriate, add a brief cross-reference to related earlier cases.
- Keep formal cases and hypothesis notes in separate sections.
- After any archive change, run `.codex/skills/unique-advantage-cleaner/scripts/manage_case_library.py reindex --file strength-system/case-library.md --index strength-system/case-index.json`.

### 9. Review Patterns

- When the user asks for a review, compare multiple entries instead of reasoning from one memorable story.
- Read `strength-system/case-index.json` first for a compact view, then open the full archive only when details matter.
- Base strong conclusions mainly on formal case entries, not hypothesis notes.
- Use hypothesis notes as prompts for future evidence collection, not as proof.
- Look for repeated high scores in the same kinds of tasks, not one-off wins.
- Keep the conclusion conservative: evidence first, interpretation second.

## Output Rules

- For a new case, produce:
  - a short acknowledgment
  - a one-paragraph reflection of the user's core point when useful
  - the classification: factual case, mixed case, or hypothesis note
  - one to three clarifying questions when they are needed before reliable scoring
  - the structured record
  - the three scores when the entry qualifies as a formal case
  - one concise next-step note if evidence is still thin
- For a review request, produce:
  - repeated patterns
  - strongest candidate advantage directions
  - weak or missing evidence
- Avoid turning the response into a long motivational essay.
- Do not redefine the framework midstream.

## Lightweight Prompt to Offer the User

If the user wants a prompt for dictating cases, offer this:

`Today I want to record a case called []. The situation was []. I mainly did []. My state while doing it was []. If I had to repeat this kind of work long term, I would feel []. I learned faster or slower than others in these ways []. The final result was []. The external feedback was []. Right now I think its relationship to my unique advantage is [].`
