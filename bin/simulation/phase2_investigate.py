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

        if name not in creds or "jwt" not in creds[name]:
            print(f"  ⚠ {name} has no credentials — run Phase 1 first")
            continue

        if creds[name].get("postId"):
            print(f"  ⏭ {name} already has a post (skipping)")
            continue

        print(f"\n  [{name}] {student['sub_topic'][:60]}...")

        findings = run_skills(student, dry_run=dry_run)

        if not findings and not dry_run:
            print(f"  ⚠ {name} produced no findings — skipping")
            continue

        if dry_run:
            conclusion = "Simulated conclusion"
        else:
            print(f"    Synthesizing conclusion...")
            conclusion = synthesize_conclusion(student, findings)

        investigation = {
            "investigation_id": str(uuid.uuid4()),
            "topic": student["sub_topic"],
            "hypothesis": f"Investigating: {student['sub_topic']}",
            "findings": findings,
            "conclusion": conclusion,
        }

        if dry_run:
            post = {"title": f"Research: {student['sub_topic']}", "body": "Simulated content"}
        else:
            print(f"    Generating {student['style']} post...")
            generator = PostGenerator(agent_name=name)
            post = generator.generate_post(investigation, style=student["style"])

        post_id = publish_post(student, post, creds[name]["jwt"], dry_run=dry_run)
        if post_id:
            creds[name]["postId"] = post_id
            save_credentials(creds)

        if not dry_run:
            time.sleep(3)

    posted = sum(1 for v in creds.values() if v.get("postId"))
    print(f"\n✓ Phase 2 complete: {posted}/{len(STUDENTS)} posts published")
    return creds
