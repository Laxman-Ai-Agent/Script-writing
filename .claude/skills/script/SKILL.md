---
name: script
description: Telugu narration script writer for Health Decode, Zumba Fitness and The Dark World. Writing rules were cleared on 2026-11-22 (rebuild from scratch); no category has rules yet. Use when the user gives a topic or new writing rules.
---

# Telugu Narration Script Writer (rules cleared 2026-11-22 - rebuild in progress)

## Status: NO writing rules exist
| Category | Rule file |
|---|---|
| Health Decode | (none - removed 2026-11-22) |
| Zumba Fitness | (none) |
| The Dark World | (none) |
- Until the user gives new rules for a category, do NOT write scripts for it: tell the user the rules are empty and ask for them. Never reuse any old rule, old script style, `sample script/`, earlier `output/` scripts or anything from git history.
- New rules from the user go into `script-system/rules/<category>.md` (one file per category; categories never mix). A later rule replaces the line it contradicts in the same edit (no stacking).

## Mechanics kept (not writing style)
- Research: English sources into `output/YYYY-MM-DD-<slug>/facts.md` (claim - source URL - confidence), optionally via one Sonnet subagent; write only from facts.md, re-tell, never translate.
- No Google Sheet connector exists now (removed 2026-11-22); `script-system/credentials/` (service-account key) is kept for when a new one is built.
