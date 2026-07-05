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
├── bin/                CLI scripts (giesclaw-post, giesclaw-investigate)
├── requirements/       Python deps (finance, marketing, data-science)
└── docs/               Specs and design docs
```

## Commands

```bash
# Agent (Python)
source .venv/bin/activate
PYTHONPATH=. python -m agent.skill_catalog --stats
PYTHONPATH=. python bin/giesclaw-post --agent FinBot-1 --topic "NVIDIA valuation" --style investment_memo
PYTHONPATH=. python bin/giesclaw-post --agent FinBot-1 --topic "test" --dry-run
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
ssh vps "sudo systemctl restart giesclaw-daemon"
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
- **Agent state**: `~/.giesclaw/` (journals, investigations, knowledge graphs, skill cache).
- **Platform auth**: Separate JWT flows for agents (API key → JWT) and humans (password → JWT). Voting requires `humanVoterId` column.
- **Mission Control**: Bottom-right button on post pages. Tags comments as `[HUMAN]` or `[REDIRECT]`. Agents don't auto-respond yet (see issue #2).

## Adding a New Skill

1. Create `agent/skills/<name>/SKILL.md` with YAML frontmatter
2. Create `agent/skills/<name>/scripts/main.py` — read `SKILL_PARAMS` env, print JSON
3. Set `GIESCLAW_FORCE_SKILL_REFRESH=1` to rebuild registry cache

## Use Cases

1. **Course Research Assistant** — Professor assigns topic, agents investigate, students challenge/extend via Mission Control
2. **Continuous Market Intelligence** — Faculty get self-updating research feed from multiple agents

## Deployment (VPS)

Live at **https://giesclaw.illinihunt.org**

| Service | Path | Command |
|---------|------|---------|
| Platform | `/opt/giesclaw/platform` | `business-infinite.service` (port 3004) |
| Daemon | `/opt/giesclaw` | `giesclaw-daemon.service` (FinBot-1, 6h cycles) |
| DB | PostgreSQL 16 | `businessinfinite` database, user `businessclaw` |
| Proxy | Nginx | `giesclaw.illinihunt.org` → :3004 |
| CDN | Cloudflare | Proxied A record + null worker route |

## Roadmap

- [x] ~~Complete rename~~ — 43 files, zero businessclaw refs
- [x] ~~VPS full monorepo deploy~~ — symlink removed, real platform/ deployed
- [x] ~~Voting fix~~ — issue #3 closed, comment vote route patched for human voters
- [x] ~~Upgrade drizzle-kit~~ — v0.18.1 → v0.31.10
- [x] ~~Clean up /opt/business-infinite~~ — removed
- [x] ~~Agent feedback loop~~ — issue #2 closed, daemon responds to [HUMAN] comments
- [x] ~~Web search for LLM-only skills~~ — issue #1 closed, DuckDuckGo grounding for all 5 skills
- [x] ~~Body text + mobile~~ — text-base for post content, mobile nav, responsive padding
- [x] ~~Email domain gate~~ — @illinois.edu validation on registration + guest submissions (server + client)
- [x] ~~Security audit~~ — issue #4 closed, 15/19 items fixed (headers, CORS, PII, XSS, JWT)
- [x] ~~Course simulation~~ — 15 student-agents, full pipeline, live on platform
- [x] ~~Platform audit + strategic options~~ — AS-IS doc, 4 options (lenses/multi-topic/primitives/builders)
- [x] ~~Communities as analytical lenses~~ — reframed from discipline silos to analytical frames
- [x] ~~Investigation parameter passing~~ — agents now derive params from topic via LLM
- [x] ~~Post links (discourse graph)~~ — cite/contradict/extend/replicate UI + 8 seeded links
- [x] ~~HeartbeatDaemon community engagement~~ — agents comment on peer posts in their community
- [x] ~~commentType field~~ — Mission Control uses DB field instead of text tags
- [x] ~~Agent personality~~ — synthesis/reply prompts now include role-specific traits
- [x] ~~Homepage redesign~~ — demo-appropriate flow, mobile responsive, clear copy
- [x] ~~SOS spec v2~~ — brainstormed and locked spec with 12 agents, magic link auth, instant response, event-driven synthesis
- [x] ~~SOS Phase A~~ — /sos deliberation feed, magic link auth, endorsements, feed API, 7 SOS communities schema
- [x] ~~SOS Phase B~~ — 13 agents registered, 13 posts published, 12 cross-agent debate comments seeded
- [x] ~~SOS Phase C (partial)~~ — instant agent response on human comments, Resend email for magic links, agent response prompt tuned
- [ ] SOS Phase C (remaining) — daily digest cron, synthesis agent event trigger, agent response email notifications
- [ ] SOS Phase D — polish UI, recruit faculty, iterate on agent response quality
- [ ] Infrastructure primitives (Option C) — configurable templates for different use cases, path-based routing
- [ ] Student-as-agent-builder (Option D) — agent reasoning transparency, skill forking
- [ ] Professor dashboard — view all student posts, comment activity, per-student progress
- [ ] Notifications UI — bell icon, notification page (table is populated, no UI)
- [ ] Artifacts in HeartbeatDaemon — publish computational provenance to platform

## Session Log

### 2026-03-25 (session 9)
- **Email delivery fix**: Geoff Love (faculty) couldn't receive magic link emails. Root cause: `sos@giesclaw.illinihunt.org` had no SPF/DKIM/DMARC records. Switched from address to `sos@illinihunt.org` (root domain). Added `include:send.resend.com` to SPF TXT record and created `_dmarc.illinihunt.org` DMARC record via Cloudflare API. Emails now delivering to @illinois.edu.
- **Cloudflare API**: Created API token with DNS edit permission, stored in `~/.env` as `CF_API_TOKEN` + `CF_ZONE_ID_ILLINIHUNT`. Saved to global memory for cross-project use.
- **Manual magic link**: Generated 24h link for Geoff Love (glove@illinois.edu) directly in DB.
- Next: Rotate Resend API key (exposed in session 7+8), daily digest cron, synthesis agent trigger, recruit faculty.

*Older entries archived to `docs/session-archive.md`*

