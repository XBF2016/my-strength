---
name: structure-oral-material
description: Turn spoken, chatty, or transcript-like narration into faithful, low-interpretation structured source material. Use when Codex needs to把用户的口述内容、语音转写、回忆性描述、案例复盘或随口说出的经历，整理成事实优先的结构化卡片、案例记录或仓库素材，而不要过度分析、擅自补全动机，或提前固化结论。
---

# Structure Oral Material

## Overview

Convert narration into structured source material with minimal interpretation.
Default to a fact-first pass. Keep analysis separate and optional.

## Workflow

1. Identify the unit of material.
- Decide whether the input is one episode, multiple episodes, or a diffuse reflection.
- Split clearly different episodes into separate cards instead of forcing them into one summary.

2. Extract only what the user actually said.
- Keep time, context, task, recipients, actions, tool involvement, outcomes, feedback, and uncertainties.
- Remove口头停顿、重复和语气词, but preserve meaning.
- Preserve brief original wording when it carries evidence, tone, or a useful label.

3. Normalize into a structured card.
- Use the templates in `references/output-templates.md`.
- Prefer empty or uncertain fields over guessed content.
- Write `未提及` or `不确定` when the gap matters.

4. Enforce low-interpretation guardrails.
- Do not infer strengths, motives, personality traits, or hidden causality unless the user explicitly asks for analysis.
- Do not rewrite the material into polished self-branding language.
- Do not merge facts and conclusions in the same section.
- If the source already contains self-interpretation, preserve it as quoted or attributed content rather than treating it as fact.

5. Add analysis only when explicitly requested.
- Put analysis in a separate section labeled `可选分析（非事实）`.
- Base the analysis on the structured material you just extracted.
- Keep the factual section untouched.

## Repo-Specific Use

When working inside this repository:

- Read `README.md` and `AI-ENTRY.md` before editing project files.
- Prefer `evidence/raw-log.md` for short entries.
- Prefer `evidence/episodes/` for richer single-case cards.
- Keep `analysis/` for hypotheses or interpretation only.
- Default to writing the structured result into the repository, not just displaying it in chat.
- Use `evidence/raw-log.md` when the input is brief, early, fragmented, or still rough.
- Create a new file in `evidence/episodes/` when the material is a richer single case with enough detail to stand on its own.
- Only return a preview without editing files when the user explicitly asks to preview, compare versions, or avoid writing.
- After writing, briefly tell the user which file was updated or created.

## Output Rules

- Default to Chinese unless the user asks otherwise.
- Prefer flat bullets and short field labels.
- Start with the structured material, not with commentary.
- Keep wording faithful and compress only for clarity.
- End with `仍不确定的点` when important gaps remain.

## Reference

- Read `references/output-templates.md` when you need the exact card format.
