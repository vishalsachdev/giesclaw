# Session Archive

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
