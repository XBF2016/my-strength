---
name: unique-advantage-cleaner
description: Cleanup workflow for the unique-advantage archive in the current project. Use when the user wants to list saved cases, inspect which formal cases or hypothesis notes exist, delete one or more entries by id, clear all entries, or reset the case library back to its initial empty state.
---

# Unique Advantage Cleaner

## Overview

Use this skill to safely inspect and clean `strength-system/case-library.md` inside the current project while keeping `strength-system/case-index.json` in sync.

Do not delete anything until the user explicitly selects `all`, `formal all`, `hypothesis all`, or specific ids.

Default to the user's language. If the user writes in Chinese, think and answer in Chinese unless asked otherwise.

## Target File

The default target files are:

- `strength-system/case-library.md`
- `strength-system/case-index.json`

If the library file does not exist, say so briefly and stop.

If the index file is missing or older than the library file, rebuild it first.

## Script

Use `scripts/manage_case_library.py` for all listing and deletion work instead of editing the archive manually.

Supported operations:

- `list`: enumerate formal cases and hypothesis notes from the index
- `delete`: delete specific ids or clear all entries
- `reindex`: rebuild the index from the source library

## Workflow

### 1. Inspect First

- Run the `list` command first unless the user already provided an exact deletion choice.
- Let the script refresh the index when it is stale.
- Summarize the current archive grouped into:
  - formal cases
  - hypothesis notes

### 2. Ask for a Concrete Deletion Choice

If the user has not already chosen, ask one short question that offers these options:

- `all`: clear everything and return the archive to its initial empty state
- `formal all`: clear all formal cases only
- `hypothesis all`: clear all hypothesis notes only
- specific ids such as `case 001`, `hypothesis 001`, or multiple ids separated by commas

Do not ask multiple open-ended questions.

### 3. Execute Safely

- Translate the user's choice to script tokens:
  - `all`
  - `formal:all`
  - `hypothesis:all`
  - `case:001`
  - `hypothesis:001`
- Run the delete command once with the final token list.
- If the user names an id that does not exist, explain that clearly and do not partially delete anything.

### 4. Confirm the Result

- Report which entries were removed.
- Report how many formal cases and hypothesis notes remain.
- If everything was cleared, say that the archive is back to its initial empty state.
- Confirm that the index was updated.

## Output Rules

- Keep the list concise.
- Use ids exactly as stored so the user can reply with those ids.
- Never silently delete entries.
- Never renumber remaining entries after deletion.
