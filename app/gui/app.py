"""Main window (customtkinter).

Left: provider/API key, input files, output folder, limits, actions.
Right: phase progress, usage/cost counter, tabs (Log, Todos, Spec preview, Report).
The agent runs in a worker thread; this window polls the controller's queue every 100 ms.
"""

from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk

from app import APP_NAME, __version__
from app.agent.replay import REPLAY_LABEL
from app.config import AppConfig, load_config, mask_key, save_config
from app.gui.controller import RunController, build_provider, find_default_inputs, launch_generated_game
from app.llm.deepseek import DEEPSEEK_MODEL
from app.llm.pricing import PRICES_PER_M
from app.parsers.spec import build_spec

PHASES = ["plan", "implement", "verify", "fix", "report"]
PHASE_LABELS = {"plan": "1 Plan", "implement": "2 Implement", "verify": "3 Verify", "fix": "4 Fix",
                "report": "5 Report"}
POLL_MS = 100
IDLE, ACTIVE, DONE, FAILED = ("gray85", "gray25"), "#c80", "#2a7", "#a33"
TODO_ICON = {"pending": "○", "in_progress": "◐", "completed": "●"}


class AgentApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("system")
        self.title(f"Space Fractions Code Agent  v{__version__}")
        self.geometry("1280x800")
        self.minsize(1050, 680)
        self.cfg = load_config()
        self.controller = RunController()
        self.vars: dict[str, tk.Variable] = {}
        self._current_phase: str | None = None
        self._build()
        self._load_into_form()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(POLL_MS, self._poll)

    # ------------------------------------------------------------------ layout
    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        column = ctk.CTkFrame(self, fg_color="transparent")
        column.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        column.grid_rowconfigure(0, weight=1)
        column.grid_columnconfigure(0, weight=1)
        left = ctk.CTkScrollableFrame(column, width=390, label_text="Configuration")
        left.grid(row=0, column=0, sticky="nsew")
        actions = ctk.CTkFrame(column)  # always visible, never scrolled away
        actions.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)
        self._build_left(left)
        self._build_actions(actions)
        self._build_right(right)

    def _section(self, parent, text: str) -> None:
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", padx=8, pady=(12, 2))

    def _var(self, name: str, kind=tk.StringVar, value: Any = "") -> tk.Variable:
        self.vars[name] = kind(value=value)
        return self.vars[name]

    def _build_left(self, f) -> None:
        self._section(f, "LLM provider")
        ctk.CTkLabel(f, text=f"Model: {DEEPSEEK_MODEL}  (official DeepSeek API)", anchor="w").pack(fill="x", padx=8)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=2)
        self.key_entry = ctk.CTkEntry(row, textvariable=self._var("api_key"), show="•",
                                      placeholder_text="DeepSeek API key (sk-…)")
        self.key_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="👁", width=34, command=self._toggle_key).pack(side="left", padx=(4, 0))
        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=2)
        ctk.CTkCheckBox(row2, text="Remember key", variable=self._var("remember_key", tk.BooleanVar, False)).pack(
            side="left")
        self.test_btn = ctk.CTkButton(row2, text="Test connection", width=130, command=self._test_connection)
        self.test_btn.pack(side="right")
        self.conn_label = ctk.CTkLabel(f, text="Test connection makes 1 tiny API request (≈ $0.0001).",
                                       anchor="w", text_color="gray", wraplength=360, justify="left")
        self.conn_label.pack(fill="x", padx=8)
        ctk.CTkCheckBox(f, text="Thinking mode (slower, more tokens)",
                        variable=self._var("thinking", tk.BooleanVar, False)).pack(anchor="w", padx=8, pady=2)
        ctk.CTkCheckBox(f, text="Developer: mock mode (no API, scripted demo)",
                        variable=self._var("mock", tk.BooleanVar, False)).pack(anchor="w", padx=8, pady=2)

        self._section(f, "Inputs")
        self._file_row(f, "doc_path", "Architecture_Documentation.md", self._pick_file)
        self._file_row(f, "view_path", "Architecture_View.md", self._pick_file)
        ctk.CTkButton(f, text="Preview spec.json", command=self._preview_spec).pack(fill="x", padx=8, pady=4)

        self._section(f, "Output")
        self._file_row(f, "output_dir", "Output folder", self._pick_dir)

        self._section(f, "Limits & options")
        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x", padx=8)
        fields = [("max_steps", "Max agent steps"), ("max_requests", "Max LLM requests / run"),
                  ("max_cost_usd", "Max cost / run (USD)"), ("fix_rounds", "Auto-fix rounds")]
        for i, (name, label) in enumerate(fields):
            ctk.CTkLabel(grid, text=label, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            ctk.CTkEntry(grid, width=90, textvariable=self._var(name)).grid(row=i, column=1, sticky="e", pady=2)
        grid.grid_columnconfigure(0, weight=1)
        ctk.CTkCheckBox(f, text="Ask before every file write", variable=self._var("ask_before_write", tk.BooleanVar,
                                                                                    False)).pack(anchor="w", padx=8,
                                                                                                 pady=4)

    def _build_actions(self, f) -> None:
        self.generate_btn = ctk.CTkButton(f, text="▶  Generate", height=38, command=self._generate,
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.generate_btn.pack(fill="x", padx=8, pady=(8, 3))
        self.stop_btn = ctk.CTkButton(f, text="■  Stop", fg_color="gray50", hover_color="#822", command=self._stop,
                                      state="disabled")
        self.stop_btn.pack(fill="x", padx=8, pady=3)
        two = ctk.CTkFrame(f, fg_color="transparent")
        two.pack(fill="x", padx=8, pady=3)
        self.resume_btn = ctk.CTkButton(two, text="⟳ Resume run", command=self._resume)
        self.resume_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.replay_btn = ctk.CTkButton(two, text="⏵ Replay recorded run", command=self._replay)
        self.replay_btn.pack(side="left", fill="x", expand=True, padx=(3, 0))
        two2 = ctk.CTkFrame(f, fg_color="transparent")
        two2.pack(fill="x", padx=8, pady=(3, 8))
        ctk.CTkButton(two2, text="📂 Open output folder", command=self._open_output).pack(
            side="left", fill="x", expand=True, padx=(0, 3))
        self.run_game_btn = ctk.CTkButton(two2, text="▶ Run generated game", fg_color="#2a7", hover_color="#185",
                                          command=self._run_game)
        self.run_game_btn.pack(side="left", fill="x", expand=True, padx=(3, 0))

    def _file_row(self, parent, var: str, placeholder: str, picker) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=2)
        entry = ctk.CTkEntry(row, textvariable=self._var(var), placeholder_text=placeholder)
        entry.pack(side="left", fill="x", expand=True)
        # show the end of long paths (the file name), not the drive letter
        self.vars[var].trace_add("write", lambda *_: entry.after_idle(lambda: entry.xview("end")))
        ctk.CTkButton(row, text="…", width=34, command=lambda: picker(var, placeholder)).pack(side="left", padx=(4, 0))

    def _build_right(self, f) -> None:
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.phase_labels: dict[str, ctk.CTkLabel] = {}
        for i, p in enumerate(PHASES):
            lbl = ctk.CTkLabel(top, text=PHASE_LABELS[p], corner_radius=6, fg_color=IDLE, width=110,
                               height=30)
            lbl.grid(row=0, column=i, padx=3, sticky="ew")
            top.grid_columnconfigure(i, weight=1)
            self.phase_labels[p] = lbl
        self.mode_banner = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.mode_banner.grid(row=1, column=0, sticky="ew", padx=8)
        self.usage_label = ctk.CTkLabel(f, text=self._usage_text(), anchor="w", font=ctk.CTkFont(family="Consolas"))

        self.tabs = ctk.CTkTabview(f)
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
        mono = ctk.CTkFont(family="Consolas", size=12)
        self.text: dict[str, ctk.CTkTextbox] = {}
        for name in ("Log", "Todos", "Spec preview", "Report"):
            tab = self.tabs.add(name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            box = ctk.CTkTextbox(tab, font=mono, wrap="word")
            box.grid(row=0, column=0, sticky="nsew")
            box.configure(state="disabled")
            self.text[name] = box
        self.usage_label.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))

    # ------------------------------------------------------------------ form <-> config
    def _load_into_form(self) -> None:
        c = self.cfg
        doc, view = find_default_inputs()
        values = {"api_key": c.api_key, "remember_key": bool(c.api_key), "thinking": c.thinking,
                  "mock": c.provider == "mock", "doc_path": c.doc_path or doc, "view_path": c.view_path or view,
                  "output_dir": c.output_dir or str(Path.home() / "Documents" / "SpaceFractionsGenerated"),
                  "max_steps": c.max_steps, "max_requests": c.max_requests, "max_cost_usd": c.max_cost_usd,
                  "fix_rounds": c.fix_rounds, "ask_before_write": c.ask_before_write}
        for k, v in values.items():
            self.vars[k].set(v)

    def _form_config(self) -> AppConfig:
        v = {k: var.get() for k, var in self.vars.items()}
        try:
            return AppConfig(api_key=v["api_key"].strip(), provider="mock" if v["mock"] else "deepseek",
                             thinking=v["thinking"], max_steps=int(v["max_steps"]),
                             max_requests=int(v["max_requests"]), max_cost_usd=float(v["max_cost_usd"]),
                             fix_rounds=int(v["fix_rounds"]), ask_before_write=v["ask_before_write"],
                             doc_path=v["doc_path"].strip(), view_path=v["view_path"].strip(),
                             output_dir=v["output_dir"].strip())
        except ValueError as exc:
            raise ValueError("Limits must be numbers.") from exc

    def _persist(self, cfg: AppConfig) -> None:
        stored = AppConfig(**{**cfg.__dict__, "api_key": cfg.api_key if self.vars["remember_key"].get() else ""})
        save_config(stored)

    # ------------------------------------------------------------------ actions
    def _toggle_key(self) -> None:
        self.key_entry.configure(show="" if self.key_entry.cget("show") else "•")

    def _pick_file(self, var: str, title: str) -> None:
        path = filedialog.askopenfilename(title=f"Select {title}", filetypes=[("Markdown", "*.md"), ("All", "*.*")])
        if path:
            self.vars[var].set(path)

    def _pick_dir(self, var: str, title: str) -> None:
        path = filedialog.askdirectory(title=f"Select {title}")
        if path:
            self.vars[var].set(path)

    def _test_connection(self) -> None:
        try:
            cfg = self._form_config()
            provider = build_provider(cfg)
        except Exception as exc:
            self.conn_label.configure(text=f"✗ {exc}", text_color="#d55")
            return
        self.conn_label.configure(text=f"Testing {mask_key(cfg.resolved_api_key())} …", text_color="gray")
        self.test_btn.configure(state="disabled")

        def work():
            try:
                msg, color = "✓ " + provider.test_connection(), "#3a3"
            except Exception as exc:
                msg, color = f"✗ {exc}", "#d55"
            self.after(0, lambda: (self.conn_label.configure(text=msg, text_color=color),
                                   self.test_btn.configure(state="normal")))

        threading.Thread(target=work, daemon=True).start()

    def _preview_spec(self) -> None:
        try:
            cfg = self._form_config()
            spec = build_spec(Path(cfg.doc_path), Path(cfg.view_path))
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not build spec.json:\n{exc}")
            return
        summary = {"domain_model": spec["domain_model"], "input_issues": spec["input_issues"],
                   "requirements": spec["requirements"]}
        self._set_text("Spec preview", json.dumps(summary, indent=2, ensure_ascii=False))
        self.tabs.set("Spec preview")

    def _generate(self, resume: bool = False, replay: Path | None = None) -> None:
        try:
            cfg = self._form_config()
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        out = Path(cfg.output_dir) if cfg.output_dir else None
        if not resume and out and out.is_dir() and any(out.iterdir()):
            messagebox.showerror(APP_NAME, "The output folder is not empty.\nChoose an empty (or new) folder for a "
                                           "new run, or press Resume to continue the run saved there.")
            return
        if replay is None and cfg.provider == "deepseek" and not self._confirm_paid_run(cfg):
            return
        self._persist(cfg)
        self._reset_view(replay is not None, cfg.provider == "mock")
        self.controller.start(cfg, resume=resume, replay_transcript=replay)
        self._set_running(True)

    def _confirm_paid_run(self, cfg: AppConfig) -> bool:
        if not cfg.resolved_api_key():
            messagebox.showerror(APP_NAME, "Enter your DeepSeek API key first (or enable mock mode).")
            return False
        p = PRICES_PER_M[DEEPSEEK_MODEL]
        return messagebox.askyesno(APP_NAME, (
            f"This run calls the paid DeepSeek API ({DEEPSEEK_MODEL}).\n\n"
            f"Price per 1M tokens: input ${p['cache_miss']} (cache hit ${p['cache_hit']}), output ${p['output']} "
            f"(2× in peak hours).\nTypical full run: ~$0.10–0.40.\n\n"
            f"Hard limits for this run: ${cfg.max_cost_usd:.2f} and {cfg.max_requests} requests.\n\nStart?"))

    def _resume(self) -> None:
        out = Path(self.vars["output_dir"].get())
        if not (out / "agent_run" / "state.json").exists():
            messagebox.showinfo(APP_NAME, "No saved run state in this output folder.")
            return
        self._generate(resume=True)

    def _replay(self) -> None:
        path = filedialog.askopenfilename(title="Select a recorded transcript.jsonl",
                                          filetypes=[("Transcript", "transcript.jsonl"), ("JSONL", "*.jsonl")])
        if not path:
            return
        self._generate(replay=Path(path))

    def _stop(self) -> None:
        self.controller.stop()
        self._log("Stop requested — finishing the current step…")

    def _open_output(self) -> None:
        out = Path(self.vars["output_dir"].get())
        if out.is_dir():
            os.startfile(out)  # noqa: S606 - Windows desktop app
        else:
            messagebox.showinfo(APP_NAME, "Output folder does not exist yet.")

    def _run_game(self) -> None:
        try:
            launch_generated_game(Path(self.vars["output_dir"].get()))
            self._log("Launched generated game (main.py) with the bundled interpreter.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def _on_close(self) -> None:
        if self.controller.running:
            if not messagebox.askyesno(APP_NAME, "A run is in progress. Stop it and quit? (State is saved.)"):
                return
            self.controller.stop()
            self.controller.thread.join(timeout=5)
        self.destroy()

    # ------------------------------------------------------------------ event handling
    def _poll(self) -> None:
        for kind, data in self.controller.drain():
            self._handle(kind, data)
        self.after(POLL_MS, self._poll)

    def _handle(self, kind: str, d: dict[str, Any]) -> None:
        if kind == "log":
            self._log(d["text"])
        elif kind == "phase":
            self._set_phase(d["phase"])
        elif kind == "tool_call":
            self._log(f"→ {d['summary']}")
        elif kind == "tool_result":
            first = d["preview"].splitlines()[0][:160] if d["preview"] else ""
            self._log(f"   {'✓' if d['ok'] else '✗'} {first}")
        elif kind == "todos":
            self._set_text("Todos", "\n".join(f"{TODO_ICON[t['status']]} {t['content']}" for t in d["todos"]))
        elif kind == "usage":
            self.usage_label.configure(text=self._usage_text(d))
        elif kind == "verify":
            self._log(("✓ VERIFY PASSED\n" if d["ok"] else "✗ VERIFY FAILED\n") + d["report"][-1500:])
        elif kind == "error":
            self._log(f"ERROR: {d['text']}")
            messagebox.showerror(APP_NAME, d["text"])
        elif kind == "approve":
            req = d["request"]
            req.approved = messagebox.askyesno(APP_NAME, f"Allow the agent to write:\n\n{req.path}\n\n"
                                                         f"{req.preview[:600]}")
            req.answered.set()
        elif kind == "done":
            self._finish(d["result"])

    def _finish(self, result: dict[str, Any]) -> None:
        self._set_running(False)
        status = result.get("status")
        self._log(f"=== Run {status}{': ' + result['reason'] if result.get('reason') else ''} ===")
        report = result.get("report_path")
        if report and Path(report).exists():
            self._set_text("Report", Path(report).read_text(encoding="utf-8"))
        if self._current_phase in self.phase_labels:
            self.phase_labels[self._current_phase].configure(fg_color=DONE if status == "completed" else FAILED)
        self._current_phase = None

    # ------------------------------------------------------------------ view helpers
    def _reset_view(self, replay: bool, mock: bool) -> None:
        for name in ("Log", "Todos", "Report"):
            self._set_text(name, "")
        self._current_phase = None
        for lbl in self.phase_labels.values():
            lbl.configure(fg_color=IDLE)
        banner, color = "", None
        if replay:
            banner, color = f"⏵ {REPLAY_LABEL} — no API calls", "#c80"
        elif mock:
            banner, color = "MOCK MODE — scripted demo, no API calls", "#c80"
        self.mode_banner.configure(text=banner, text_color=color)
        self.usage_label.configure(text=self._usage_text())
        self.tabs.set("Log")

    def _set_phase(self, phase: str) -> None:
        """Previous phase turns green, the current one orange."""
        if self._current_phase in self.phase_labels:
            self.phase_labels[self._current_phase].configure(fg_color=DONE)
        self._current_phase = phase
        if phase in self.phase_labels:
            self.phase_labels[phase].configure(fg_color=ACTIVE)

    def _set_running(self, running: bool) -> None:
        for b in (self.generate_btn, self.resume_btn, self.replay_btn, self.test_btn, self.run_game_btn):
            b.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled", fg_color="#a33" if running else "gray50")

    @staticmethod
    def _usage_text(d: dict[str, Any] | None = None) -> str:
        if not d:
            return "requests 0 | tokens 0 (cache hit 0) | cost $0.0000"
        u = d["usage"]
        total = u["prompt_tokens"] + u["completion_tokens"]
        return (f"requests {d['requests']} | tokens {total:,} (prompt {u['prompt_tokens']:,}, cache hit "
                f"{u['cache_hit_tokens']:,}, output {u['completion_tokens']:,}) | cost ${d['cost_usd']:.4f}")

    def _log(self, text: str) -> None:
        box = self.text["Log"]
        box.configure(state="normal")
        box.insert("end", text + "\n")
        box.see("end")
        box.configure(state="disabled")

    def _set_text(self, tab: str, text: str) -> None:
        box = self.text[tab]
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")


def launch() -> int:
    app = AgentApp()
    app.mainloop()
    return 0
