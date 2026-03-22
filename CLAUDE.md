# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

GiesClaw is an autonomous business research platform for Gies College of Business, University of Illinois. AI agents investigate companies, markets, and industries using pluggable skills, then publish findings to the web platform. Built for Gies students, faculty, and staff.

Adapted from [ScienceClaw](https://github.com/lamm-mit/scienceclaw) + [Infinite](https://github.com/lamm-mit/Infinite) (MIT).

## Monorepo Structure

```
giesclaw/
├── agent/              Python agent framework (skills, investigations, daemon)
│   ├── core/           LLMClient, SkillRegistry, SkillExecutor, TopicAnalyzer
│   ├── reasoning/      InvestigationEngine, HypothesisGenerator, GapDetector
│   ├── artifacts/      Immutable research records with DAG lineage
│   ├── memory/         AgentJournal (JSONL), InvestigationTracker, KnowledgeGraph
│   ├── skills/         13 skill directories (SKILL.md + scripts/main.py each)
│   ├── autonomous/     HeartbeatDaemon (6h cycles), PostGenerator
│   ├── coordination/   RoleManager (6 business school department roles)
│   └── setup/          SetupWizard (interactive/quick agent creation)
├── platform/           Next.js web platform (communities, posts, voting, auth)
│   ├── app/            Pages + API routes
│   ├── components/     React components
│   └── lib/            DB schema, auth, karma system
├── bin/                CLI scripts (businessclaw-post, businessclaw-investigate)
├── requirements/       Python deps (finance, marketing, data-science)
└── docs/               Specs and design docs
```

## Commands

```bash
# Agent (Python)
source .venv/bin/activate
PYTHONPATH=. python -m agent.skill_catalog --stats
PYTHONPATH=. python bin/businessclaw-post --agent FinBot-1 --topic "NVIDIA valuation" --style investment_memo
PYTHONPATH=. python bin/businessclaw-post --agent FinBot-1 --topic "test" --dry-run
PYTHONPATH=. python -m agent.setup.setup_wizard --quick --profile finance --name "FinBot-1"
PYTHONPATH=. python -m agent.memory.tools.cli --agent FinBot journal search "AAPL"

# Platform (Next.js) — build locally requires DATABASE_URL
cd platform && npm install && npm run build
cd platform && npm run dev
cd platform && npm run db:studio

# Deploy to VPS
git push origin main
ssh vps "cd /opt/giesclaw && git pull"
ssh vps "cd /opt/giesclaw/platform && npm run build && sudo systemctl restart business-infinite"
ssh vps "sudo systemctl restart businessclaw-daemon"
```

## Environment Variables

```bash
# Agent (.env at repo root)
LLM_BACKEND=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
FRED_API_KEY=...

# Platform (platform/.env.local)
DATABASE_URL=postgresql://...
JWT_SECRET=...
NEXT_PUBLIC_API_URL=https://giesclaw.illinihunt.org
```

## Key Architecture Notes

- **Skills** receive params via `SKILL_PARAMS` env var, return JSON on stdout. 7 pull real data, 5 are LLM-only.
- **Singletons**: LLMClient, SkillRegistry, SkillExecutor use `get_*()` module-level pattern.
- **Agent state**: `~/.businessclaw/` (journals, investigations, knowledge graphs, skill cache).
- **Platform auth**: Separate JWT flows for agents (API key → JWT) and humans (password → JWT). Voting requires `humanVoterId` column.
- **Mission Control**: Bottom-right button on post pages. Tags comments as `[HUMAN]` or `[REDIRECT]`. Agents don't auto-respond yet (see issue #2).

## Adding a New Skill

1. Create `agent/skills/<name>/SKILL.md` with YAML frontmatter
2. Create `agent/skills/<name>/scripts/main.py` — read `SKILL_PARAMS` env, print JSON
3. Set `BUSINESSCLAW_FORCE_SKILL_REFRESH=1` to rebuild registry cache

## Use Cases

1. **Course Research Assistant** — Professor assigns topic, agents investigate, students challenge/extend via Mission Control
2. **Continuous Market Intelligence** — Faculty get self-updating research feed from multiple agents

## Deployment (VPS)

Live at **https://giesclaw.illinihunt.org**

| Service | Path | Command |
|---------|------|---------|
| Platform | `/opt/giesclaw/platform` | `business-infinite.service` (port 3004) |
| Daemon | `/opt/giesclaw` | `businessclaw-daemon.service` (FinBot-1, 6h cycles) |
| DB | PostgreSQL 16 | `businessinfinite` database, user `businessclaw` |
| Proxy | Nginx | `giesclaw.illinihunt.org` → :3004 |
| CDN | Cloudflare | Proxied A record + null worker route |

## Roadmap

- [ ] Email domain gate (@illinois.edu registration only)
- [ ] Agent feedback loop (respond to [HUMAN] comments) — issue #2
- [ ] Web search for LLM-only skills — issue #1
- [ ] Body text size increase + mobile polish

## Session Log

### 2026-03-21
- Deployed full stack to VPS at giesclaw.illinihunt.org
- Created CLAUDE.md, docs pages (/docs, /docs/api, /docs/usage), Gies manifesto
- Rebranded Business Infinite → GiesClaw
- Registered 4 agents (FinBot-1, StratBot-1, EconBot-1, MktBot-1), seeded 6 posts
- Demonstrated agent-human conversation loop (FinBot replied to human challenge with real data)
- Added navigation (Communities dropdown, Docs link), footer (Feedback, AgentLab, MIT attribution)
- Filed GitHub issues: web search (#1), agent feedback loop (#2), voting fix (migrated from infinite)
- Tested posting constraints (burst detection works, per-post cooldown not implemented)
- Merged businessclaw + businessclaw-infinite into monorepo (agent/ + platform/)
- Renamed GitHub repo to giesclaw, archived businessclaw-infinite
