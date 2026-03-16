# Memory Conventions

All persistent state lives in `.memory/`. This directory is committed to git.

## File Naming
```
.memory/<subdirectory>/YYYY-MM-DD-<slug>.md
```

## Subdirectories

| Directory | What Goes Here |
|-----------|---------------|
| `decisions/` | Architecture choices, tech stack picks, strategy calls |
| `blockers/` | Known obstacles, rate limits, missing credentials |
| `context/` | Session handoff notes, "where I left off" summaries |
| `team/` | Role assignments, availability, who owns what |

## Entry Format
```markdown
# <Title>

**Date:** YYYY-MM-DD
**Category:** Cat 1 | Cat 2 | Cat 3 | Cat 4 | Cat 5 | Cross-cutting
**Author:** <person or agent name>
**Status:** Active | Resolved | Superseded by <link>

## Context
<What prompted this entry>

## Decision / Blocker / Context
<The substance>

## Consequences
<What changes as a result>
```

## INDEX.md
`.memory/INDEX.md` is a flat list of all entries, newest first.
Agents append to INDEX.md when creating a new memory entry.
