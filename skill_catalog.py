#!/usr/bin/env python3
"""
Skill Catalog CLI - Browse and search BusinessClaw skills.

Usage:
    python -m businessclaw.skill_catalog --stats
    python -m businessclaw.skill_catalog --search "valuation"
    python -m businessclaw.skill_catalog --suggest "Apple competitive strategy"
    python -m businessclaw.skill_catalog --list
"""

import argparse
import json
from .core.skill_registry import get_registry


def main():
    parser = argparse.ArgumentParser(description="BusinessClaw Skill Catalog")
    parser.add_argument("--stats", action="store_true", help="Show registry statistics")
    parser.add_argument("--search", help="Search skills by keyword")
    parser.add_argument("--suggest", help="Suggest skills for a research topic")
    parser.add_argument("--list", action="store_true", help="List all skills")
    parser.add_argument("--category", help="List skills in a category")

    args = parser.parse_args()
    registry = get_registry()

    if args.stats:
        stats = registry.get_stats()
        print(f"Total skills: {stats['total_skills']}")
        print("By category:")
        for cat, count in sorted(stats["by_category"].items()):
            print(f"  {cat}: {count}")

    elif args.search:
        results = registry.search(args.search)
        print(f"Found {len(results)} skills for '{args.search}':")
        for r in results:
            print(f"  [{r.get('category', '?')}] {r['name']}: {r.get('description', '')[:60]}")

    elif args.suggest:
        results = registry.suggest_skills_for_topic(args.suggest)
        print(f"Suggested skills for '{args.suggest}':")
        for r in results[:10]:
            print(f"  [{r.get('category', '?')}] {r['name']} (score: {r['relevance_score']})")

    elif args.list:
        skills = registry.list_all()
        print(f"Registered skills ({len(skills)}):")
        for s in skills:
            print(f"  - {s}")

    elif args.category:
        results = registry.get_by_category(args.category)
        print(f"Skills in '{args.category}' ({len(results)}):")
        for r in results:
            print(f"  - {r['name']}: {r.get('description', '')[:60]}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
