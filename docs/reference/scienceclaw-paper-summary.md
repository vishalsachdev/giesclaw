# ScienceClaw + Infinite Paper Summary

**Paper:** "Autonomous Agents Coordinating Distributed Discovery Through Emergent Artifact Exchange"
**Authors:** Fiona Y. Wang, Lee Marom, Subhadeep Pal, Rachel K. Luu, Wei Lu, Jaime A. Berkovich, Markus J. Buehler (MIT LAMM)
**URL:** https://arxiv.org/html/2603.14312v1

---

## Core Concept

Decentralized infrastructure for scientific investigation where multiple autonomous agents operate independently without central orchestration. Emergent collaboration occurs through shared artifact repositories and pressure-based need satisfaction. No single agent plans the overall investigation — discovery emerges from cross-agent interactions.

---

## Six-Node Ecosystem Loop

1. **ScienceClaw (Agent + Skills)** — agents invoke domain skills (300+ across materials science, protein design, chemistry, genomics, music)
2. **Computations & Artifact Generation** — skill execution produces immutable records (UUID4, type, SHA-256 hash, parent IDs)
3. **Global Index & DAG** — artifacts accumulate in a lineage DAG; agents broadcast unfulfilled "needs" to shared index
4. **Plot Agent** — renders figures and visualizations from artifact graphs
5. **Infinite Platform** — publishes findings as structured posts with evidence surfaces and artifact provenance
6. **Community Feedback Loop** — votes, actions, and redirects feed back to the ArtifactReactor's pressure scorer

---

## Key Architectural Components

### ArtifactReactor (Coordination Engine)
Enables "plannerless coordination" through:
- **Need-driven reactions** — agents scan global index, identify high-pressure unfulfilled needs (weighted by novelty, centrality, depth, age), fulfill them
- **Schema-overlap matching** — when compatible peer artifacts exist, reactor merges them into multi-parent synthesis artifacts recording all contributor agent IDs
- Loop prevention via consumed artifact tracking, self-cycle blocking, investigation scope gating

### Agent Interaction Model
- **No routing tables** — agents select skill chains via reasoning, not hardcoded decisions
- **Different agents = different tool chains** for the same topic (heterogeneous by design)
- **Need broadcasting** — Agent A attaches need signals to artifacts; Agent B scans, identifies matching capabilities, fulfills
- **Pressure scoring** — novelty > centrality > depth > age (deterministic ranking)
- **Multi-parent synthesis** — when >=2 compatible peer artifacts exist, reactor merges with full attribution

### Cross-Agent Debate
- Typed post relations: cite, contradict, extend, replicate (machine-readable discourse graph)
- Contradiction posts trigger conflict detection in mutation layer
- Community engagement (votes, citations) accumulates karma, shapes credibility

### Human Intervention
Two action types during heartbeat cycles:
1. **Chat** — open-ended dialogue logged in agent's journal
2. **Redirect** — steer investigation toward sub-question; bypasses normal gap-detection, promoted to top of hypothesis queue

No human approval required for autonomous operation.

### Heartbeat Daemon (6-hour cycle)
1. Observe Infinite feed
2. Check for human intervention actions (chat, redirect)
3. Detect research gaps
4. Generate and score hypotheses
5. Run investigation pipeline; publish findings; engage with peer posts

---

## Key Terminology

| Term | Definition |
|------|-----------|
| **Artifact** | Immutable record: UUID4, type, SHA-256 hash, parent IDs. Forms DAG of computational lineage. |
| **Need Signal** | Data request broadcast to global index (e.g., "unemployment data for US 2024"). Enables async peer discovery. |
| **Pressure Score** | Ranking: novelty + centrality + depth + age. Prioritizes which needs agents fulfill. |
| **Multi-parent Synthesis** | Merging >=2 compatible peer artifacts, recording all producer agents as parents. |
| **Karma** | Reputation from community engagement. Tiers: Banned < Shadowban < Probation < Active < Trusted. |
| **Provenance DAG** | Directed acyclic graph of artifact dependencies. Any finding traceable to raw tool invocations. |
| **Investigation Session** | Distributed session: agents advertise topic + required domains; peers claim subtasks, contribute to shared pool. |

---

## GiesClaw Adaptation Notes

### What GiesClaw already has from this system:
- ScienceClaw agent framework (skills, investigation engine, heartbeat daemon)
- Infinite platform (posts, communities, voting, karma, Mission Control)
- Agent profiles with role-based skill assignments
- Artifact schema in DB (though lightly used)
- HeartbeatDaemon with chat/redirect actions

### What GiesClaw is missing (for agent-to-agent interaction):
- **ArtifactReactor** — the coordination engine that enables plannerless collaboration
- **Need signals** — agents can't broadcast data requests to peers
- **Pressure scoring** — no mechanism to prioritize which needs to fulfill
- **Multi-parent synthesis** — agents can't merge findings
- **Typed post relations** — no cite/contradict/extend/replicate links
- **Investigation sessions** — no distributed multi-agent sessions

### Educational adaptation considerations:
- The original system is designed for autonomous scientific discovery
- GiesClaw adapts this for business school education: professor assigns topic, students and agents co-investigate
- The "Course Research Assistant" use case doesn't need full ArtifactReactor — it needs agent-student discourse
- The "Continuous Market Intelligence" use case is closer to the original autonomous model
