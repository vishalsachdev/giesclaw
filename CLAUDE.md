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

### 2026-03-24 (sessions 7+8)
- **SOS spec v2** (session 7): Brainstormed through 16 design questions. Locked: 12 agents (advocate+critic pairs), magic link auth, instant response, event-driven synthesis, outbound-only email, single-page deliberation feed at /sos. Spec: `docs/superpowers/specs/2026-03-22-sos-collective-intelligence-v2.md`
- **Phase A**: 14 new files, 3 DB tables (magic_links, endorsements, email_log), (sos) route group with separate layout. Magic link auth, feed API, endorsement toggle, full UI components. Codex review: fixed all P1/P2 findings.
- **Phase B**: 13 SOS agents registered (6 advocate-critic pairs + synthesizer), 13 posts published via real skill executions (FRED, SEC, Google Trends, etc.), 12 cross-agent debate comments seeded.
- **Phase C (partial)**: Instant agent response — human comment triggers Python subprocess that generates LLM reply in ~30-60s. Resend email integrated for magic link delivery (illinihunt.org verified domain). Agent response prompt tuned for direct, data-grounded replies.
- **UI polish**: White background (replaced dark theme), bigger fonts, faculty explainer section, agent personality tooltips on all agent names, timestamps on posts/comments, self-contained post cards (no links to main giesclaw), auth-gated comment form + endorse button, homepage isolation (no SOS content leak).
- **Fixes**: VPS table permissions, agent probation→active, correct python3 venv path for subprocess spawn.
- **RESEND_API_KEY exposed in conversation** — user needs to rotate it in Resend dashboard and re-run `bash bin/setup-resend-key.sh`.
- Next: Rotate Resend key, daily digest cron, synthesis agent trigger, agent response email notifications, recruit faculty.

### 2026-03-22 (session 6)
- **Platform audit**: Created `docs/reference/as-is-platform-audit.md` — full inventory of what works, what's stubbed, inconsistencies with ScienceClaw paper. Found 7 unused schema features, 5 naming inconsistencies, 10 paper gaps.
- **Strategic options**: Brainstormed 4 approaches (A: lenses, B: multi-topic, C: primitives, D: student-builders). Selected A for now, C for future, D as stretch goal. Saved to `docs/reference/brainstorm-use-cases.md`.
- **Paper reference**: Extracted and saved ScienceClaw paper summary to `docs/reference/scienceclaw-paper-summary.md`.
- **Communities as Analytical Lenses**: Updated all 6 community descriptions in DB (e.g., "Finance Lens: What do the numbers say?"). Reframed homepage, How It Works, and stats.
- **Investigation parameter passing (fixed)**: Added `_derive_skill_params()` — LLM extracts appropriate params (ticker, series_id, keyword) from the research topic. Skills now receive relevant context.
- **Post links (wired up)**: Fixed GET query bug (inArray), added "Linked Research" UI on post detail pages. Seeded 8 cross-lens links (contradict/cite/extend) between student posts.
- **4 high-impact audit fixes**: (1) Sessions API path `~/.infinite` → `~/.giesclaw`, (2) commentType DB field replaces text tags in Mission Control + daemon, (3) HeartbeatDaemon community engagement — agents comment on peer posts (2/cycle cap), (4) Agent personality in LLM prompts — analytical style, communication, frameworks from RoleManager.
- **Homepage iterations**: Replaced Submit/Join CTAs with demo-appropriate "Explore the Research" flow. Improved copy for first-time visitors. Added "Under the Hood" section. Mobile responsive tweaks (stats, banner stats grid, lens descriptions, community headings).
- **Next.js 16 async params fix**: Fixed 4 dynamic pages that crashed on community load.
- **Article published**: "The Classroom Where AI and Students Argue" — Substack, LinkedIn, Twitter/X. References ScienceClaw paper and compound engineering.
- All deployed to VPS and pushed to GitHub.

### 2026-03-21 (session 5)
- **Course Research Assistant simulation**: Designed, built, and executed `bin/simulate-course.py` — full 3-phase pipeline (register → investigate → comment)
  - 15 student-agents across 6 disciplines (finance, strategy, economics, marketing, entrepreneurship, operations)
  - Topic: "AI's Impact on the Workforce" — each student has a unique sub-topic
  - 45+ real skill executions (yahoo-finance, fred-data, world-bank, google-trends, sec-edgar, sentiment-analysis, news-search, porter-five-forces, market-sizing, business-model-canvas, competitor-intel, case-study-search, financial-statement-analysis)
  - 15 posts published (investment memos, case analyses, market reports, research briefs, executive summaries)
  - 8 cross-student [STUDENT] comments creating cross-disciplinary discourse
  - Script supports `--dry-run`, `--phase`, `--student`, `--cleanup` flags
  - Credentials persisted to `~/.giesclaw/simulation/credentials.json`
  - Spec: `docs/superpowers/specs/2026-03-21-course-simulation-design.md`
  - Plan: `docs/superpowers/plans/2026-03-21-course-simulation.md`
- **Next.js 16 async params fix**: Fixed 4 dynamic pages (community, post, agent, session) that used sync `params` destructuring — caused UNDEFINED_VALUE errors in Drizzle queries
- **Homepage redesign**: Added "Research Assignment In Progress" banner, "Recent Research" feed (6 latest posts), "How It Works" 3-step flow, post counts per community. Replaced abstract hero with concrete explanation.
- Deployed and verified all changes on VPS. All communities loading correctly.

### 2026-03-21 (session 4)
- **Security audit** (issue #4): Fixed 15 of 19 findings — security headers (CSP, HSTS, X-Frame-Options), CORS locked to domain, PII stripped from API, @illinois.edu email gate, form validation, XSS disclaimer, sorting tabs, sitemap, GET /api/posts/[id]
- **SVG XSS fix**: Added isomorphic-dompurify to sanitize SVG figures on input and output (dangerouslySetInnerHTML was unprotected)
- **JWT hardening**: Removed hardcoded 'your-secret-key' fallback — now fails fast if JWT_SECRET env var missing
- **All 4 GitHub issues closed** (0 open). Deployed and verified.

### 2026-03-21 (session 3)
- **Voting fix** (issue #3): Applied `getVoterIdentity()` to comment vote route — humans can now vote on comments
- **Agent feedback loop** (issue #2): Daemon checks [HUMAN] comments, generates grounded replies with [AGENT-REPLY] tag, capped at 3/cycle
- **Web search** (issue #1): Shared DuckDuckGo utility at `agent/skills/_shared/web_search.py`, all 5 LLM-only skills now search-grounded
- **Mobile + text**: Post body text-sm → text-base, mobile hamburger nav, responsive padding, Mission Control mobile sizing
- **VPS cleanup**: drizzle-kit upgraded (v0.31.10), git remote fixed, /opt/business-infinite removed, duckduckgo-search installed
- All 3 GitHub issues closed. Deployed and verified (HTTP 200, both services active).

### 2026-03-21 (session 2)
- **Rename complete**: 43 files, ~100 businessclaw→giesclaw refs across agent/, platform/, bin/, docs/
  - CLI: bin/businessclaw-{post,investigate} → bin/giesclaw-{post,investigate}
  - Agent state: ~/.businessclaw/ → ~/.giesclaw/ (10 Python files)
  - Env var: BUSINESSCLAW_FORCE_SKILL_REFRESH → GIESCLAW_FORCE_SKILL_REFRESH
  - Platform: package name, API headers, regex, docs, CollaborationViewer
- **VPS monorepo deploy**: Removed platform/ symlink → /opt/business-infinite, restored real git files, rebuilt. Fixed drizzle.config.ts type error (removed deprecated `driver` field, excluded from tsconfig). Both services active (HTTP 200).
- **Voting**: humanVoterId column already in DB — schema was applied in prior session. Needs end-to-end test.
- **VPS systemd**: Created giesclaw-daemon.service (renamed from businessclaw-daemon), agent state dir renamed ~/.businessclaw → ~/.giesclaw
- Note: VPS git remote still says `businessclaw` (GitHub redirect handles it), drizzle-kit v0.18.1 too old for push:pg

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
