# BusinessClaw

**Autonomous Business Investigation Framework for Business Schools**

Adapted from [ScienceClaw](https://github.com/lamm-mit/scienceclaw) — replacing 300+ scientific tools with business-relevant skills spanning finance, marketing, strategy, operations, economics, and entrepreneurship.

BusinessClaw enables independent AI agents to conduct autonomous business research: analyzing companies, evaluating competitive dynamics, sizing markets, and synthesizing findings into investment memos, case analyses, and executive summaries.

## Architecture

```
businessclaw/
├── core/                    # Core engine
│   ├── llm_client.py        # Multi-backend LLM client (OpenAI, Anthropic, HuggingFace)
│   ├── skill_registry.py    # Skill discovery, indexing, and recommendation
│   ├── skill_executor.py    # Universal skill execution engine
│   └── topic_analyzer.py    # Topic classification and decomposition
├── artifacts/               # Research provenance
│   ├── artifact.py          # Immutable research records with DAG lineage
│   └── reactor.py           # Emergent multi-agent coordination
├── memory/                  # Persistent memory
│   ├── journal.py           # Chronological research log (JSONL)
│   ├── investigation_tracker.py  # Multi-step investigation lifecycle
│   └── knowledge_graph.py   # Entity-relationship graph
├── skills/                  # Business research tools
│   ├── yahoo-finance/       # Market data & company financials
│   ├── sec-edgar/           # SEC regulatory filings (10-K, 10-Q, 8-K)
│   ├── fred-data/           # Federal Reserve economic data
│   ├── google-trends/       # Search interest & consumer trends
│   ├── porter-five-forces/  # Competitive dynamics analysis
│   ├── market-sizing/       # TAM/SAM/SOM estimation
│   ├── case-study-search/   # Business school case finder
│   ├── sentiment-analysis/  # Brand & market sentiment (NLP)
│   ├── business-model-canvas/ # Osterwalder BMC analysis
│   ├── financial-statement-analysis/ # Ratios, DuPont, common-size
│   ├── competitor-intel/    # Competitive intelligence & benchmarking
│   ├── news-search/         # Business news aggregation (RSS)
│   └── world-bank/          # Development indicators (190 countries)
├── reasoning/               # Analysis engine
│   ├── gap_detector.py      # Identify missing research angles
│   ├── hypothesis_generator.py  # Generate testable hypotheses
│   └── investigation_engine.py  # End-to-end research orchestration
├── autonomous/              # Continuous operation
│   ├── heartbeat_daemon.py  # Scheduled research cycles
│   └── post_generator.py    # Publishable output generation
├── coordination/            # Multi-agent
│   └── role_manager.py      # Business school department roles
└── setup/                   # Configuration
    └── setup_wizard.py      # Interactive/quick agent setup
```

## Quick Start

### Installation

```bash
git clone <this-repo>
cd businessclaw
pip install -r requirements.txt

# Domain-specific dependencies
pip install -r requirements/finance.txt      # yfinance, fredapi, sec-edgar
pip install -r requirements/marketing.txt    # pytrends, textblob
pip install -r requirements/data-science.txt # sklearn, matplotlib, statsmodels
```

### Agent Setup

```bash
# Interactive wizard
python -m businessclaw.setup.setup_wizard

# Quick setup with presets
python -m businessclaw.setup.setup_wizard --quick --profile finance --name "FinBot-1"
python -m businessclaw.setup.setup_wizard --quick --profile strategy --name "StratBot-1"
python -m businessclaw.setup.setup_wizard --quick --profile marketing --name "MktBot-1"
python -m businessclaw.setup.setup_wizard --quick --profile economics --name "EconBot-1"
python -m businessclaw.setup.setup_wizard --quick --profile entrepreneurship --name "VCBot-1"
```

### Configuration

```bash
export LLM_BACKEND=openai          # or anthropic, huggingface
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
export FRED_API_KEY=your_key       # Free at https://fred.stlouisfed.org/docs/api/api_key.html
```

### Run Investigations

```bash
# Single investigation with post
./bin/businessclaw-post --agent FinBot --topic "Apple services segment valuation" --style investment_memo

# Dry run (plan only)
./bin/businessclaw-post --agent FinBot --topic "Tesla competitive positioning" --dry-run

# Quick skill chain
./bin/businessclaw-investigate --topic "AAPL" --skills yahoo-finance,financial-statement-analysis

# Continuous daemon (every 6 hours)
python -m businessclaw.autonomous.heartbeat_daemon background --profile finbot-1

# Single daemon cycle
python -m businessclaw.autonomous.heartbeat_daemon once --profile finbot-1
```

### Skill Catalog

```bash
python -m businessclaw.skill_catalog --stats
python -m businessclaw.skill_catalog --list
python -m businessclaw.skill_catalog --search "valuation"
python -m businessclaw.skill_catalog --suggest "Apple competitive strategy"
python -m businessclaw.skill_catalog --category finance
```

### Memory CLI

```bash
python -m businessclaw.memory.tools.cli --agent FinBot journal search "AAPL"
python -m businessclaw.memory.tools.cli --agent FinBot journal stats
python -m businessclaw.memory.tools.cli --agent FinBot investigations list
python -m businessclaw.memory.tools.cli --agent FinBot knowledge search "Apple"
```

## Agent Roles (Business School Departments)

| Role | Department | Core Skills | Frameworks |
|------|-----------|-------------|------------|
| `finance_analyst` | Finance | Yahoo Finance, SEC EDGAR, Ratio Analysis | DCF, WACC, CAPM, LBO |
| `strategy_consultant` | Strategy | Porter's 5 Forces, Competitor Intel, Cases | SWOT, Value Chain, BCG Matrix |
| `marketing_researcher` | Marketing | Google Trends, Sentiment, Market Sizing | STP, 4Ps, Customer Journey |
| `operations_analyst` | Operations | Supply Chain, Process Optimization | Lean, Six Sigma, TOC |
| `economist` | Economics | FRED, World Bank, Forecasting | IS-LM, AS-AD, Phillips Curve |
| `entrepreneur` | Entrepreneurship | Market Sizing, BMC, Competitor Intel | Lean Startup, TAM/SAM/SOM |

## How It Works

### Investigation Lifecycle

1. **Topic Analysis** — Classify research topic into business domains
2. **Skill Selection** — Match relevant tools from the skill registry
3. **Hypothesis Generation** — LLM generates testable business hypotheses
4. **Skill Execution** — Run selected tools, producing artifacts
5. **Gap Detection** — Identify missing analyses and data
6. **Conclusion Synthesis** — LLM synthesizes findings
7. **Post Generation** — Format output as investment memo, case analysis, etc.

### Artifact DAG

Every skill execution produces an immutable artifact with:
- Unique ID and content hash (SHA-256)
- Parent artifact references (provenance chain)
- Investigation linkage
- Domain-typed classification

### Multi-Agent Coordination

The ArtifactReactor enables emergent coordination:
- Finance agent broadcasts need for competitive analysis
- Strategy agent detects schema overlap and fulfills the need
- Results link via artifact lineage without explicit orchestration

### Output Styles

- **Research Brief** — Concise 300-word summary
- **Case Analysis** — Situation/analysis/recommendation format
- **Market Report** — Data-driven market insights
- **Investment Memo** — Thesis/evidence/risks format
- **Executive Summary** — C-suite key takeaways

## Mapping: ScienceClaw → BusinessClaw

| ScienceClaw | BusinessClaw |
|-------------|-------------|
| PubMed, ArXiv | SEC EDGAR, FRED, World Bank |
| BLAST, UniProt | Yahoo Finance, Financial Statements |
| AlphaFold, Chai | Porter's Five Forces, SWOT |
| RDKit, PubChem | Sentiment Analysis, Google Trends |
| Materials Project | Market Sizing, Business Model Canvas |
| Scientific papers | Case studies, earnings calls |
| Lab experiments | Financial models, market analyses |
| Research communities | Business school departments |

## License

Apache License 2.0 (same as ScienceClaw)
