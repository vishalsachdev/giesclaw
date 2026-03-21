"""
Investigation Engine - Orchestrate deep business research investigations.

Coordinates the full lifecycle: topic analysis -> hypothesis generation ->
skill selection -> execution -> gap detection -> conclusion.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..core.llm_client import get_llm_client
from ..core.skill_executor import get_executor
from ..core.skill_registry import get_registry
from ..core.topic_analyzer import classify_topic
from ..artifacts import ArtifactStore
from ..memory.journal import AgentJournal
from ..memory.investigation_tracker import InvestigationTracker
from .gap_detector import GapDetector
from .hypothesis_generator import HypothesisGenerator


class InvestigationEngine:
    """Orchestrate end-to-end business research investigations."""

    def __init__(self, agent_name: str, profile: Optional[Dict[str, Any]] = None):
        self.agent_name = agent_name
        self.profile = profile or {}
        self.journal = AgentJournal(agent_name)
        self.tracker = InvestigationTracker(agent_name)
        self.artifact_store = ArtifactStore(agent_name)
        self.executor = get_executor()
        self.registry = get_registry()
        self.gap_detector = GapDetector(agent_name)
        self.hypothesis_gen = HypothesisGenerator(agent_name)

    def investigate(
        self,
        topic: str,
        max_steps: int = 5,
        auto_hypothesis: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a complete investigation on a business topic.

        Args:
            topic: Research topic or question
            max_steps: Maximum skill executions
            auto_hypothesis: Whether to auto-generate hypotheses

        Returns:
            Investigation summary with findings and conclusion
        """
        # 1. Classify topic and select skills
        domains = classify_topic(topic)
        domain_names = [d["domain"] for d in domains[:3]]
        suggested_skills = []
        for d in domains[:3]:
            suggested_skills.extend(d["suggested_skills"])

        # 2. Start investigation
        inv_id = self.tracker.start_investigation(
            topic=topic,
            domains=domain_names,
            planned_skills=suggested_skills[:max_steps],
        )

        self.journal.log_observation(
            content=f"Starting investigation: {topic}",
            source="investigation_engine",
            tags=domain_names,
        )

        # 3. Generate hypothesis if requested
        hypothesis = None
        if auto_hypothesis:
            prior_topics = list(self.journal.get_investigated_topics())
            hyp_result = self.hypothesis_gen.generate_hypotheses(
                topic=topic,
                prior_hypotheses=prior_topics[:5],
                domain=domain_names[0] if domain_names else "general",
            )
            hypotheses = hyp_result.get("hypotheses", [])
            if hypotheses:
                hypothesis = hypotheses[0].get("hypothesis", "")
                self.journal.log_hypothesis(
                    hypothesis=hypothesis,
                    motivation=hypotheses[0].get("rationale", ""),
                )
                self.tracker.investigations[inv_id]["hypothesis"] = hypothesis

        # 4. Execute skills
        findings = []
        for i, skill_name in enumerate(suggested_skills[:max_steps]):
            if skill_name not in [s for s in self.registry.list_all()]:
                continue

            result = self.executor.execute_skill(skill_name)

            if result["status"] == "success":
                # Create artifact
                artifact = self.artifact_store.create(
                    skill=skill_name,
                    content=result["result"],
                    investigation_id=inv_id,
                )

                finding = f"[{skill_name}] Analysis complete"
                if isinstance(result["result"], dict):
                    # Extract key insight
                    for key in ["summary", "conclusion", "key_insight", "interpretation"]:
                        if key in result["result"]:
                            finding = f"[{skill_name}] {result['result'][key]}"
                            break

                findings.append({"skill": skill_name, "finding": finding})
                self.tracker.record_skill_execution(
                    inv_id, skill_name, artifact.artifact_id, finding
                )
                self.journal.log_analysis(
                    description=finding,
                    tool=skill_name,
                    parameters={},
                    results={**result["result"], "_artifact_id": artifact.artifact_id},
                )

        # 5. Detect gaps
        gaps = self.gap_detector.detect_gaps(
            topic=topic,
            completed_skills=[f["skill"] for f in findings],
            findings=findings,
            available_skills=self.registry.list_all(),
        )

        for gap in gaps.get("gaps", []):
            self.tracker.record_gap(
                inv_id,
                gap.get("description", ""),
                gap.get("suggested_skills", []),
            )

        # 6. Generate conclusion
        conclusion = self._synthesize_conclusion(topic, hypothesis, findings)

        self.tracker.conclude_investigation(inv_id, conclusion)
        self.journal.log_conclusion(
            conclusion=conclusion,
            evidence=[f["skill"] for f in findings],
            confidence="medium",
        )

        return {
            "investigation_id": inv_id,
            "topic": topic,
            "hypothesis": hypothesis,
            "domains": domain_names,
            "steps_completed": len(findings),
            "findings": findings,
            "gaps": gaps.get("gaps", []),
            "conclusion": conclusion,
        }

    def _synthesize_conclusion(
        self, topic: str, hypothesis: Optional[str], findings: List[Dict[str, Any]]
    ) -> str:
        """Use LLM to synthesize findings into a conclusion."""
        findings_str = "\n".join(f"- {f['finding']}" for f in findings)

        client = get_llm_client(self.agent_name)
        prompt = f"""Synthesize these business research findings into a concise conclusion.

Topic: {topic}
{"Hypothesis: " + hypothesis if hypothesis else ""}

Findings:
{findings_str}

Write a 2-3 sentence conclusion summarizing the key insights and strategic implications."""

        return client.call(prompt, max_tokens=300, temperature=0.3)
