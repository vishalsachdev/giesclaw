"""
Memory CLI - Command-line interface for managing agent memory.

Usage:
    python -m businessclaw.memory.tools.cli journal search "AAPL"
    python -m businessclaw.memory.tools.cli journal stats
    python -m businessclaw.memory.tools.cli investigations list
    python -m businessclaw.memory.tools.cli knowledge search "Apple"
"""

import argparse
import json
import sys

from ..journal import AgentJournal
from ..investigation_tracker import InvestigationTracker
from ..knowledge_graph import KnowledgeGraph


def main():
    parser = argparse.ArgumentParser(description="BusinessClaw Memory CLI")
    parser.add_argument("--agent", default="Agent", help="Agent name")

    subparsers = parser.add_subparsers(dest="command")

    # Journal commands
    journal_parser = subparsers.add_parser("journal", help="Journal operations")
    journal_sub = journal_parser.add_subparsers(dest="journal_cmd")

    search_parser = journal_sub.add_parser("search", help="Search journal")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", help="Entry type filter")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    journal_sub.add_parser("stats", help="Journal statistics")
    journal_sub.add_parser("topics", help="List investigated topics")

    export_parser = journal_sub.add_parser("export", help="Export journal")
    export_parser.add_argument("--output", help="Output file path")

    # Investigation commands
    inv_parser = subparsers.add_parser("investigations", help="Investigation operations")
    inv_sub = inv_parser.add_subparsers(dest="inv_cmd")
    inv_sub.add_parser("list", help="List investigations")
    inv_sub.add_parser("gaps", help="Show unresolved gaps")
    inv_sub.add_parser("stats", help="Investigation statistics")

    # Knowledge graph commands
    kg_parser = subparsers.add_parser("knowledge", help="Knowledge graph operations")
    kg_sub = kg_parser.add_subparsers(dest="kg_cmd")
    kg_search = kg_sub.add_parser("search", help="Search entities")
    kg_search.add_argument("query", help="Search query")
    kg_sub.add_parser("stats", help="Knowledge graph statistics")

    args = parser.parse_args()

    if args.command == "journal":
        journal = AgentJournal(args.agent)
        if args.journal_cmd == "search":
            types = [args.type] if args.type else None
            results = journal.search(args.query, entry_types=types, limit=args.limit)
            print(json.dumps(results, indent=2))
        elif args.journal_cmd == "stats":
            print(json.dumps(journal.get_stats(), indent=2))
        elif args.journal_cmd == "topics":
            topics = sorted(journal.get_investigated_topics())
            for t in topics:
                print(f"  - {t}")
        elif args.journal_cmd == "export":
            path = journal.export_to_json(args.output)
            print(f"Exported to: {path}")

    elif args.command == "investigations":
        tracker = InvestigationTracker(args.agent)
        if args.inv_cmd == "list":
            for inv in tracker.get_active_investigations():
                print(f"  [{inv['id']}] {inv['topic']} ({len(inv['completed_skills'])} skills)")
        elif args.inv_cmd == "gaps":
            for gap in tracker.get_all_gaps():
                print(f"  [{gap['investigation_id']}] {gap['description']}")
        elif args.inv_cmd == "stats":
            print(json.dumps(tracker.get_stats(), indent=2))

    elif args.command == "knowledge":
        kg = KnowledgeGraph(args.agent)
        if args.kg_cmd == "search":
            results = kg.search_entities(args.query)
            print(json.dumps(results, indent=2))
        elif args.kg_cmd == "stats":
            print(json.dumps(kg.get_stats(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
