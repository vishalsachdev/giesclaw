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
        if name in creds and "jwt" in creds[name]:
            print(f"  ⏭ {name} already has credentials (skipping)")
            continue

        result = register_student(student, dry_run=dry_run)
        if result:
            creds[name] = result
            save_credentials(creds)

        time.sleep(1)

    registered = sum(1 for v in creds.values() if "jwt" in v)
    print(f"\n✓ Phase 1 complete: {registered}/{len(STUDENTS)} students registered")
    return creds
