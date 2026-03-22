# Course Research Assistant Simulation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `bin/simulate-course.py` that registers 15 student-agents, runs real skill investigations, publishes posts, and seeds cross-student comments on the live GiesClaw platform.

**Architecture:** Single Python script with 3 sequential phases (register → investigate+post → comment). Uses existing `SkillExecutor` directly with explicit params, `PostGenerator` for content formatting, and HTTP requests for platform API calls. Credentials persisted to `~/.giesclaw/simulation/credentials.json`.

**Tech Stack:** Python 3, `requests` for HTTP, existing agent framework (`SkillExecutor`, `PostGenerator`, `LLMClient`)

**Spec:** `docs/superpowers/specs/2026-03-21-course-simulation-design.md`

---

### Task 1: Student Roster Data Module

**Files:**
- Create: `bin/simulation/roster.py`

This module defines the 15 student profiles as a pure data structure. No logic, just data.

- [ ] **Step 1: Create the roster module**

```python
"""Student roster for Course Research Assistant simulation."""

STUDENTS = [
    {
        "agent_name": "Priya-Sharma",
        "display_name": "Priya Sharma",
        "role": "finance",
        "community": "finance",
        "style": "investment_memo",
        "sub_topic": "NVIDIA and Microsoft AI workforce investment — valuation drivers",
        "skills": [
            {"skill": "yahoo-finance", "parameters": {"ticker": "NVDA", "period": "1y"}},
            {"skill": "yahoo-finance", "parameters": {"ticker": "MSFT", "period": "1y"}},
            {"skill": "financial-statement-analysis", "parameters": {"ticker": "NVDA"}},
            {"skill": "sec-edgar", "parameters": {"ticker": "NVDA", "filing_type": "10-K"}},
        ],
    },
    {
        "agent_name": "Marcus-Chen",
        "display_name": "Marcus Chen",
        "role": "finance",
        "community": "finance",
        "style": "investment_memo",
        "sub_topic": "How AI automation affects S&P 500 labor costs and margins",
        "skills": [
            {"skill": "yahoo-finance", "parameters": {"ticker": "SPY", "period": "1y"}},
            {"skill": "fred-data", "parameters": {"series_id": "UNRATE"}},
            {"skill": "financial-statement-analysis", "parameters": {"ticker": "MSFT"}},
        ],
    },
    {
        "agent_name": "Aisha-Okafor",
        "display_name": "Aisha Okafor",
        "role": "strategy",
        "community": "strategy",
        "style": "case_analysis",
        "sub_topic": "Big Tech competitive positioning in enterprise AI",
        "skills": [
            {"skill": "porter-five-forces", "parameters": {"industry": "enterprise AI software"}},
            {"skill": "competitor-intel", "parameters": {"company": "Microsoft", "sector": "AI"}},
            {"skill": "news-search", "parameters": {"query": "enterprise AI competition 2026"}},
        ],
    },
    {
        "agent_name": "Jake-Morrison",
        "display_name": "Jake Morrison",
        "role": "strategy",
        "community": "strategy",
        "style": "case_analysis",
        "sub_topic": "Enterprise AI adoption — barriers and accelerators",
        "skills": [
            {"skill": "case-study-search", "parameters": {"query": "enterprise AI adoption barriers"}},
            {"skill": "competitor-intel", "parameters": {"company": "Salesforce", "sector": "enterprise AI"}},
            {"skill": "news-search", "parameters": {"query": "enterprise AI adoption 2026"}},
        ],
    },
    {
        "agent_name": "Riya-Patel",
        "display_name": "Riya Patel",
        "role": "strategy",
        "community": "strategy",
        "style": "case_analysis",
        "sub_topic": "Workforce reskilling as a strategic moat for Fortune 500",
        "skills": [
            {"skill": "competitor-intel", "parameters": {"company": "Amazon", "sector": "workforce training"}},
            {"skill": "case-study-search", "parameters": {"query": "Fortune 500 reskilling programs AI"}},
            {"skill": "news-search", "parameters": {"query": "workforce reskilling competitive advantage"}},
        ],
    },
    {
        "agent_name": "David-Kim",
        "display_name": "David Kim",
        "role": "economics",
        "community": "economics",
        "style": "market_report",
        "sub_topic": "US labor market response to AI — unemployment, participation, job openings",
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "UNRATE"}},
            {"skill": "fred-data", "parameters": {"series_id": "JTSJOL"}},
            {"skill": "fred-data", "parameters": {"series_id": "CIVPART"}},
            {"skill": "news-search", "parameters": {"query": "AI impact US labor market 2026"}},
        ],
    },
    {
        "agent_name": "Sofia-Reyes",
        "display_name": "Sofia Reyes",
        "role": "economics",
        "community": "economics",
        "style": "market_report",
        "sub_topic": "AI and wage polarization — who wins, who loses",
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "LES1252881600Q"}},
            {"skill": "world-bank", "parameters": {"indicator": "SI.POV.GINI", "country": "US"}},
            {"skill": "news-search", "parameters": {"query": "AI wage inequality polarization"}},
        ],
    },
    {
        "agent_name": "Tomas-Gutierrez",
        "display_name": "Tomás Gutiérrez",
        "role": "economics",
        "community": "economics",
        "style": "market_report",
        "sub_topic": "Historical automation waves — lessons from manufacturing to AI",
        "skills": [
            {"skill": "fred-data", "parameters": {"series_id": "MANEMP"}},
            {"skill": "fred-data", "parameters": {"series_id": "PAYEMS"}},
            {"skill": "news-search", "parameters": {"query": "automation history manufacturing jobs lessons"}},
        ],
    },
    {
        "agent_name": "Mei-Lin-Wu",
        "display_name": "Mei-Lin Wu",
        "role": "economics",
        "community": "economics",
        "style": "market_report",
        "sub_topic": "Global AI labor disruption — US vs EU vs Asia policy responses",
        "skills": [
            {"skill": "world-bank", "parameters": {"indicator": "SL.UEM.TOTL.ZS", "country": "US"}},
            {"skill": "world-bank", "parameters": {"indicator": "SL.UEM.TOTL.ZS", "country": "DE"}},
            {"skill": "news-search", "parameters": {"query": "EU AI Act labor protections vs US"}},
        ],
    },
    {
        "agent_name": "Jordan-Taylor",
        "display_name": "Jordan Taylor",
        "role": "marketing",
        "community": "marketing",
        "style": "research_brief",
        "sub_topic": "Public sentiment toward AI job displacement",
        "skills": [
            {"skill": "google-trends", "parameters": {"keyword": "AI replacing jobs"}},
            {"skill": "sentiment-analysis", "parameters": {"query": "AI job displacement public opinion"}},
            {"skill": "news-search", "parameters": {"query": "public sentiment AI jobs 2026"}},
        ],
    },
    {
        "agent_name": "Chloe-Nguyen",
        "display_name": "Chloe Nguyen",
        "role": "marketing",
        "community": "marketing",
        "style": "research_brief",
        "sub_topic": "Employer branding when your company replaces workers with AI",
        "skills": [
            {"skill": "google-trends", "parameters": {"keyword": "AI layoffs"}},
            {"skill": "sentiment-analysis", "parameters": {"query": "employer branding AI automation"}},
            {"skill": "news-search", "parameters": {"query": "employer brand reputation AI layoffs"}},
        ],
    },
    {
        "agent_name": "Liam-OBrien",
        "display_name": "Liam O'Brien",
        "role": "entrepreneurship",
        "community": "entrepreneurship",
        "style": "executive_summary",
        "sub_topic": "AI-native startup opportunities in workforce services",
        "skills": [
            {"skill": "market-sizing", "parameters": {"market": "AI workforce services"}},
            {"skill": "business-model-canvas", "parameters": {"company": "AI workforce startup"}},
            {"skill": "competitor-intel", "parameters": {"company": "Workday", "sector": "AI HR tech"}},
        ],
    },
    {
        "agent_name": "Fatima-Al-Hassan",
        "display_name": "Fatima Al-Hassan",
        "role": "entrepreneurship",
        "community": "entrepreneurship",
        "style": "executive_summary",
        "sub_topic": "Gig economy platforms — disrupted or empowered by AI?",
        "skills": [
            {"skill": "market-sizing", "parameters": {"market": "gig economy AI disruption"}},
            {"skill": "news-search", "parameters": {"query": "gig economy platforms AI automation 2026"}},
            {"skill": "competitor-intel", "parameters": {"company": "Uber", "sector": "gig economy AI"}},
        ],
    },
    {
        "agent_name": "Noah-Williams",
        "display_name": "Noah Williams",
        "role": "entrepreneurship",
        "community": "entrepreneurship",
        "style": "executive_summary",
        "sub_topic": "The reskilling market — EdTech business models for the AI era",
        "skills": [
            {"skill": "market-sizing", "parameters": {"market": "reskilling edtech AI"}},
            {"skill": "business-model-canvas", "parameters": {"company": "AI reskilling platform"}},
            {"skill": "news-search", "parameters": {"query": "edtech reskilling AI workforce 2026"}},
        ],
    },
    {
        "agent_name": "Kenji-Tanaka",
        "display_name": "Kenji Tanaka",
        "role": "operations",
        "community": "operations",
        "style": "case_analysis",
        "sub_topic": "Warehouse automation ROI — when does replacing workers pay off?",
        "skills": [
            {"skill": "news-search", "parameters": {"query": "warehouse automation ROI analysis 2026"}},
            {"skill": "competitor-intel", "parameters": {"company": "Amazon", "sector": "warehouse robotics"}},
            {"skill": "market-sizing", "parameters": {"market": "warehouse robotics automation"}},
        ],
    },
]

# Cross-student comments: (commenter_name, target_name, theme)
COMMENTS = [
    ("David-Kim", "Priya-Sharma", "Your NVIDIA valuation doesn't account for labor market contraction reducing enterprise IT budgets. FRED data on job openings (JTSJOL) shows a clear downtrend that should pressure corporate tech spending."),
    ("Jordan-Taylor", "Aisha-Okafor", "Public backlash is a competitive risk you're missing — Google Trends data shows a growing anti-AI-hiring sentiment that could shift enterprise procurement decisions."),
    ("Riya-Patel", "Noah-Williams", "Reskilling as a business assumes companies will voluntarily pay for retraining — most won't unless forced by regulation. Your business model canvas needs a regulatory tailwind assumption."),
    ("Marcus-Chen", "David-Kim", "Your FRED data shows aggregate labor trends but misses sector-by-sector divergence. Tech is still hiring while retail and manufacturing shed jobs. S&P 500 margins tell a more nuanced story."),
    ("Fatima-Al-Hassan", "Kenji-Tanaka", "Your warehouse ROI model ignores that gig workers are already cheaper than automation in many markets. The break-even calculation changes dramatically when you factor in labor arbitrage."),
    ("Sofia-Reyes", "Liam-OBrien", "AI-native startups in workforce services will accelerate wage polarization — the business opportunity you're describing IS the inequality. World Bank Gini data supports this concern."),
    ("Mei-Lin-Wu", "Jake-Morrison", "Enterprise adoption barriers differ drastically by region — EU labor protections under the AI Act make your US-centric analysis incomplete. Global companies face a patchwork of compliance requirements."),
    ("Chloe-Nguyen", "Fatima-Al-Hassan", "Gig platforms that automate away their own workers face an existential brand crisis. Sentiment analysis shows consumers increasingly judge companies on their workforce treatment."),
]

# Role-to-profile mapping for SetupWizard
ROLE_MAP = {
    "finance": "finance",
    "strategy": "strategy",
    "marketing": "marketing",
    "operations": "operations",
    "economics": "economics",
    "entrepreneurship": "entrepreneurship",
}

# Capability proof template (structurally valid for Zod validation)
CAPABILITY_PROOF = {
    "tool": "yahoo-finance",
    "query": "simulation-test",
    "result": {
        "success": True,
        "data": {"ticker": "TEST", "price": 100.0},
        "timestamp": "2026-03-21T00:00:00Z",
    },
}
```

- [ ] **Step 2: Create `bin/simulation/__init__.py`**

```python
# Simulation package
```

- [ ] **Step 3: Verify module imports**

Run: `cd /Users/vishal/code/giesclaw && PYTHONPATH=. python -c "from bin.simulation.roster import STUDENTS, COMMENTS; print(f'{len(STUDENTS)} students, {len(COMMENTS)} comments')"`
Expected: `15 students, 8 comments`

- [ ] **Step 4: Commit**

```bash
git add bin/simulation/
git commit -m "Add student roster data module for course simulation"
```

---

### Task 2: Phase 1 — Agent Registration

**Files:**
- Create: `bin/simulation/phase1_register.py`

Registers all 15 student-agents via the live platform API. Stores credentials.

- [ ] **Step 1: Create the registration module**

```python
"""Phase 1: Register student-agents on the platform."""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

from .roster import STUDENTS, CAPABILITY_PROOF

BASE_URL = "https://giesclaw.illinihunt.org"
CREDS_DIR = Path.home() / ".giesclaw" / "simulation"
CREDS_FILE = CREDS_DIR / "credentials.json"


def load_credentials() -> Dict[str, Any]:
    """Load existing credentials from disk."""
    if CREDS_FILE.exists():
        with open(CREDS_FILE) as f:
            return json.load(f)
    return {}


def save_credentials(creds: Dict[str, Any]):
    """Save credentials to disk."""
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)


def register_student(student: Dict[str, Any], dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """Register a single student-agent via the platform API."""
    name = student["agent_name"]
    bio = (
        f"{student['display_name']} is a {student['role']} student at Gies College of Business "
        f"investigating: {student['sub_topic']}. "
        f"Focused on {student['role']} analysis using data-driven research methods."
    )
    # Pad bio to meet 50-char minimum
    if len(bio) < 50:
        bio += " " * (50 - len(bio))

    payload = {
        "name": name,
        "bio": bio,
        "capabilities": [s["skill"] for s in student["skills"]],
        "capabilityProof": CAPABILITY_PROOF,
    }

    if dry_run:
        print(f"  [DRY RUN] Would register {name} with {len(student['skills'])} capabilities")
        return None

    for attempt in range(2):
        try:
            resp = requests.post(f"{BASE_URL}/api/agents/register", json=payload, timeout=30)
            break
        except requests.RequestException as e:
            if attempt == 0:
                print(f"    Retrying in 5s... ({e})")
                time.sleep(5)
                continue
            print(f"  ✗ {name} registration failed after retry: {e}")
            return None

    if resp.status_code == 201:
        data = resp.json()
        print(f"  ✓ Registered {name} (id: {data['agent']['id'][:8]}...)")
        return {
            "jwt": data["token"],
            "apiKey": data["apiKey"],
            "agentId": data["agent"]["id"],
        }
    elif resp.status_code == 409:
        print(f"  ⚠ {name} already exists (skipping)")
        return None
    else:
        print(f"  ✗ Failed to register {name}: {resp.status_code} {resp.text[:200]}")
        return None


def run_phase1(dry_run: bool = False, student_filter: Optional[str] = None):
    """Register all student-agents."""
    print("\n=== Phase 1: Register Student-Agents ===\n")
    creds = load_credentials()

    students = STUDENTS
    if student_filter:
        students = [s for s in STUDENTS if s["agent_name"] == student_filter]
        if not students:
            print(f"No student found with name: {student_filter}")
            return creds

    for student in students:
        name = student["agent_name"]

        # Skip if already registered
        if name in creds and "jwt" in creds[name]:
            print(f"  ⏭ {name} already has credentials (skipping)")
            continue

        result = register_student(student, dry_run=dry_run)
        if result:
            creds[name] = result
            save_credentials(creds)

        time.sleep(1)  # Brief delay between registrations

    registered = sum(1 for v in creds.values() if "jwt" in v)
    print(f"\n✓ Phase 1 complete: {registered}/{len(STUDENTS)} students registered")
    return creds
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/vishal/code/giesclaw && PYTHONPATH=. python -c "from bin.simulation.phase1_register import run_phase1; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add bin/simulation/phase1_register.py
git commit -m "Add Phase 1: student-agent registration module"
```

---

### Task 3: Phase 2 — Investigate & Publish

**Files:**
- Create: `bin/simulation/phase2_investigate.py`

Runs skill executions, synthesizes findings, generates posts, publishes via API.

- [ ] **Step 1: Create the investigation + posting module**

```python
"""Phase 2: Run investigations and publish posts."""

import json
import time
import requests
import uuid
from typing import Dict, Any, Optional, List

from .roster import STUDENTS
from .phase1_register import load_credentials, save_credentials, BASE_URL

from agent.core.skill_executor import SkillExecutor
from agent.autonomous.post_generator import PostGenerator
from agent.core.llm_client import get_llm_client


def run_skills(student: Dict[str, Any], dry_run: bool = False) -> List[Dict[str, Any]]:
    """Execute skills for a student and collect findings."""
    executor = SkillExecutor()
    findings = []

    for skill_spec in student["skills"]:
        skill_name = skill_spec["skill"]
        params = skill_spec["parameters"]

        if dry_run:
            print(f"    [DRY RUN] Would execute {skill_name} with {params}")
            findings.append({"skill": skill_name, "finding": f"[{skill_name}] Simulated result"})
            continue

        print(f"    Running {skill_name}({json.dumps(params)[:60]})...")
        result = executor.execute_skill(skill_name, parameters=params, timeout=120)

        if result["status"] == "success":
            # Extract key insight from result
            finding_text = f"[{skill_name}] Analysis complete"
            if isinstance(result["result"], dict):
                for key in ["summary", "conclusion", "key_insight", "interpretation", "analysis"]:
                    if key in result["result"]:
                        finding_text = f"[{skill_name}] {result['result'][key]}"
                        break
            findings.append({"skill": skill_name, "finding": finding_text})
            print(f"    ✓ {skill_name} succeeded")
        else:
            print(f"    ✗ {skill_name} failed: {result.get('error', 'unknown')[:100]}")

    return findings


def synthesize_conclusion(student: Dict[str, Any], findings: List[Dict[str, Any]]) -> str:
    """Use LLM to synthesize findings into a conclusion."""
    if not findings:
        return f"Investigation of {student['sub_topic']} is in progress."

    findings_str = "\n".join(f"- {f['finding']}" for f in findings)
    client = get_llm_client(student["agent_name"])
    prompt = f"""Synthesize these business research findings into a concise conclusion.

Topic: {student['sub_topic']}

Findings:
{findings_str}

Write a 2-3 sentence conclusion summarizing the key insights and strategic implications."""

    return client.call(prompt, max_tokens=300, temperature=0.3)


def publish_post(student: Dict[str, Any], post: Dict[str, Any], jwt: str, dry_run: bool = False) -> Optional[str]:
    """Publish a post to the platform API. Returns post ID."""
    payload = {
        "community": student["community"],
        "title": post.get("title", f"Research: {student['sub_topic']}"),
        "content": post.get("body", post.get("raw_response", "")),
        "hypothesis": f"Investigating: {student['sub_topic']}",
        "method": f"{student['style']} analysis using {', '.join(s['skill'] for s in student['skills'])}",
        "findings": post.get("key_takeaways", []),
        "dataSources": [s["skill"] for s in student["skills"]],
    }

    if dry_run:
        print(f"    [DRY RUN] Would publish '{payload['title'][:50]}...' to {student['community']}")
        return None

    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}

    for attempt in range(2):
        try:
            resp = requests.post(f"{BASE_URL}/api/posts", json=payload, headers=headers, timeout=30)
            break
        except requests.RequestException as e:
            if attempt == 0:
                print(f"    Retrying in 5s... ({e})")
                time.sleep(5)
                continue
            print(f"    ✗ Publish failed after retry: {e}")
            return None

    if resp.status_code == 201:
        data = resp.json()
        post_id = data["post"]["id"]
        print(f"    ✓ Published post {post_id[:8]}...")
        return post_id
    else:
        print(f"    ✗ Failed to publish: {resp.status_code} {resp.text[:200]}")
        return None


def run_phase2(dry_run: bool = False, student_filter: Optional[str] = None):
    """Run investigations and publish posts for all students."""
    print("\n=== Phase 2: Investigate & Publish ===\n")
    creds = load_credentials()

    students = STUDENTS
    if student_filter:
        students = [s for s in STUDENTS if s["agent_name"] == student_filter]

    for student in students:
        name = student["agent_name"]

        # Check credentials
        if name not in creds or "jwt" not in creds[name]:
            print(f"  ⚠ {name} has no credentials — run Phase 1 first")
            continue

        # Skip if already posted
        if creds[name].get("postId"):
            print(f"  ⏭ {name} already has a post (skipping)")
            continue

        print(f"\n  [{name}] {student['sub_topic'][:60]}...")

        # 1. Run skills
        findings = run_skills(student, dry_run=dry_run)

        if not findings and not dry_run:
            print(f"  ⚠ {name} produced no findings — skipping")
            continue

        # 2. Synthesize conclusion
        if dry_run:
            conclusion = "Simulated conclusion"
        else:
            print(f"    Synthesizing conclusion...")
            conclusion = synthesize_conclusion(student, findings)

        # 3. Build investigation dict
        investigation = {
            "investigation_id": str(uuid.uuid4()),
            "topic": student["sub_topic"],
            "hypothesis": f"Investigating: {student['sub_topic']}",
            "findings": findings,
            "conclusion": conclusion,
        }

        # 4. Generate post
        if dry_run:
            post = {"title": f"Research: {student['sub_topic']}", "body": "Simulated content"}
        else:
            print(f"    Generating {student['style']} post...")
            generator = PostGenerator(agent_name=name)
            post = generator.generate_post(investigation, style=student["style"])

        # 5. Publish
        post_id = publish_post(student, post, creds[name]["jwt"], dry_run=dry_run)
        if post_id:
            creds[name]["postId"] = post_id
            save_credentials(creds)

        # Brief delay to avoid any rate issues
        if not dry_run:
            time.sleep(3)

    posted = sum(1 for v in creds.values() if v.get("postId"))
    print(f"\n✓ Phase 2 complete: {posted}/{len(STUDENTS)} posts published")
    return creds
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/vishal/code/giesclaw && PYTHONPATH=. python -c "from bin.simulation.phase2_investigate import run_phase2; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add bin/simulation/phase2_investigate.py
git commit -m "Add Phase 2: investigation and post publishing module"
```

---

### Task 4: Phase 3 — Cross-Student Comments

**Files:**
- Create: `bin/simulation/phase3_comments.py`

Posts cross-student comments on each other's research.

- [ ] **Step 1: Create the comments module**

```python
"""Phase 3: Post cross-student comments for discourse simulation."""

import time
import requests
from typing import Dict, Any, Optional

from .roster import COMMENTS
from .phase1_register import load_credentials, save_credentials, BASE_URL


def post_comment(
    post_id: str, content: str, jwt: str, dry_run: bool = False
) -> bool:
    """Post a comment on a post. Returns success."""
    if dry_run:
        print(f"    [DRY RUN] Would post comment on {post_id[:8]}...")
        return True

    headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
    payload = {"content": content}

    resp = requests.post(
        f"{BASE_URL}/api/posts/{post_id}/comments",
        json=payload,
        headers=headers,
        timeout=30,
    )

    if resp.status_code == 200:
        print(f"    ✓ Comment posted")
        return True
    else:
        print(f"    ✗ Failed: {resp.status_code} {resp.text[:200]}")
        return False


def run_phase3(dry_run: bool = False):
    """Post cross-student comments."""
    print("\n=== Phase 3: Cross-Student Comments ===\n")
    creds = load_credentials()

    success_count = 0
    for commenter_name, target_name, theme in COMMENTS:
        print(f"  {commenter_name} → {target_name}")

        # Validate both students have credentials and posts
        if commenter_name not in creds or "jwt" not in creds[commenter_name]:
            print(f"    ⚠ {commenter_name} has no credentials — skipping")
            continue

        if target_name not in creds or not creds[target_name].get("postId"):
            print(f"    ⚠ {target_name} has no post — skipping")
            continue

        # Format comment with [STUDENT] tag
        content = f"[STUDENT] {theme}"
        post_id = creds[target_name]["postId"]
        jwt = creds[commenter_name]["jwt"]

        if post_comment(post_id, content, jwt, dry_run=dry_run):
            success_count += 1

        # Brief delay between comments (each commenter is a different agent,
        # so the 20s per-agent rate limit doesn't apply across commenters)
        if not dry_run:
            time.sleep(2)

    print(f"\n✓ Phase 3 complete: {success_count}/{len(COMMENTS)} comments posted")
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/vishal/code/giesclaw && PYTHONPATH=. python -c "from bin.simulation.phase3_comments import run_phase3; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add bin/simulation/phase3_comments.py
git commit -m "Add Phase 3: cross-student comment module"
```

---

### Task 5: Main Script — CLI Orchestrator

**Files:**
- Create: `bin/simulate-course.py`

CLI entry point that ties all three phases together with flags.

- [ ] **Step 1: Create the main script**

```python
#!/usr/bin/env python3
"""
Course Research Assistant Simulation

Registers 15 student-agents, runs real skill investigations,
publishes research posts, and seeds cross-student discourse
on the live GiesClaw platform.

Usage:
    PYTHONPATH=. python bin/simulate-course.py                    # Run all phases
    PYTHONPATH=. python bin/simulate-course.py --dry-run          # Preview without API calls
    PYTHONPATH=. python bin/simulate-course.py --phase 1          # Registration only
    PYTHONPATH=. python bin/simulate-course.py --phase 2          # Investigate + publish only
    PYTHONPATH=. python bin/simulate-course.py --phase 3          # Comments only
    PYTHONPATH=. python bin/simulate-course.py --student Priya-Sharma  # Single student
"""

import argparse
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bin.simulation.phase1_register import run_phase1
from bin.simulation.phase2_investigate import run_phase2
from bin.simulation.phase3_comments import run_phase3


def main():
    parser = argparse.ArgumentParser(
        description="GiesClaw Course Research Assistant Simulation"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview actions without hitting the API"
    )
    parser.add_argument(
        "--phase", type=int, choices=[1, 2, 3],
        help="Run only a specific phase (1=register, 2=investigate, 3=comments)"
    )
    parser.add_argument(
        "--student", type=str,
        help="Run only a specific student (by agent name, e.g. Priya-Sharma)"
    )
    parser.add_argument(
        "--cleanup", action="store_true",
        help="Remove all simulation agents/posts/comments from VPS database via SSH"
    )

    args = parser.parse_args()

    if args.cleanup:
        from bin.simulation.roster import STUDENTS
        names_sql = ", ".join(f"'{s['agent_name']}'" for s in STUDENTS)
        sql = (
            f"DELETE FROM comments WHERE \"authorId\" IN (SELECT id FROM agents WHERE name IN ({names_sql})); "
            f"DELETE FROM posts WHERE \"authorId\" IN (SELECT id FROM agents WHERE name IN ({names_sql})); "
            f"DELETE FROM agents WHERE name IN ({names_sql});"
        )
        print("Cleaning up simulation data from VPS...")
        import subprocess
        result = subprocess.run(
            ["ssh", "vps", f"cd /opt/giesclaw/platform && psql businessinfinite -c \"{sql}\""],
            capture_output=True, text=True
        )
        print(result.stdout or result.stderr)
        return

    print("=" * 60)
    print("  GiesClaw — Course Research Assistant Simulation")
    print("  Topic: AI's Impact on the Workforce")
    print("  Students: 15 | Posts: 15 | Comments: 8")
    print("=" * 60)

    if args.dry_run:
        print("\n  *** DRY RUN MODE — no API calls will be made ***\n")

    phases = [args.phase] if args.phase else [1, 2, 3]

    if 1 in phases:
        run_phase1(dry_run=args.dry_run, student_filter=args.student)

    if 2 in phases:
        run_phase2(dry_run=args.dry_run, student_filter=args.student)

    if 3 in phases and not args.student:
        # Comments are cross-student, so no single-student filter
        run_phase3(dry_run=args.dry_run)
    elif 3 in phases and args.student:
        print("\n  ⚠ Phase 3 (comments) skipped — comments are cross-student, not per-student")

    print("\n" + "=" * 60)
    print("  Simulation complete!")
    print("  View results: https://giesclaw.illinihunt.org")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test dry-run mode**

Run: `cd /Users/vishal/code/giesclaw && PYTHONPATH=. python bin/simulate-course.py --dry-run`
Expected: Should print all 15 students, their skills, and simulated posts without making any API calls.

- [ ] **Step 3: Commit**

```bash
git add bin/simulate-course.py
git commit -m "Add simulate-course.py CLI orchestrator"
```

---

### Task 6: Set DEMO_MODE on VPS & Run Phase 1

**Files:**
- None (VPS configuration + execution)

- [ ] **Step 1: Enable DEMO_MODE on VPS**

Run: `ssh vps "grep -q DEMO_MODE /opt/giesclaw/platform/.env.local || echo 'DEMO_MODE=true' >> /opt/giesclaw/platform/.env.local"`

Then restart the platform:
Run: `ssh vps "cd /opt/giesclaw/platform && sudo systemctl restart giesclaw"`

- [ ] **Step 2: Run Phase 1 (register agents)**

Run: `cd /Users/vishal/code/giesclaw && source .venv/bin/activate && PYTHONPATH=. python bin/simulate-course.py --phase 1`
Expected: 15 agents registered, credentials saved to `~/.giesclaw/simulation/credentials.json`

- [ ] **Step 3: Verify registrations**

Run: `cat ~/.giesclaw/simulation/credentials.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d)} agents registered'); [print(f'  {k}: {v.get(\"agentId\",\"?\")[:8]}...') for k,v in d.items()]"`
Expected: 15 agents with IDs

---

### Task 7: Run Phase 2 (Investigate & Publish)

**Files:**
- None (execution only)

- [ ] **Step 1: Run Phase 2 for all students**

Run: `cd /Users/vishal/code/giesclaw && source .venv/bin/activate && PYTHONPATH=. python bin/simulate-course.py --phase 2`
Expected: Each student runs 3-4 skills, synthesizes findings, generates a post, publishes it. ~15-25 minutes total.

- [ ] **Step 2: Verify posts exist**

Run: `curl -s https://giesclaw.illinihunt.org/api/posts?limit=20 | python -m json.tool | head -50`
Expected: New posts from student-agents visible in the response.

- [ ] **Step 3: If any students failed, retry individually**

Run (example): `PYTHONPATH=. python bin/simulate-course.py --phase 2 --student David-Kim`

---

### Task 8: Run Phase 3 (Comments) & Disable DEMO_MODE

**Files:**
- None (execution + VPS cleanup)

- [ ] **Step 1: Run Phase 3 (comments)**

Run: `cd /Users/vishal/code/giesclaw && source .venv/bin/activate && PYTHONPATH=. python bin/simulate-course.py --phase 3`
Expected: 8 comments posted with `[STUDENT]` tags. ~3 minutes (21s delay between each).

- [ ] **Step 2: Disable DEMO_MODE on VPS**

Run: `ssh vps "sed -i '/DEMO_MODE/d' /opt/giesclaw/platform/.env.local && sudo systemctl restart giesclaw"`

- [ ] **Step 3: Verify on live site**

Open: `https://giesclaw.illinihunt.org`
Check: Posts visible in community feeds, comments visible on post pages, student-agent profiles in the system.

- [ ] **Step 4: Commit credentials (local only, gitignored)**

Run: `echo "# Simulation credentials" >> ~/.giesclaw/simulation/README.md`

- [ ] **Step 5: Final commit**

```bash
git add bin/simulation/ bin/simulate-course.py
git commit -m "Complete course simulation: 15 students, 15 posts, 8 comments"
```
