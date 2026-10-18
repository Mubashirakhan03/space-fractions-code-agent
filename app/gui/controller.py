"""UI-independent run controller: builds provider + agent, runs it in a worker thread, and hands
events to the UI through a queue (the Tk main loop polls it, so the window never freezes).
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.agent.loop import Agent
from app.agent.replay import ReplayProvider
from app.config import AppConfig
from app.llm.deepseek import DeepSeekProvider
from app.llm.demo_script import demo_provider
from app.llm.provider import LLMError, LLMProvider
from app.parsers.spec import build_spec
from app.tools.runner import base_command, clean_env

DOC_NAME = "Architecture_Documentation.md"
VIEW_NAME = "Architecture_View.md"


def build_provider(cfg: AppConfig, replay_transcript: Path | None = None) -> LLMProvider:
    if replay_transcript:
        return ReplayProvider(replay_transcript)
    if cfg.provider == "mock":
        return demo_provider()
    key = cfg.resolved_api_key()
    if not key:
        raise LLMError("No DeepSeek API key: enter it in the GUI or set DEEPSEEK_API_KEY.")
    return DeepSeekProvider(key, thinking=cfg.thinking)


def find_default_inputs(extra_dirs: list[Path] | None = None) -> tuple[str, str]:
    """Pre-fill the two input files if they sit next to the exe, in samples/, or in the cwd."""
    exe_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else None
    app_root = Path(__file__).resolve().parent.parent.parent
    candidates = [*(extra_dirs or []), *(d for d in (exe_dir, exe_dir and exe_dir / "samples") if d),
                  Path.cwd(), Path.cwd() / "samples", app_root / "samples"]
    for d in candidates:
        if (d / DOC_NAME).is_file() and (d / VIEW_NAME).is_file():
            return str(d / DOC_NAME), str(d / VIEW_NAME)
    return "", ""


@dataclass
class ApprovalRequest:
    path: str
    preview: str
    answered: threading.Event = field(default_factory=threading.Event)
    approved: bool = False


class RunController:
    def __init__(self) -> None:
        self.events: queue.Queue[tuple[str, dict[str, Any]]] = queue.Queue()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.agent: Agent | None = None

    @property
    def running(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def _emit(self, kind: str, data: dict[str, Any]) -> None:
        self.events.put((kind, data))

    def start(self, cfg: AppConfig, *, resume: bool = False, replay_transcript: Path | None = None,
              provider: LLMProvider | None = None, approval_timeout: float = 600) -> None:
        if self.running:
            raise RuntimeError("A run is already in progress.")
        self.stop_event = threading.Event()

        def approve(path: str, preview: str) -> bool:
            req = ApprovalRequest(path, preview)
            self._emit("approve", {"request": req})
            req.answered.wait(timeout=approval_timeout)
            return req.approved

        def work() -> None:
            try:
                prov = provider or build_provider(cfg, replay_transcript)
                spec = self._load_spec(cfg, replay_transcript)
                self.agent = Agent(prov, cfg, cfg.output_dir, spec, on_event=self._emit,
                                   approve_write=approve if cfg.ask_before_write else None,
                                   stop_event=self.stop_event)
                self._emit("log", {"text": f"Provider: {prov.name} | model: {prov.model}"})
                self.agent.run(resume=resume)
            except Exception as exc:  # surface everything to the UI instead of dying silently
                self._emit("error", {"text": f"{type(exc).__name__}: {exc}"})
                self._emit("done", {"result": {"status": "error", "reason": str(exc)}})

        self.thread = threading.Thread(target=work, name="agent-run", daemon=True)
        self.thread.start()

    @staticmethod
    def _load_spec(cfg: AppConfig, replay_transcript: Path | None) -> dict[str, Any]:
        if replay_transcript:  # replay must use the exact spec of the recorded run
            recorded = Path(replay_transcript).parent / "spec.json"
            if recorded.exists():
                return json.loads(recorded.read_text(encoding="utf-8"))
        if not (cfg.doc_path and cfg.view_path):
            raise ValueError("Select both input files first.")
        if not cfg.output_dir:
            raise ValueError("Select an output folder first.")
        return build_spec(Path(cfg.doc_path), Path(cfg.view_path))

    def stop(self) -> None:
        self.stop_event.set()

    def drain(self, limit: int = 200) -> list[tuple[str, dict[str, Any]]]:
        out = []
        while len(out) < limit:
            try:
                out.append(self.events.get_nowait())
            except queue.Empty:
                break
        return out


def launch_generated_game(output_dir: Path) -> subprocess.Popen:
    """Start the generated main.py with the bundled interpreter (no Python needed on the PC)."""
    main_py = Path(output_dir) / "main.py"
    if not main_py.is_file():
        raise FileNotFoundError(f"No main.py in {output_dir}")
    return subprocess.Popen([*base_command(), "--run-script", "main.py"], cwd=output_dir, env=clean_env(),
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
