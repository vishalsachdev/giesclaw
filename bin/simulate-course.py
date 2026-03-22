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
        run_phase3(dry_run=args.dry_run)
    elif 3 in phases and args.student:
        print("\n  ⚠ Phase 3 (comments) skipped — comments are cross-student, not per-student")

    print("\n" + "=" * 60)
    print("  Simulation complete!")
    print("  View results: https://giesclaw.illinihunt.org")
    print("=" * 60)


if __name__ == "__main__":
    main()
