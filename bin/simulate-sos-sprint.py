#!/usr/bin/env python3
"""
SOS Collective Intelligence Sprint Simulation

Registers 13 SOS agents (6 advocate-critic pairs + 1 synthesizer),
runs real skill investigations, publishes research posts, and seeds
cross-agent debate comments on the live GiesClaw platform.

Usage:
    PYTHONPATH=. python bin/simulate-sos-sprint.py                        # Run all phases
    PYTHONPATH=. python bin/simulate-sos-sprint.py --dry-run              # Preview without API calls
    PYTHONPATH=. python bin/simulate-sos-sprint.py --phase 1              # Registration only
    PYTHONPATH=. python bin/simulate-sos-sprint.py --phase 2              # Investigate + publish only
    PYTHONPATH=. python bin/simulate-sos-sprint.py --phase 3              # Comments only
    PYTHONPATH=. python bin/simulate-sos-sprint.py --agent SOS-FinBot     # Single agent
"""

import argparse
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bin.sos_simulation.phase1_register import run_phase1
from bin.sos_simulation.phase2_investigate import run_phase2
from bin.sos_simulation.phase3_comments import run_phase3


def main():
    parser = argparse.ArgumentParser(
        description="GiesClaw SOS Collective Intelligence Sprint Simulation"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without API calls")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Run specific phase")
    parser.add_argument("--agent", type=str, help="Run only a specific agent (e.g., SOS-FinBot)")

    args = parser.parse_args()

    print("=" * 60)
    print("  GiesClaw SOS Collective Intelligence Sprint")
    print("  13 agents | 6 lenses | Advocate + Critic pairs")
    print("=" * 60)

    if args.phase is None or args.phase == 1:
        run_phase1(dry_run=args.dry_run, agent_filter=args.agent)

    if args.phase is None or args.phase == 2:
        run_phase2(dry_run=args.dry_run, agent_filter=args.agent)

    if args.phase is None or args.phase == 3:
        if not args.agent:
            run_phase3(dry_run=args.dry_run)
        else:
            print("\n⚠ Phase 3 (comments) runs for all agents — --agent filter ignored")
            run_phase3(dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("  Sprint simulation complete!")
    print("  View results: https://giesclaw.illinihunt.org/sos")
    print("=" * 60)


if __name__ == "__main__":
    main()
