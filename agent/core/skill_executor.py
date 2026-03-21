"""
Skill Executor - Universal execution engine for business research skills.

Executes Python scripts, API calls, and package-based tools through a unified
interface, returning standardized JSON results for chaining.
"""

import os
import json
import subprocess
import sys
import importlib
from pathlib import Path
from typing import Optional, Dict, Any, List


class SkillExecutor:
    """Execute business research skills through a unified interface."""

    def __init__(self, root_dir: Optional[str] = None):
        if root_dir:
            self.root_dir = Path(root_dir)
        else:
            self.root_dir = Path(__file__).parent.parent
        self.skills_dir = self.root_dir / "skills"

    def _resolve_executable_path(self, skill_name: str, script_name: str) -> Path:
        """Resolve and validate script path (must be within skills directory)."""
        script_path = (self.skills_dir / skill_name / "scripts" / script_name).resolve()
        skills_resolved = self.skills_dir.resolve()
        if not str(script_path).startswith(str(skills_resolved)):
            raise ValueError(f"Script path {script_path} is outside skills directory")
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        return script_path

    def execute_skill(
        self,
        skill_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        script_name: Optional[str] = None,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        Execute a single skill and return results.

        Args:
            skill_name: Name of the skill to execute
            parameters: Parameters to pass to the skill
            script_name: Specific script to run (default: main.py)
            timeout: Execution timeout in seconds

        Returns:
            Standardized result dict with keys: skill, status, result/error
        """
        params = parameters or {}
        script = script_name or "main.py"

        try:
            script_path = self._resolve_executable_path(skill_name, script)
            return self._execute_script(skill_name, script_path, params, timeout)
        except FileNotFoundError:
            # Try package-based execution
            return self._execute_package(skill_name, params)
        except Exception as e:
            return {"skill": skill_name, "status": "error", "error": str(e)}

    def _execute_script(
        self, skill_name: str, script_path: Path, params: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """Execute a Python script skill."""
        env = os.environ.copy()
        env["SKILL_PARAMS"] = json.dumps(params)
        env["SKILL_NAME"] = skill_name

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )

            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output = {"raw_output": result.stdout.strip()}
                return {"skill": skill_name, "status": "success", "result": output}
            else:
                return {
                    "skill": skill_name,
                    "status": "error",
                    "error": result.stderr.strip() or f"Exit code {result.returncode}",
                }
        except subprocess.TimeoutExpired:
            return {"skill": skill_name, "status": "error", "error": f"Timeout after {timeout}s"}

    def _execute_package(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a package-based skill by importing and calling it."""
        module_name = f"businessclaw.skills.{skill_name.replace('-', '_')}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "run"):
                result = mod.run(**params)
                return {"skill": skill_name, "status": "success", "result": result}
            else:
                return {"skill": skill_name, "status": "error", "error": "No run() function found"}
        except ImportError:
            return {"skill": skill_name, "status": "error", "error": f"Skill '{skill_name}' not found"}

    def execute_skill_chain(
        self, chain: List[Dict[str, Any]], shared_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a sequence of skills, passing results forward.

        Args:
            chain: List of dicts with keys: skill, parameters, script (optional)
            shared_context: Initial context shared across all skills

        Returns:
            List of results from each skill execution
        """
        context = shared_context or {}
        results = []

        for step in chain:
            params = {**context, **(step.get("parameters", {}))}
            result = self.execute_skill(
                skill_name=step["skill"],
                parameters=params,
                script_name=step.get("script"),
            )
            results.append(result)

            # Inject successful results into context for downstream skills
            if result["status"] == "success":
                context[f"{step['skill']}_result"] = result["result"]

        return results


_executor: Optional[SkillExecutor] = None


def get_executor(root_dir: Optional[str] = None) -> SkillExecutor:
    global _executor
    if _executor is None:
        _executor = SkillExecutor(root_dir=root_dir)
    return _executor
