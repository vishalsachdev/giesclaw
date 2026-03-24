"""Phase 1: Register SOS agents on the platform."""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

from .roster import AGENTS, CAPABILITY_PROOF

BASE_URL = "https://giesclaw.illinihunt.org"
CREDS_DIR = Path.home() / ".giesclaw" / "sos_simulation"
CREDS_FILE = CREDS_DIR / "credentials.json"


def load_credentials() -> Dict[str, Any]:
    if CREDS_FILE.exists():
        with open(CREDS_FILE) as f:
            return json.load(f)
    return {}


def save_credentials(creds: Dict[str, Any]):
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)


def register_agent(agent: Dict[str, Any], dry_run: bool = False) -> Optional[Dict[str, Any]]:
    name = agent["agent_name"]
    bio = f"{name} is a {agent['role']} analyst at Gies College of Business. {agent['personality'][:200]}"
    if len(bio) < 50:
        bio += " " * (50 - len(bio))

    payload = {
        "name": name,
        "bio": bio,
        "capabilities": list(set(s["skill"] for s in agent["skills"])),
        "capabilityProof": CAPABILITY_PROOF,
    }

    if dry_run:
        print(f"  [DRY RUN] Would register {name} with {len(agent['skills'])} capabilities")
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
            print(f"  ✗ {name} registration failed: {e}")
            return None

    if resp.status_code == 201:
        data = resp.json()
        print(f"  ✓ Registered {name} (id: {data['agent']['id'][:8]}...)")
        return {"jwt": data["token"], "apiKey": data["apiKey"], "agentId": data["agent"]["id"]}
    elif resp.status_code == 409:
        print(f"  ⚠ {name} already exists — attempting login")
        # Try to login with existing apiKey from creds
        return None
    else:
        print(f"  ✗ Failed to register {name}: {resp.status_code} {resp.text[:200]}")
        return None


def run_phase1(dry_run: bool = False, agent_filter: Optional[str] = None):
    print("\n=== Phase 1: Register SOS Agents ===\n")
    creds = load_credentials()

    agents = AGENTS
    if agent_filter:
        agents = [a for a in AGENTS if a["agent_name"] == agent_filter]
        if not agents:
            print(f"No agent found with name: {agent_filter}")
            return creds

    for agent in agents:
        name = agent["agent_name"]
        if name in creds and "jwt" in creds[name]:
            print(f"  ⏭ {name} already has credentials (skipping)")
            continue

        result = register_agent(agent, dry_run=dry_run)
        if result:
            creds[name] = result
            save_credentials(creds)

        time.sleep(1)

    registered = sum(1 for v in creds.values() if "jwt" in v)
    print(f"\n✓ Phase 1 complete: {registered}/{len(AGENTS)} agents registered")
    return creds
