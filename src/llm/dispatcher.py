import subprocess
import json
import logging
import os
import re
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from llm.core.types import ToolCall
from llm.session_recorder import SessionRecorder

logging.basicConfig(level=logging.INFO, format='%(asctime)s [Dispatcher] %(message)s')
logger = logging.getLogger("dispatcher")

@dataclass
class HookResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_veto: bool = False

@dataclass
class DispatchResult:
    tool_call: Optional[ToolCall] = None
    hook_outputs: Dict[str, Any] = field(default_factory=dict)
    vetoed: bool = False
    error: Optional[str] = None

def format_osc8(text: str, uri: str) -> str:
    """Format a string as an OSC-8 terminal hyperlink."""
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return f"{text} ({uri})"
    return f"\x1b]8;;{uri}\x1b\\{text}\x1b]8;;\x1b\\"


class Dispatcher:
    """
    Hook Mesh Dispatcher.
    Reads hooks/hooks.json and orchestrates the execution of hook chains
    based on events and matchers.
    """

    def __init__(self, recorder: SessionRecorder):
        self.recorder = recorder
        self.project_root = os.environ.get("PROJECT_ROOT", os.getcwd())
        self.hooks_config = self._load_hooks_config()

    def _load_hooks_config(self) -> Dict[str, Any]:
        hooks_json_path = os.path.join(self.project_root, "hooks", "hooks.json")
        if not os.path.exists(hooks_json_path):
            logger.warning(f"hooks.json not found at {hooks_json_path}")
            return {"hooks": {}}

        try:
            with open(hooks_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load hooks.json: {e}")
            return {"hooks": {}}

    def _match(self, matcher: str, tool_name: str) -> bool:
        if matcher == "*":
            return True

        parts = matcher.split('|')
        return tool_name in parts

    def dispatch(self, event_type: str, tool_call: Optional[ToolCall] = None, session_id: Optional[str] = None, extra_payload: Optional[Dict[str, Any]] = None) -> DispatchResult:
        """
        Dispatch an event to the hook mesh.
        Returns a DispatchResult containing the (possibly mutated) ToolCall,
        hook-specific outputs, and veto status.
        """
        tool_name = tool_call.name if tool_call else "*"
        
        trace_id = f"{session_id or 'default'}-{event_type}-{tool_name}-{os.getpid()}"
        trace_uri = f"egc://trace/{trace_id}"
        
        logger.info(f"Evento: {event_type} | Alvo: {tool_name} | Trace: {format_osc8(trace_id, trace_uri)}")
        
        relevant_hooks = self.hooks_config.get("hooks", {}).get(event_type, [])
        
        current_tool_call = tool_call
        cumulative_hook_outputs = {}

        for entry in relevant_hooks:
            matcher = entry.get("matcher", "*")
            if self._match(matcher, tool_name):
                for hook_def in entry.get("hooks", []):
                    payload = {
                        "event": event_type,
                        "tool": tool_name,
                        "tool_name": tool_name, # Mirroring for Node parity
                        "params": current_tool_call.arguments if current_tool_call else {},
                        "tool_input": current_tool_call.arguments if current_tool_call else {}, # Mirroring for Node parity
                        "context": {
                            "session_id": session_id or "default",
                            "runtime_source": "egc-python-dispatcher"
                        }
                    }

                    if extra_payload:
                        payload.update(extra_payload)
                        if "transcript_path" in extra_payload:
                            payload["transcript_path"] = extra_payload["transcript_path"]

                    result = self._execute_hook_command(hook_def.get("command"), payload, session_id)

                    if not result.success:
                        logger.warning(f"Hook {entry.get('id', 'unnamed')} vetoed or failed: {result.error}")
                        self.recorder.record("veto", {"event": event_type, "tool": tool_name, "reason": result.error})
                        return DispatchResult(vetoed=True, error=result.error)

                    if result.data and isinstance(result.data, dict):
                        hook_out = result.data.get("hookSpecificOutput")
                        if hook_out and isinstance(hook_out, dict):
                            cumulative_hook_outputs.update(hook_out)

                    if result.data and current_tool_call:
                        validated = self._validate_and_reconstruct(result.data, current_tool_call)
                        if validated:
                            if validated.arguments != current_tool_call.arguments:
                                self.recorder.record("mutation", {"original": current_tool_call.arguments, "mutated": validated.arguments})
                                logger.info(f"Mutation applied by hook {entry.get('id', 'unnamed')}")
                            current_tool_call = validated

        return DispatchResult(tool_call=current_tool_call, hook_outputs=cumulative_hook_outputs)

    def _execute_hook_command(self, command: str, payload: Dict[str, Any], session_id: Optional[str]) -> HookResult:
        if not command or not isinstance(command, str):
            return HookResult(success=True)

        try:
            env = os.environ.copy()
            env["PROJECT_ROOT"] = self.project_root

            raw_sid = session_id or env.get("EGC_SESSION_ID") or env.get("ECC_SESSION_ID") or "default"
            sid = re.sub(r"[^A-Za-z0-9._-]", "_", str(raw_sid)) or "default"
            env["SESSION_ID"] = sid
            env["EGC_SESSION_ID"] = sid
            env["ECC_SESSION_ID"] = sid

            if "EGC_PLUGIN_ROOT" not in env:
                env["EGC_PLUGIN_ROOT"] = self.project_root
            if "GEMINI_PLUGIN_ROOT" not in env:
                env["GEMINI_PLUGIN_ROOT"] = self.project_root

            try:
                timeout_s = int(env.get("EGC_HOOK_TIMEOUT_SECONDS") or env.get("ECC_HOOK_TIMEOUT_SECONDS") or "30")
                if timeout_s <= 0:
                    timeout_s = 30
            except (TypeError, ValueError):
                timeout_s = 30

            process = subprocess.run(
                command,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=env,
                shell=True,
                cwd=self.project_root
            )

            if process.returncode != 0:
                return HookResult(success=False, error=f"Exit code {process.returncode}: {process.stderr}")

            try:
                data = json.loads(process.stdout) if process.stdout.strip() else None
                return HookResult(success=True, data=data)
            except json.JSONDecodeError:
                return HookResult(success=True)

        except subprocess.TimeoutExpired:
            return HookResult(success=False, error="Timeout reached", is_veto=True)
        except Exception as e:
            return HookResult(success=False, error=str(e))

    def _validate_and_reconstruct(self, data: Dict[str, Any], original: ToolCall) -> Optional[ToolCall]:
        if not isinstance(data, dict):
            return original

        params = data.get("params")
        if params is None or not isinstance(params, dict):
            return original

        return ToolCall(
            id=original.id,
            name=data.get("tool", original.name),
            arguments=params
        )
