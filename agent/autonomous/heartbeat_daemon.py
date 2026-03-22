"""
Heartbeat Daemon - Continuous autonomous business research.

Runs the agent's investigation loop at regular intervals (default: 6 hours).
Each cycle: observe -> detect gaps -> hypothesize -> investigate -> publish.
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class HeartbeatDaemon:
    """Continuous autonomous research daemon for business agents."""

    def __init__(self, profile_name: str = "default", interval_hours: float = 6.0):
        self.profile_name = profile_name
        self.interval_seconds = int(interval_hours * 3600)
        self.base_dir = Path.home() / ".giesclaw"
        self.state_path = self.base_dir / "heartbeat_state.json"
        self.log_path = self.base_dir / "heartbeat_daemon.log"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_heartbeat": None, "cycle_count": 0, "last_error": None}

    def _save_state(self, state: Dict[str, Any]):
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    def _log(self, message: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"[{timestamp}] {message}\n"
        print(line.strip())
        with open(self.log_path, "a") as f:
            f.write(line)

    def _load_profile(self) -> Optional[Dict[str, Any]]:
        profile_path = self.base_dir / "profiles" / f"{self.profile_name}.json"
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"Error loading profile: {e}")
        return None

    def _is_heartbeat_due(self, state: Dict[str, Any]) -> bool:
        last = state.get("last_heartbeat")
        if last is None:
            return True
        try:
            last_dt = datetime.fromisoformat(last)
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
            return elapsed >= self.interval_seconds
        except Exception:
            return True

    def run_single_cycle(self) -> Dict[str, Any]:
        """Run a single heartbeat cycle."""
        self._log(f"Starting heartbeat cycle (profile: {self.profile_name})")

        profile = self._load_profile()
        if not profile:
            self._log("No profile found. Run setup first.")
            return {"error": "No profile configured"}

        agent_name = profile.get("agent_name", "BusinessAgent")

        try:
            from ..reasoning.investigation_engine import InvestigationEngine

            engine = InvestigationEngine(agent_name, profile)

            # Determine research topic from profile interests
            interests = profile.get("research_interests", [])
            if interests:
                topic = interests[0]
            else:
                topic = "Current market trends and investment opportunities"

            result = engine.investigate(topic=topic, max_steps=3)

            self._log(
                f"Cycle complete: {result.get('steps_completed', 0)} steps, "
                f"topic: {result.get('topic', 'unknown')}"
            )
            return result

        except Exception as e:
            self._log(f"Cycle error: {e}")
            return {"error": str(e)}

    def run_daemon(self):
        """Run the continuous daemon loop."""
        self._log(f"Starting GiesClaw heartbeat daemon (interval: {self.interval_seconds}s)")

        try:
            while True:
                state = self._load_state()

                if self._is_heartbeat_due(state):
                    result = self.run_single_cycle()
                    state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
                    state["cycle_count"] = state.get("cycle_count", 0) + 1

                    if "error" in result:
                        state["last_error"] = result["error"]
                    else:
                        state["last_error"] = None

                    self._save_state(state)

                # Check interval: 10% of heartbeat interval, capped 10-600s
                check_interval = max(10, min(600, self.interval_seconds // 10))
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self._log("Daemon stopped by user")


def main():
    parser = argparse.ArgumentParser(description="GiesClaw Heartbeat Daemon")
    parser.add_argument("mode", choices=["once", "background", "status"],
                        help="Run mode: once (single cycle), background (daemon), status")
    parser.add_argument("--profile", default="default", help="Agent profile name")
    parser.add_argument("--interval", type=float, default=6.0, help="Heartbeat interval in hours")

    args = parser.parse_args()
    daemon = HeartbeatDaemon(profile_name=args.profile, interval_hours=args.interval)

    if args.mode == "once":
        result = daemon.run_single_cycle()
        print(json.dumps(result, indent=2, default=str))
    elif args.mode == "background":
        daemon.run_daemon()
    elif args.mode == "status":
        state = daemon._load_state()
        print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
