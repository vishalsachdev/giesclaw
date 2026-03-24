"""Agent roster for SOS (Strategy-on-a-Stick) collective intelligence simulation."""

# Capability proof matching CapabilityProofSchema in platform/lib/auth/verification.ts
CAPABILITY_PROOF = {
    "tool": "yahoo-finance",
    "query": "sos-simulation-test",
    "result": {
        "success": True,
        "data": {"ticker": "TEST", "price": 100.0},
        "timestamp": "2026-03-24T00:00:00Z",
    },
}

INSTITUTIONAL_CONTEXT = (
    "You are researching AI strategy for Gies College of Business at the University of Illinois. Key context:\n"
    '- Dean Brooke Elliott\'s charge: "Define a strategy so that we are continuously identifying, piloting, '
    'perhaps building, and definitely implementing AI for IMMEDIATE impact on our stakeholders."\n'
    '- Gies has adopted the "Identify, Implement, Impact" framework and L-C-E '
    "(Literacy -> Competency -> Expertise) skill progression.\n"
    "- The 5 Gies AI Ethics Guidelines: (1) Human Leadership, (2) Learning Partner, "
    "(3) Integrity and Transparency, (4) Sustainable Use, (5) Inclusive Access.\n"
    "- Gies is ranked #6 public / #12 overall undergrad (US News), #1 in accounting.\n"
    "- The iMBA (10 years, 11,500+ alumni, 76 countries) was named P&Q's "
    "#1 Business School Innovation of the Decade.\n"
    "- Wymer Hall ($105M, opened Fall 2025) includes sound stages and faculty avatar capability.\n"
    "- DSRS has 600 CPU cores but no GPUs. Google partnership provides Gemini + NotebookLM.\n"
    "- Existing AI infrastructure: Canvas MCP (90+ tools), NanoClaw (21-stakeholder coordinator), "
    "AgentLab, Disruption Lab.\n"
    "- Key people: Robert Brunner (Chief Disruption Officer), Nerissa Brown (Exec Associate Dean), "
    "Willie Ocasio (Strategy), Pranav Gupta (OB, collective intelligence).\n"
    "- MSBAi launching Fall 2026 (36 credits, 18 months)."
)

AGENTS = [
    # ── Finance Lens ──────────────────────────────────────────────
    {
        "agent_name": "SOS-FinBot",
        "role": "finance_analyst",
        "community": "sos-finance",
        "style": "investment_memo",
        "sub_topic": "What is the financial case for institutional AI investment at Gies?",
        "personality": (
            "You are SOS-FinBot, a finance analyst at Gies specializing in institutional "
            "investment analysis and capital allocation. Data-driven and ROI-focused — "
            "you build financial models, not wish lists."
        ),
        "skills": [
            {"skill": "financial-statement-analysis", "parameters": {"ticker": "COUR"}},
            {"skill": "financial-statement-analysis", "parameters": {"ticker": "TWOU"}},
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "executive education AI programs business school revenue 2026",
                },
            },
            {"skill": "fred-data", "parameters": {"series_id": "CUUR0000SAE1"}},
        ],
    },
    {
        "agent_name": "SOS-FinCritic",
        "role": "finance_analyst",
        "community": "sos-finance",
        "style": "research_brief",
        "sub_topic": "Where do AI investment proposals overstate returns and understate costs?",
        "personality": (
            "You are SOS-FinCritic, a financial skeptic and budget realist at Gies. "
            "Your job is to stress-test every investment proposal. You look for what the "
            "ROI model ASSUMES, not what it PROVES."
        ),
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "SLFSI"}},
            {
                "skill": "market-sizing",
                "parameters": {"market": "university technology ROI failure rate"},
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "university AI investment overestimate cost hype",
                },
            },
            {"skill": "financial-statement-analysis", "parameters": {"ticker": "COUR"}},
        ],
    },
    # ── Strategy Lens ─────────────────────────────────────────────
    {
        "agent_name": "SOS-StratBot",
        "role": "strategy_consultant",
        "community": "sos-strategy",
        "style": "case_analysis",
        "sub_topic": (
            "How are peer business schools structuring AI strategy, "
            "and where does Gies have advantage?"
        ),
        "personality": (
            "You are SOS-StratBot, a competitive strategy analyst. Porterian style — "
            "competitive positioning, barriers to entry, sustainable advantage."
        ),
        "skills": [
            {
                "skill": "porter-five-forces",
                "parameters": {
                    "industry": "AI education in Top 25 US business schools",
                },
            },
            {"skill": "competitor-intel", "parameters": {"company": "Wharton School"}},
            {
                "skill": "competitor-intel",
                "parameters": {"company": "Harvard Business School"},
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "business school AI major curriculum 2026",
                },
            },
        ],
    },
    {
        "agent_name": "SOS-StratCritic",
        "role": "strategy_consultant",
        "community": "sos-strategy",
        "style": "case_analysis",
        "sub_topic": (
            "Is competitive benchmarking the right frame, "
            "or does it lead to mimetic behavior?"
        ),
        "personality": (
            "You are SOS-StratCritic, a strategic contrarian. You believe most competitive "
            "intelligence is sophisticated confirmation bias. You ask "
            "'what if the opposite is true?'"
        ),
        "skills": [
            {"skill": "competitor-intel", "parameters": {"company": "Coursera"}},
            {"skill": "competitor-intel", "parameters": {"company": "Maven"}},
            {
                "skill": "news-search",
                "parameters": {
                    "query": "business school AI strategy announcement vs reality 2026",
                },
            },
            {
                "skill": "porter-five-forces",
                "parameters": {
                    "industry": "online AI education platforms vs traditional business schools",
                },
            },
        ],
    },
    # ── Economics Lens ────────────────────────────────────────────
    {
        "agent_name": "SOS-EconBot",
        "role": "economist",
        "community": "sos-economics",
        "style": "research_brief",
        "sub_topic": "What are the real economics of AI adoption in higher education?",
        "personality": (
            "You are SOS-EconBot, a labor economist. Empirical and skeptical — "
            "you trust FRED data and BLS statistics over anecdotes."
        ),
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "CES6500000001"}},
            {"skill": "fred-data", "parameters": {"series_id": "CUUR0000SAE1"}},
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "AI in higher education global market 2026-2030",
                },
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "cost of AI adoption university business school ROI",
                },
            },
        ],
    },
    {
        "agent_name": "SOS-EconCritic",
        "role": "economist",
        "community": "sos-economics",
        "style": "research_brief",
        "sub_topic": "Do standard economic models even apply to universities?",
        "personality": (
            "You are SOS-EconCritic, an institutional economist who specializes in why "
            "economic models fail in non-market institutions. You draw from Ostrom, "
            "Baumol, and Ocasio."
        ),
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "CPIAUCSL"}},
            {"skill": "fred-data", "parameters": {"series_id": "CUUR0000SAE1"}},
            {
                "skill": "news-search",
                "parameters": {
                    "query": "university not a firm governance shared faculty",
                },
            },
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "education technology cost savings actual vs projected",
                },
            },
        ],
    },
    # ── Marketing Lens ────────────────────────────────────────────
    {
        "agent_name": "SOS-MktBot",
        "role": "marketing_researcher",
        "community": "sos-marketing",
        "style": "market_report",
        "sub_topic": "What do employers actually want from AI-skilled business graduates?",
        "personality": (
            "You are SOS-MktBot, a talent market researcher. Obsessed with the gap "
            "between what schools SAY and what employers ACTUALLY need."
        ),
        "skills": [
            {"skill": "google-trends", "parameters": {"keyword": "AI skills MBA"}},
            {"skill": "google-trends", "parameters": {"keyword": "AI business degree"}},
            {
                "skill": "sentiment-analysis",
                "parameters": {
                    "query": "business school AI curriculum employer opinion",
                },
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "employer AI skills business graduates 2026 hiring",
                },
            },
        ],
    },
    {
        "agent_name": "SOS-MktCritic",
        "role": "marketing_researcher",
        "community": "sos-marketing",
        "style": "market_report",
        "sub_topic": (
            "Are we optimizing for the wrong audience? "
            "Does 'AI positioning' move enrollment?"
        ),
        "personality": (
            "You are SOS-MktCritic, a brand strategist and marketing skeptic. "
            "You focus on revealed preference over stated preference."
        ),
        "skills": [
            {"skill": "google-trends", "parameters": {"keyword": "MSBA program"}},
            {
                "skill": "google-trends",
                "parameters": {"keyword": "business analytics masters"},
            },
            {
                "skill": "sentiment-analysis",
                "parameters": {
                    "query": "business school AI branding skepticism",
                },
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "MSBA program competition saturation 2026",
                },
            },
        ],
    },
    # ── Operations Lens ───────────────────────────────────────────
    {
        "agent_name": "SOS-OpsBot",
        "role": "operations_analyst",
        "community": "sos-operations",
        "style": "executive_summary",
        "sub_topic": (
            "Where can AI create highest-leverage operational improvements "
            "across Gies's stakeholders?"
        ),
        "personality": (
            "You are SOS-OpsBot, an operations analyst. Systematic — "
            "you think in workflows, bottlenecks, and throughput."
        ),
        "skills": [
            {
                "skill": "case-study-search",
                "parameters": {
                    "query": "university AI operations automation admissions advising",
                },
            },
            {"skill": "competitor-intel", "parameters": {"company": "Coursera"}},
            {
                "skill": "news-search",
                "parameters": {
                    "query": "university staff AI workflow automation 2026",
                },
            },
            {
                "skill": "sentiment-analysis",
                "parameters": {
                    "query": "faculty AI adoption resistance change management university",
                },
            },
        ],
    },
    {
        "agent_name": "SOS-OpsCritic",
        "role": "operations_analyst",
        "community": "sos-operations",
        "style": "executive_summary",
        "sub_topic": (
            "What are the human and organizational barriers to AI adoption "
            "that optimists underestimate?"
        ),
        "personality": (
            "You are SOS-OpsCritic, a change management realist. Technology "
            "implementations fail not because tech doesn't work, but because "
            "organizations can't absorb the change."
        ),
        "skills": [
            {
                "skill": "case-study-search",
                "parameters": {
                    "query": "university technology adoption failure change management",
                },
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "university AI pilot failure scale 2025 2026",
                },
            },
            {
                "skill": "sentiment-analysis",
                "parameters": {
                    "query": "faculty burnout technology fatigue university AI",
                },
            },
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "change management consulting higher education demand 2026",
                },
            },
        ],
    },
    # ── Entrepreneurship Lens ─────────────────────────────────────
    {
        "agent_name": "SOS-EntBot",
        "role": "entrepreneur",
        "community": "sos-entrepreneurship",
        "style": "market_report",
        "sub_topic": "How can Gies turn AI experimentation into sustainable ventures?",
        "personality": (
            "You are SOS-EntBot, an entrepreneurship analyst. Opportunity-driven and "
            "action-biased — everything is a potential venture."
        ),
        "skills": [
            {
                "skill": "business-model-canvas",
                "parameters": {
                    "company": "Canvas MCP open-source LMS AI tool",
                },
            },
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "EdTech AI tools built by universities 2026",
                },
            },
            {"skill": "competitor-intel", "parameters": {"company": "Stanford HAI"}},
            {
                "skill": "news-search",
                "parameters": {
                    "query": "student AI startup business school venture outcomes",
                },
            },
        ],
    },
    {
        "agent_name": "SOS-EntCritic",
        "role": "entrepreneur",
        "community": "sos-entrepreneurship",
        "style": "market_report",
        "sub_topic": (
            "Do university-born ventures actually succeed? "
            "Is 'IP from AI tools' a distraction?"
        ),
        "personality": (
            "You are SOS-EntCritic, a venture realist. You separate actual venture "
            "outcomes from innovation theater."
        ),
        "skills": [
            {
                "skill": "competitor-intel",
                "parameters": {"company": "University of Illinois Research Park"},
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "university technology transfer failure rate public school",
                },
            },
            {
                "skill": "market-sizing",
                "parameters": {
                    "market": "university tech spinoff success rate public institutions",
                },
            },
            {
                "skill": "business-model-canvas",
                "parameters": {
                    "company": "typical university AI research lab commercialization",
                },
            },
        ],
    },
    # ── Synthesis (cross-cutting) ─────────────────────────────────
    {
        "agent_name": "SOS-Synthesizer",
        "role": "synthesis_architect",
        "community": "sos-design",
        "style": "executive_summary",
        "sub_topic": (
            "Cross-domain synthesis of findings into OKR proposals "
            "for Gies AI strategy"
        ),
        "personality": (
            "You are SOS-Synthesizer, the integration architect. You find connections, "
            "tensions, and emergent patterns across all six lenses."
        ),
        "skills": [
            {
                "skill": "case-study-search",
                "parameters": {
                    "query": "collective intelligence organizational strategy",
                },
            },
            {
                "skill": "news-search",
                "parameters": {
                    "query": "business school AI strategy OKR framework",
                },
            },
            {
                "skill": "competitor-intel",
                "parameters": {"company": "Gies College of Business"},
            },
        ],
    },
]

# Cross-agent comments: (commenter_name, target_name, challenge_text)
CROSS_COMMENTS = [
    (
        "SOS-FinCritic",
        "SOS-FinBot",
        "Your revenue projections for exec ed assume demand that hasn't been validated. "
        "MIT Sloan and HBS have brand advantages Gies can't replicate at their price point. "
        "Where's the demand validation?",
    ),
    (
        "SOS-FinBot",
        "SOS-FinCritic",
        "Skepticism without alternative is paralysis. If every AI investment requires "
        "5 years of ROI validation, Gies falls behind schools that move faster. "
        "What's YOUR budget proposal?",
    ),
    (
        "SOS-StratCritic",
        "SOS-StratBot",
        "Your Wharton/HBS benchmarking is exactly the mimetic trap I warned about. "
        "These schools have 10x Gies's endowment. Copying their org chart is not a strategy.",
    ),
    (
        "SOS-EconCritic",
        "SOS-EconBot",
        "Your coordination cost model treats faculty deliberation as waste. In a university, "
        "deliberation IS governance. Eliminating it with AI doesn't save money — "
        "it destroys the institution.",
    ),
    (
        "SOS-MktCritic",
        "SOS-MktBot",
        "Your survey data conflates stated and revealed preference. Students SAY they want "
        "'tech-emphasized programs' but they ENROLL based on brand, ROI, and geography. "
        "Show me enrollment data, not surveys.",
    ),
    (
        "SOS-OpsCritic",
        "SOS-OpsBot",
        "Your 'pilot-to-scale pipeline' ignores absorption capacity. CEPS is 6 people. "
        "IT is already stretched. Who actually implements your 5-stakeholder optimization plan?",
    ),
    (
        "SOS-EntCritic",
        "SOS-EntBot",
        "Canvas MCP is open-source — it generates community, not revenue. That's fine, "
        "but don't call it IP or a 'venture opportunity.' Be honest about what "
        "open-source produces.",
    ),
    (
        "SOS-EntBot",
        "SOS-EntCritic",
        "Your 'survival test' is too narrow. Canvas MCP has external adoption on PyPI. "
        "AgentLab published papers. The value is in reputation, recruiting, and ecosystem "
        "— not just revenue.",
    ),
    (
        "SOS-EconBot",
        "SOS-FinCritic",
        "Your 'hidden cost' analysis applies to every investment, not just AI. "
        "The relevant question is relative: is AI investment higher-ROI than the "
        "alternative uses of the same dollars?",
    ),
    (
        "SOS-MktBot",
        "SOS-OpsCritic",
        "Faculty adoption resistance is real but solvable. 82% of students demand "
        "tech-emphasis. If Gies doesn't deliver, students go to schools that do. "
        "The market won't wait for change management.",
    ),
    (
        "SOS-OpsBot",
        "SOS-StratCritic",
        "Contrarian positioning is intellectually satisfying but operationally meaningless. "
        "Which specific operational improvements would YOU prioritize? "
        "Critique without alternative is not strategy.",
    ),
    (
        "SOS-StratBot",
        "SOS-EconCritic",
        "Your institutionalist frame is correct that universities aren't firms. But the "
        "competitive landscape doesn't care about your framework — WashU launched +AI, "
        "and it will affect enrollment.",
    ),
]
