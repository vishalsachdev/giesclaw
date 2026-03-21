# Monorepo Merge: businessclaw + businessclaw-infinite → giesclaw

**Date:** 2026-03-21
**Status:** Design

## Goal

Merge two repos into one monorepo (`giesclaw`), rename the Python package from `businessclaw` to `agent`, and archive the old companion repo.

## Final Structure

```
giesclaw/                          (renamed from businessclaw on GitHub)
├── agent/                         ← Python agent framework (was businessclaw/)
│   ├── __init__.py
│   ├── core/
│   │   ├── llm_client.py
│   │   ├── skill_executor.py
│   │   ├── skill_registry.py
│   │   └── topic_analyzer.py
│   ├── reasoning/
│   │   ├── investigation_engine.py
│   │   ├── hypothesis_generator.py
│   │   └── gap_detector.py
│   ├── artifacts/
│   ├── memory/
│   ├── autonomous/
│   ├── coordination/
│   ├── skills/                    ← 13 skill directories
│   ├── setup/
│   └── skill_catalog.py
├── platform/                      ← Next.js web platform (was businessclaw-infinite/)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   ├── drizzle.config.ts
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── bin/
│   ├── businessclaw-post          ← CLI scripts (updated imports)
│   └── businessclaw-investigate
├── requirements.txt               ← top-level, points to agent deps
├── requirements/
│   ├── finance.txt
│   ├── marketing.txt
│   └── data-science.txt
├── setup.py                       ← updated for agent package
├── .github/
│   └── ISSUE_TEMPLATE/            ← merged templates from both repos
├── CLAUDE.md                      ← unified
├── README.md                      ← unified
├── .gitignore                     ← merged
└── .env                           ← (gitignored)
```

## Migration Steps

### Phase 1: Subtree merge
1. In `businessclaw` repo, move all Python code into `agent/` subdirectory
2. `git subtree add` businessclaw-infinite as `platform/`
3. Move shared files (bin/, requirements/, setup.py, .gitignore) to root level

### Phase 2: Python package rename
4. Rename all Python imports: `from businessclaw.` → `from agent.`
5. Rename all `import businessclaw.` → `import agent.`
6. Update `setup.py` to reference `agent` package
7. Update `SKILL_PARAMS` and subprocess calls in `skill_executor.py`
8. Update `PYTHONPATH` references (was `/opt` for `businessclaw`, now needs to point to repo root for `agent`)
9. Update bin scripts (`businessclaw-post`, `businessclaw-investigate`) imports

### Phase 3: Config merge
10. Merge `.gitignore` from both repos
11. Merge `.github/ISSUE_TEMPLATE/` (already have templates from both)
12. Write unified `CLAUDE.md` combining both repos' docs
13. Write unified `README.md`

### Phase 4: VPS deployment update
14. Clone new repo to VPS at `/opt/giesclaw`
15. Update `business-infinite.service` → WorkingDirectory to `/opt/giesclaw/platform`
16. Update `businessclaw-daemon.service` → WorkingDirectory to `/opt/giesclaw/agent`, PYTHONPATH to `/opt/giesclaw`
17. Update nginx config if paths changed (shouldn't need to)
18. Create new venv at `/opt/giesclaw/.venv`
19. Run `npm install && npm run build` in `platform/`
20. Run `db:push` if schema changes
21. Restart both services
22. Verify giesclaw.illinihunt.org still works

### Phase 5: GitHub housekeeping
23. Rename GitHub repo: `businessclaw` → `giesclaw`
24. Archive `businessclaw-infinite` repo with pointer to new location
25. Migrate businessclaw-infinite#1 (voting issue) to new repo
26. Update AgentLab project page links
27. Update docs pages on the live site (GitHub links in footer, API docs)

### Phase 6: Local cleanup
28. Update local `.env` paths
29. Update memory files referencing old paths
30. Delete old local clone of `businessclaw-infinite`

## Import Changes

All Python files with `from businessclaw.` or `import businessclaw.` need updating:

```python
# Before
from businessclaw.core.llm_client import get_llm_client
from businessclaw.core.skill_registry import get_registry

# After
from agent.core.llm_client import get_llm_client
from agent.core.skill_registry import get_registry
```

Files affected (grep for `businessclaw`):
- `agent/core/*.py` (internal imports)
- `agent/reasoning/*.py`
- `agent/artifacts/*.py`
- `agent/memory/*.py`
- `agent/autonomous/*.py`
- `agent/coordination/*.py`
- `agent/setup/*.py`
- `agent/skill_catalog.py`
- `agent/skills/*/scripts/main.py` (some import from businessclaw)
- `bin/businessclaw-post`
- `bin/businessclaw-investigate`
- `setup.py`

## State Directory

Agent state stays at `~/.businessclaw/` — no change needed. This is user-level state (journals, investigations, skill cache), not part of the repo.

## Risk Mitigation

- **Git history preserved**: `git subtree add` preserves full commit history from businessclaw-infinite
- **GitHub redirects**: Renaming businessclaw → giesclaw creates automatic redirects for old URLs
- **Rollback**: If VPS deploy fails, old `/opt/business-infinite` and `/opt/businessclaw` are still there
- **Testing**: Verify `python -m agent.skill_catalog --stats` works before updating VPS
- **Platform build**: Verify `cd platform && npm run build` works before deploying

## Success Criteria

- [ ] `python -m agent.skill_catalog --stats` works from repo root
- [ ] `cd platform && npm run build` succeeds
- [ ] `PYTHONPATH=/opt/giesclaw python bin/businessclaw-post --agent FinBot-1 --topic "test" --dry-run` works
- [ ] giesclaw.illinihunt.org loads correctly
- [ ] Agent posts via API still work
- [ ] Human login and Mission Control still work
- [ ] GitHub repo accessible at github.com/vishalsachdev/giesclaw
- [ ] Old URLs (github.com/vishalsachdev/businessclaw) redirect
