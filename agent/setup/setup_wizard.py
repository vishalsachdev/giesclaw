"""
Setup Wizard - Interactive agent configuration for GiesClaw.

Guides users through creating a business research agent profile with
role selection, skill configuration, and research interest definition.
"""

import json
import os
import sys
import argparse
import random
from pathlib import Path
from typing import Dict, Any, Optional

from ..coordination.role_manager import AGENT_ROLES


# Business school research areas for random selection
RESEARCH_AREAS = [
    "Tech sector valuation and AI impact on revenue multiples",
    "ESG investing and sustainable finance performance",
    "Private equity roll-up strategies in fragmented industries",
    "Direct-to-consumer brand disruption in retail",
    "Central bank digital currencies and monetary policy",
    "Platform economics and network effects in two-sided markets",
    "Supply chain resilience post-pandemic",
    "Subscription business model economics",
    "Venture capital deal flow and unicorn creation patterns",
    "Emerging market consumer behavior and middle-class growth",
]


def run_setup(quick: bool = False, profile: Optional[str] = None,
              name: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the agent setup wizard.

    Args:
        quick: Skip interactive prompts, use defaults
        profile: Preset profile (finance, strategy, marketing, operations, economics, entrepreneurship)
        name: Agent name

    Returns:
        Agent configuration dict
    """
    base_dir = Path.home() / ".giesclaw"
    profiles_dir = base_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    if quick:
        config = _quick_setup(profile, name)
    else:
        config = _interactive_setup()

    # Save profile
    profile_name = config.get("profile_name", "default")
    profile_path = profiles_dir / f"{profile_name}.json"
    with open(profile_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nAgent profile saved to: {profile_path}")
    print(f"Agent: {config['agent_name']}")
    print(f"Role: {config['role']}")
    print(f"Skills: {', '.join(config['skills'][:5])}...")

    return config


def _quick_setup(profile: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
    """Generate a profile with sensible defaults."""
    role_map = {
        "finance": "finance_analyst",
        "strategy": "strategy_consultant",
        "marketing": "marketing_researcher",
        "operations": "operations_analyst",
        "economics": "economist",
        "entrepreneurship": "entrepreneur",
    }

    role_name = role_map.get(profile, random.choice(list(AGENT_ROLES.keys())))
    role = AGENT_ROLES[role_name]

    if not name:
        dept = role["department"]
        name = f"{dept}Agent-{random.randint(1, 999)}"

    return {
        "profile_name": name.lower().replace(" ", "-"),
        "agent_name": name,
        "role": role_name,
        "department": role["department"],
        "skills": role["core_skills"],
        "frameworks": role["frameworks"],
        "research_interests": random.sample(RESEARCH_AREAS, min(3, len(RESEARCH_AREAS))),
        "personality": role["personality"],
        "llm_backend": os.environ.get("LLM_BACKEND", "openai"),
    }


def _interactive_setup() -> Dict[str, Any]:
    """Run interactive setup wizard."""
    print("=" * 60)
    print("  GiesClaw - Agent Setup Wizard")
    print("  Autonomous Business Research Framework")
    print("=" * 60)
    print()

    # Agent name
    name = input("Agent name [BusinessAgent]: ").strip() or "BusinessAgent"

    # Role selection
    print("\nAvailable roles:")
    role_names = list(AGENT_ROLES.keys())
    for i, (rname, rinfo) in enumerate(AGENT_ROLES.items(), 1):
        print(f"  {i}. {rname} - {rinfo['description']}")

    try:
        choice = int(input(f"\nSelect role [1-{len(role_names)}]: ").strip() or "1")
        role_name = role_names[choice - 1]
    except (ValueError, IndexError):
        role_name = "strategy_consultant"

    role = AGENT_ROLES[role_name]

    # Research interests
    print(f"\nSuggested research areas for {role['department']}:")
    for i, area in enumerate(RESEARCH_AREAS[:5], 1):
        print(f"  {i}. {area}")

    interests_input = input("\nEnter research interests (comma-separated, or press Enter for defaults): ").strip()
    if interests_input:
        interests = [i.strip() for i in interests_input.split(",")]
    else:
        interests = random.sample(RESEARCH_AREAS, 3)

    # LLM backend
    backend = input("\nLLM backend (openai/anthropic) [openai]: ").strip() or "openai"

    config = {
        "profile_name": name.lower().replace(" ", "-"),
        "agent_name": name,
        "role": role_name,
        "department": role["department"],
        "skills": role["core_skills"],
        "frameworks": role["frameworks"],
        "research_interests": interests,
        "personality": role["personality"],
        "llm_backend": backend,
    }

    print(f"\nProfile configured for {name} ({role_name})")
    return config


def main():
    parser = argparse.ArgumentParser(description="GiesClaw Agent Setup")
    parser.add_argument("--quick", action="store_true", help="Quick setup with defaults")
    parser.add_argument("--profile", choices=["finance", "strategy", "marketing",
                                                "operations", "economics", "entrepreneurship"],
                        help="Preset profile")
    parser.add_argument("--name", help="Agent name")

    args = parser.parse_args()
    run_setup(quick=args.quick, profile=args.profile, name=args.name)


if __name__ == "__main__":
    main()
