#!/usr/bin/env python3
"""DELTA-X adapter: OpenAI (GPT / ChatGPT family) models, via the Responses API.

Peer of ``adapters/claude_code.sh``. Drives one model through one task and
leaves a submission a grader can audit.

    python3 openai_agent.py --prompt-file P --workdir W --mode tools|notools \
        --timeout-seconds N --session-file S --out-json O [--model M] \
        [--max-turns 120]
    python3 openai_agent.py --self-test        # offline; no API key, no network

Contract
  --prompt-file     the whole task prompt (UTF-8, may be tens of KB).
  --workdir         the agent's cwd. Every command and every file write happens
                    inside it; anything reaching outside by absolute path or
                    ``..`` is refused and the refusal is shown to the model and
                    written to the transcript. Never silently rewritten.
  --mode tools      the model gets run_bash + write_file.
  --mode notools    no shell and no network -- but write_file IS granted, so
                    the artifacts DX01/DX02/DX02B require land as real files.
                    This matches claude_code.sh, which grants Write in notools
                    for the same reason, and it is what the adapter contract
                    specifies. Set DELTAX_NOTOOLS_NO_WRITE=1 for the stricter
                    reading -- but then s1/s2/s2b deliver nothing, DX01 cannot
                    be scored, and the run is not comparable to the Claude arm.
  --timeout-seconds hard wall-clock budget for this task. On expiry the loop
                    stops cleanly, everything already on disk stands, and the
                    result says "timed_out": true. It is never an exception.
  --session-file    conversation continuity ACROSS tasks. Loaded on start,
                    rewritten on exit; JSON {"model":..., "items":[...]}.
  --out-json        result record. The only thing on stdout is a one-line
                    summary; the detail goes to transcript.jsonl next to it
                    (append mode, so the six stages of a run accumulate).

Exit codes: 0 when the task completed or timed out gracefully; 2 on a
configuration error (no API key, unreadable prompt, SDK missing); 1 only when a
terminal API error produced no useful work at all.

API surface: the Responses API (client.responses.create). It is the surface
OpenAI documents for tool-using agents, it round-trips reasoning items between
turns for reasoning models, and its output items can be fed straight back as
input, which is what makes the cross-task session file a plain list of items.

Dependencies: Python 3.9+, stdlib, and the official ``openai`` SDK. The SDK is
imported lazily so --help and --self-test work without it installed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shlex
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Fallback only. A published measurement MUST pin the model id explicitly
# (--model, or DELTAX_OPENAI_MODEL) -- an unpinned default silently changes
# under you and the number stops being comparable to the run before it.
DEFAULT_MODEL = "gpt-5.1"

MAX_TOOL_OUTPUT_CHARS = 30_000
DEFAULT_MAX_TURNS = 120
DEFAULT_BASH_TIMEOUT_S = 300
MAX_API_ATTEMPTS = 6
BACKOFF_BASE_S = 2.0
BACKOFF_CAP_S = 60.0

# Absolute prefixes a command may name although they sit outside the working
# directory: interpreters, libraries and the usual pseudo-files. Without this
# `/usr/bin/python3 script.py` would be refused. It is an allowlist for reading
# the system, not an escape hatch for the run's own data.
SYSTEM_ROOTS = ("/usr/", "/bin/", "/sbin/", "/lib/", "/lib64/", "/opt/", "/etc/",
                "/proc/", "/sys/", "/dev/null", "/dev/stdin", "/dev/stdout", "/dev/stderr")


class BudgetExhausted(Exception):
    """The wall-clock budget ran out; unwind the loop, do not fail the run."""


def _iso(ts=None):
    return _dt.datetime.utcfromtimestamp(ts if ts is not None else time.time()).strftime("%Y-%m-%dT%H:%M:%SZ")


def _truncate(s, cap=MAX_TOOL_OUTPUT_CHARS):
    if s is None:
        return ""
    if isinstance(s, bytes):
        s = s.decode("utf-8", "replace")
    if not isinstance(s, str):
        s = str(s)
    if len(s) <= cap:
        return s
    return s[:cap] + "\n[truncated %d chars]" % (len(s) - cap)


def _to_plain(obj):
    """Pydantic model / namespace / dict -> JSON-safe plain data."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    for meth in ("model_dump", "dict"):
        fn = getattr(obj, meth, None)
        if callable(fn):
            try:
                return _to_plain(fn())
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        return {k: _to_plain(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return str(obj)


class Transcript:
    """One JSON object per line: every request, tool call and tool result."""

    def __init__(self, path):
        self.path = Path(path)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def log(self, event, **fields):
        rec = {"ts": time.time(), "iso": _iso(), "event": event}
        rec.update(fields)
        try:  # logging must never be what kills a run
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass


# workdir containment

def _inside(workdir, candidate):
    try:
        c = Path(candidate).resolve(strict=False)
        w = Path(workdir).resolve(strict=False)
    except Exception:
        return False
    return c == w or w in c.parents


def resolve_in_workdir(workdir, rel):
    """Return (absolute Path, None) or (None, reason) for a write target."""
    if not isinstance(rel, str) or not rel.strip():
        return None, "path must be a non-empty string"
    p = Path(rel)
    if p.is_absolute():
        return None, "absolute path refused: %r (write paths are relative to the working directory)" % rel
    target = Path(workdir) / p
    if not _inside(workdir, target):
        return None, "path escapes the working directory: %r" % rel
    return target, None


def _path_like_tokens(command):
    """Best-effort static scan for path-shaped tokens in a shell command.

    Static, not a sandbox: a path hidden inside a quoted python one-liner will
    not be seen. Real isolation belongs in a container; this catches the honest
    mistakes and records the refusal where a grader can read it.
    """
    try:
        toks = shlex.split(command, comments=False)
    except ValueError:
        toks = command.split()
    out = []
    for tok in toks:
        if "=" in tok and not tok.startswith("/"):
            tok = tok.split("=", 1)[1]
        tok = tok.lstrip("<>&|0123456789")  # redirections: 2>/x, &>/x, >>/x
        if not tok:
            continue
        if tok.startswith("/") or tok == ".." or tok.startswith("../") or "/../" in tok or tok.endswith("/.."):
            out.append(tok)
    return out


def scan_command(command, workdir):
    """(ok, reason). Refuse commands naming paths outside the working directory."""
    for tok in _path_like_tokens(command):
        if tok.startswith("/"):
            if _inside(workdir, Path(tok)) or tok.startswith(SYSTEM_ROOTS):
                continue
            return False, "absolute path outside the working directory: %r" % tok
        if not _inside(workdir, Path(workdir) / tok):
            return False, "relative path escapes the working directory: %r" % tok
    return True, ""


# tools

RUN_BASH_TOOL = {
    "type": "function",
    "name": "run_bash",
    "description": ("Run a shell command inside the working directory and return its exit code, "
                    "stdout and stderr (each truncated at %d chars). Every path must stay inside "
                    "the working directory; absolute paths outside it and '..' escapes are refused."
                    % MAX_TOOL_OUTPUT_CHARS),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "the shell command, run with bash semantics in the working directory"},
            "timeout_s": {"type": "integer", "description": "per-command timeout in seconds (default %d)" % DEFAULT_BASH_TIMEOUT_S},
        },
        "required": ["command"],
        "additionalProperties": False,
    },
}

WRITE_FILE_TOOL = {
    "type": "function",
    "name": "write_file",
    "description": ("Write a UTF-8 text file inside the working directory, creating parent "
                    "directories. Use this for deliverables with exact filenames; it does not "
                    "depend on quoting a heredoc correctly."),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "path relative to the working directory"},
            "content": {"type": "string", "description": "full file content"},
        },
        "required": ["path", "content"],
        "additionalProperties": False,
    },
}


def tool_run_bash(workdir, args, budget_left_s):
    command = args.get("command")
    if not isinstance(command, str) or not command.strip():
        return {"error": "bad_arguments", "detail": "command must be a non-empty string"}
    ok, why = scan_command(command, workdir)
    if not ok:
        return {"error": "containment_violation", "detail": why,
                "hint": "All work must stay inside the working directory. Use paths relative to it."}
    try:
        t = int(args.get("timeout_s") or DEFAULT_BASH_TIMEOUT_S)
    except Exception:
        t = DEFAULT_BASH_TIMEOUT_S
    t = max(1, min(t, max(1, int(budget_left_s))))
    try:
        p = subprocess.run(command, shell=True, cwd=str(workdir), capture_output=True,
                           text=True, errors="replace", timeout=t)
    except subprocess.TimeoutExpired as exc:
        return {"error": "command_timeout", "timeout_s": t,
                "stdout": _truncate(exc.stdout), "stderr": _truncate(exc.stderr)}
    except Exception as exc:
        return {"error": "exec_failed", "detail": "%s: %s" % (type(exc).__name__, exc)}
    return {"exit_code": p.returncode, "stdout": _truncate(p.stdout), "stderr": _truncate(p.stderr)}


def tool_write_file(workdir, args):
    target, why = resolve_in_workdir(workdir, args.get("path"))
    if target is None:
        return {"error": "containment_violation", "detail": why,
                "hint": "Give a path relative to the working directory, e.g. 'out/answer.json'."}
    content = args.get("content")
    if content is None:
        content = ""
    if not isinstance(content, str):
        content = str(content)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except Exception as exc:
        return {"error": "write_failed", "detail": "%s: %s" % (type(exc).__name__, exc)}
    return {"ok": True, "path": os.path.relpath(str(target), str(Path(workdir).resolve(strict=False))),
            "bytes": len(content.encode("utf-8"))}


# session file

def load_session(path):
    if not path or not os.path.exists(path):
        return []
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return []
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)]


def save_session(path, items, model):
    if not path:
        return
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = str(p) + ".tmp"
        payload = {"adapter": "openai_agent", "model": model, "updated": _iso(), "items": items}
        Path(tmp).write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
        os.replace(tmp, str(p))
    except Exception:
        pass


def _sanitize_items(items):
    """Drop items a fresh request may reject: reasoning items whose encrypted
    payload has expired, and tool outputs whose call no longer has a call."""
    live = {i.get("call_id") for i in items if i.get("type") == "function_call"}
    out = []
    for i in items:
        if i.get("type") == "reasoning":
            continue
        if i.get("type") == "function_call_output" and i.get("call_id") not in live:
            continue
        out.append(i)
    return out


# API calls

def make_client():
    try:
        from openai import OpenAI
    except ImportError:
        print("openai SDK not installed: pip install openai", file=sys.stderr)
        raise SystemExit(2)
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set", file=sys.stderr)
        raise SystemExit(2)
    kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
    base = os.environ.get("OPENAI_BASE_URL")
    if base:  # same adapter drives any OpenAI-compatible endpoint
        kwargs["base_url"] = base
    return OpenAI(**kwargs)


def _is_transient(exc):
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    if isinstance(status, int) and (status in (408, 409, 429) or status >= 500):
        return True
    return type(exc).__name__ in {
        "APIConnectionError", "APITimeoutError", "APIConnectionTimeoutError",
        "RateLimitError", "InternalServerError", "ConnectionError", "Timeout",
    }


def create_with_retry(client, kwargs, deadline, tr):
    delay = BACKOFF_BASE_S
    for attempt in range(1, MAX_API_ATTEMPTS + 1):
        if time.time() >= deadline:
            raise BudgetExhausted()
        try:
            return _to_plain(client.responses.create(**kwargs))
        except Exception as exc:
            transient = _is_transient(exc)
            tr.log("api_error", attempt=attempt, transient=transient,
                   error_type=type(exc).__name__, error=str(exc)[:2000])
            if not transient or attempt == MAX_API_ATTEMPTS:
                raise
            nap = min(delay, deadline - time.time())
            if nap <= 0:
                raise BudgetExhausted()
            time.sleep(nap)
            delay = min(delay * 2, BACKOFF_CAP_S)
    raise RuntimeError("unreachable")


def extract_text(resp):
    parts = []
    for item in resp.get("output") or []:
        if item.get("type") == "message":
            for c in item.get("content") or []:
                if c.get("type") in ("output_text", "text") and c.get("text"):
                    parts.append(c["text"])
    if not parts and isinstance(resp.get("output_text"), str):
        parts.append(resp["output_text"])
    return "\n".join(parts).strip()


# agentic loop

def run_agent(client, model, prompt, workdir, tools, deadline, max_turns, tr, prior_items):
    items = list(prior_items) + [{"role": "user", "content": prompt}]
    turns = 0
    tool_calls = 0
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    final_text = ""
    exit_reason = "completed"
    timed_out = False
    error = None
    sanitized_once = False

    while True:
        if time.time() >= deadline:
            exit_reason, timed_out = "timeout", True
            break
        kwargs = {"model": model, "input": items,
                  "timeout": max(5.0, min(deadline - time.time(), 3600.0))}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        tr.log("request", turn=turns + 1, model=model, n_input_items=len(items),
               tools=[t["name"] for t in (tools or [])])
        try:
            resp = create_with_retry(client, kwargs, deadline, tr)
        except BudgetExhausted:
            exit_reason, timed_out = "timeout", True
            break
        except Exception as exc:
            # A stale session (expired reasoning items) looks like a terminal
            # 400. Strip those once and try again before giving up.
            if not sanitized_once and turns == 0 and prior_items:
                sanitized_once = True
                items = _sanitize_items(items)
                tr.log("retry_sanitized", reason=str(exc)[:500], n_input_items=len(items))
                continue
            error = "%s: %s" % (type(exc).__name__, exc)
            exit_reason = "api_error"
            tr.log("api_fatal", error=error, trace=traceback.format_exc()[-4000:])
            break

        turns += 1
        u = resp.get("usage") or {}
        for key, alt in (("input_tokens", "prompt_tokens"), ("output_tokens", "completion_tokens"),
                         ("total_tokens", "total_tokens")):
            v = u.get(key, u.get(alt))
            if isinstance(v, (int, float)):
                usage[key] += int(v)
        output = resp.get("output") or []
        tr.log("response", turn=turns, response_id=resp.get("id"), usage=u, output=output)
        items.extend(output)  # output items are valid input items next turn

        text = extract_text(resp)
        if text:
            final_text = text
        calls = [i for i in output if i.get("type") == "function_call"]
        if not calls:
            exit_reason = "completed"
            break

        for call in calls:  # a turn may carry several
            tool_calls += 1
            name = call.get("name")
            call_id = call.get("call_id") or call.get("id")
            raw = call.get("arguments")
            bad = None
            if isinstance(raw, dict):
                args = raw
            else:
                try:
                    args = json.loads(raw or "{}")
                except Exception:
                    args, bad = {}, {"error": "bad_arguments",
                                     "detail": "arguments were not valid JSON",
                                     "raw": _truncate(str(raw), 2000)}
            tr.log("tool_call", turn=turns, call_id=call_id, name=name,
                   arguments=args if bad is None else _truncate(str(raw), 2000))
            budget = deadline - time.time()
            if bad is not None:
                result = bad
            elif budget <= 0:
                result = {"error": "budget_exhausted", "detail": "the task wall-clock budget is spent"}
            elif name == "run_bash":
                result = tool_run_bash(workdir, args, budget)
            elif name == "write_file":
                result = tool_write_file(workdir, args)
            else:
                result = {"error": "unknown_tool", "detail": str(name)}
            tr.log("tool_result", turn=turns, call_id=call_id, name=name, result=result)
            items.append({"type": "function_call_output", "call_id": call_id,
                          "output": json.dumps(result, ensure_ascii=False, default=str)})

        if time.time() >= deadline:
            exit_reason, timed_out = "timeout", True
            break
        if turns >= max_turns:
            exit_reason = "max_turns"
            break

    return {"items": items, "turns": turns, "tool_calls": tool_calls, "usage": usage,
            "final_text": final_text, "exit_reason": exit_reason, "timed_out": timed_out,
            "error": error}


# CLI

def tools_for_mode(mode):
    """Which tools a task mode grants.

    `notools` still grants write_file: the tool-free tasks are scored on
    artifacts, and a system that cannot write files delivers nothing. This
    matches claude_code.sh, which grants Write in notools for the same reason.
    DELTAX_NOTOOLS_NO_WRITE=1 is the strict reading, and it breaks DX01 scoring.
    """
    if mode == "tools":
        return [RUN_BASH_TOOL, WRITE_FILE_TOOL]
    if os.environ.get("DELTAX_NOTOOLS_NO_WRITE") == "1":
        return None
    return [WRITE_FILE_TOOL]


def build_parser():
    p = argparse.ArgumentParser(
        prog="openai_agent.py",
        description="DELTA-X adapter: OpenAI GPT/ChatGPT models through the Responses API.",
        epilog="Env: OPENAI_API_KEY (required), OPENAI_BASE_URL (optional, for an "
               "OpenAI-compatible endpoint), DELTAX_OPENAI_MODEL (default model id), "
               "DELTAX_NOTOOLS_NO_WRITE=1 (withhold write_file in notools mode too -- "
               "breaks DX01 scoring, see --help). "
               "Pin --model explicitly for any published measurement.")
    p.add_argument("--prompt-file", help="file holding the whole task prompt (UTF-8)")
    p.add_argument("--workdir", help="the agent's working directory; all commands and writes stay inside it")
    p.add_argument("--mode", choices=("tools", "notools"), default="tools",
                   help="tools: run_bash + write_file; notools: write_file only, no shell")
    p.add_argument("--timeout-seconds", type=int, default=3600, help="hard wall-clock budget for this task")
    p.add_argument("--session-file", default="", help="JSON conversation state carried across tasks")
    p.add_argument("--out-json", help="where to write the result record")
    p.add_argument("--model", default="", help="model id (default $DELTAX_OPENAI_MODEL or %s)" % DEFAULT_MODEL)
    p.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS, help="model turns before stopping (default %d)" % DEFAULT_MAX_TURNS)
    p.add_argument("--self-test", action="store_true",
                   help="run the offline smoke test (no API key, no network) and exit")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.self_test:
        return self_test()

    missing = [f for f in ("prompt_file", "workdir", "out_json") if not getattr(args, f)]
    if missing:
        print("missing required option(s): %s" % ", ".join("--" + m.replace("_", "-") for m in missing), file=sys.stderr)
        return 2
    try:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    except Exception as exc:
        print("cannot read --prompt-file %s: %s" % (args.prompt_file, exc), file=sys.stderr)
        return 2
    model = args.model or os.environ.get("DELTAX_OPENAI_MODEL") or DEFAULT_MODEL
    workdir = Path(args.workdir)
    try:
        workdir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        print("cannot create --workdir %s: %s" % (args.workdir, exc), file=sys.stderr)
        return 2
    out_path = Path(args.out_json)
    tr = Transcript(out_path.parent / "transcript.jsonl")

    tools = tools_for_mode(args.mode)

    tr.log("task_start", model=model, mode=args.mode, workdir=str(workdir.resolve(strict=False)),
           prompt_file=str(args.prompt_file), prompt_chars=len(prompt),
           timeout_seconds=args.timeout_seconds, out_json=str(out_path),
           tools=[t["name"] for t in (tools or [])])

    client = make_client()  # exits 2 on a configuration error
    prior = load_session(args.session_file)
    started = time.time()
    res = run_agent(client, model, prompt, workdir, tools,
                    started + max(1, args.timeout_seconds), args.max_turns, tr, prior)
    elapsed = time.time() - started

    save_session(args.session_file, res["items"], model)
    record = {
        "adapter": "openai_agent", "model": model, "mode": args.mode,
        "api": "responses", "base_url": os.environ.get("OPENAI_BASE_URL") or "default",
        "turns": res["turns"], "tool_calls": res["tool_calls"],
        "exit_reason": res["exit_reason"], "timed_out": res["timed_out"],
        "wall_clock_seconds": round(elapsed, 2), "usage": res["usage"],
        "final_text": res["final_text"], "error": res["error"],
        "prompt_file": str(args.prompt_file), "workdir": str(workdir.resolve(strict=False)),
        "session_file": args.session_file or None,
        "transcript": str(tr.path), "finished_utc": _iso(),
    }
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(record, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    except Exception as exc:
        print("cannot write --out-json %s: %s" % (out_path, exc), file=sys.stderr)
    tr.log("task_end", **{k: v for k, v in record.items() if k != "final_text"})

    print("openai_agent: model=%s mode=%s turns=%d tool_calls=%d reason=%s timed_out=%s elapsed=%ds out=%s"
          % (model, args.mode, res["turns"], res["tool_calls"], res["exit_reason"],
             str(res["timed_out"]).lower(), int(elapsed), out_path))
    useful = res["tool_calls"] > 0 or bool(res["final_text"])
    if res["exit_reason"] == "api_error" and not useful:
        return 1
    return 0


# offline smoke test (--self-test): no API key, no network

class _FakeResponses:
    def __init__(self, outer):
        self._outer = outer

    def create(self, **kwargs):
        self._outer.calls.append(kwargs)
        return self._outer.scripted.pop(0)


class _FakeClient:
    """Stands in for openai.OpenAI; returns scripted plain-dict responses."""

    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = []
        self.responses = _FakeResponses(self)


def self_test():
    import tempfile
    fails = []

    def check(name, cond, detail=""):
        print("%-46s %s%s" % (name, "PASS" if cond else "FAIL", "" if cond else "  <- " + str(detail)))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp) / "work"
        wd.mkdir()
        outside = Path(tmp) / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("key material", encoding="utf-8")
        tr = Transcript(Path(tmp) / "transcript.jsonl")

        # 1. containment: command scanning
        check("scan: plain relative command allowed", scan_command("python3 analysis.py data/x.fasta", wd)[0])
        check("scan: absolute inside workdir allowed", scan_command("cat %s/note.md" % wd, wd)[0])
        check("scan: interpreter under /usr allowed", scan_command("/usr/bin/env python3 -c 'print(1)'", wd)[0])
        check("scan: absolute outside workdir refused", not scan_command("cat %s/secret.txt" % outside, wd)[0])
        check("scan: dotdot escape refused", not scan_command("cat ../outside/secret.txt", wd)[0])
        check("scan: redirect escape refused", not scan_command("echo hi > %s/pwn.txt" % outside, wd)[0])

        # 2. run_bash honours containment and does not execute the refused command
        r = tool_run_bash(wd, {"command": "cat %s/secret.txt" % outside}, 60)
        check("run_bash: refuses escape, no execution",
              r.get("error") == "containment_violation" and "stdout" not in r, r)
        r = tool_run_bash(wd, {"command": "echo contained"}, 60)
        check("run_bash: runs contained command", r.get("exit_code") == 0 and "contained" in r.get("stdout", ""), r)

        # 3. truncation, in the helper and end to end
        t = _truncate("a" * (MAX_TOOL_OUTPUT_CHARS + 500))
        check("truncate: caps and marks",
              t.startswith("a") and "[truncated 500 chars]" in t and len(t) < MAX_TOOL_OUTPUT_CHARS + 60, len(t))
        r = tool_run_bash(wd, {"command": "python3 -c \"print('b'*%d)\"" % (MAX_TOOL_OUTPUT_CHARS + 1000)}, 60)
        check("run_bash: truncates oversized stdout", "[truncated" in r.get("stdout", ""), list(r)[:3])

        # 4. write_file: escapes refused, normal write lands
        check("write_file: absolute path refused",
              tool_write_file(wd, {"path": "/etc/passwd", "content": "x"}).get("error") == "containment_violation")
        check("write_file: dotdot escape refused",
              tool_write_file(wd, {"path": "../outside/pwn.txt", "content": "x"}).get("error") == "containment_violation")
        check("write_file: escape wrote nothing", not (outside / "pwn.txt").exists())
        r = tool_write_file(wd, {"path": "sub/dir/answer.json", "content": '{"a":1}'})
        check("write_file: creates parents and writes",
              r.get("ok") and (wd / "sub/dir/answer.json").read_text(encoding="utf-8") == '{"a":1}', r)

        # 5. session file round-trip
        sess = Path(tmp) / "session.json"
        items = [{"role": "user", "content": "task one"},
                 {"type": "function_call", "call_id": "c1", "name": "write_file", "arguments": "{}"},
                 {"type": "function_call_output", "call_id": "c1", "output": "{}"}]
        save_session(str(sess), items, "m")
        check("session: round-trips items", load_session(str(sess)) == items)
        check("session: absent file -> empty history", load_session(str(Path(tmp) / "nope.json")) == [])
        bad = Path(tmp) / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        check("session: corrupt file -> empty history, no raise", load_session(str(bad)) == [])
        check("session: sanitize drops stale reasoning",
              _sanitize_items([{"type": "reasoning", "id": "r1"}] + items) == items)

        # 6. agentic loop against a fake client: tool call -> result -> final text
        scripted = [
            {"id": "resp_1", "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
             "output": [{"type": "function_call", "call_id": "call_1", "name": "write_file",
                         "arguments": json.dumps({"path": "out/dx01.json", "content": "{}"})},
                        {"type": "function_call", "call_id": "call_2", "name": "run_bash",
                         "arguments": json.dumps({"command": "ls out"})},
                        {"type": "function_call", "call_id": "call_3", "name": "run_bash",
                         "arguments": json.dumps({"command": "cat %s/secret.txt" % outside})}]},
            {"id": "resp_2", "usage": {"input_tokens": 20, "output_tokens": 7, "total_tokens": 27},
             "output": [{"type": "message", "content": [{"type": "output_text", "text": "done: wrote dx01.json"}]}]},
        ]
        client = _FakeClient(scripted)
        res = run_agent(client, "fake-model", "do the task", wd, [RUN_BASH_TOOL, WRITE_FILE_TOOL],
                        time.time() + 60, DEFAULT_MAX_TURNS, tr, load_session(str(sess)))
        check("loop: two turns, three tool calls", res["turns"] == 2 and res["tool_calls"] == 3, res["tool_calls"])
        check("loop: artifact landed on disk", (wd / "out/dx01.json").exists())
        check("loop: final text captured", res["final_text"] == "done: wrote dx01.json", res["final_text"])
        check("loop: exit reason completed, not timed out",
              res["exit_reason"] == "completed" and res["timed_out"] is False)
        check("loop: usage summed across turns", res["usage"]["total_tokens"] == 42, res["usage"])
        check("loop: prior session history prepended", res["items"][:len(items)] == items)
        check("loop: tool outputs fed back",
              sum(1 for i in res["items"] if i.get("type") == "function_call_output") == 4)

        # 7. the loop stops on an exhausted budget instead of raising
        res = run_agent(_FakeClient([]), "fake-model", "p", wd, None, time.time() - 1,
                        DEFAULT_MAX_TURNS, tr, [])
        check("loop: expired budget -> timeout, no raise",
              res["timed_out"] and res["exit_reason"] == "timeout" and res["turns"] == 0)

        # 8. notools mode sends no tools
        client = _FakeClient([{"id": "r", "output": [{"type": "message", "content": [{"type": "output_text", "text": "answer"}]}]}])
        res = run_agent(client, "fake-model", "p", wd, None, time.time() + 60, DEFAULT_MAX_TURNS, tr, [])
        check("notools: no tools in request and no tool calls",
              "tools" not in client.calls[0] and res["tool_calls"] == 0 and res["final_text"] == "answer")

        # 8b. the mode -> tools mapping main() uses
        os.environ.pop("DELTAX_NOTOOLS_NO_WRITE", None)
        names = lambda t: [x["name"] for x in (t or [])]
        check("mode mapping: tools grants shell and write",
              names(tools_for_mode("tools")) == ["run_bash", "write_file"])
        check("mode mapping: notools grants write only",
              names(tools_for_mode("notools")) == ["write_file"])
        os.environ["DELTAX_NOTOOLS_NO_WRITE"] = "1"
        check("mode mapping: DELTAX_NOTOOLS_NO_WRITE withholds it",
              tools_for_mode("notools") is None)
        os.environ.pop("DELTAX_NOTOOLS_NO_WRITE", None)

        lines = [json.loads(l) for l in (Path(tmp) / "transcript.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        events = [l["event"] for l in lines]
        check("transcript: every line is one JSON object", len(lines) >= 8, len(lines))
        check("transcript: records requests, calls and results",
              {"request", "response", "tool_call", "tool_result"} <= set(events), sorted(set(events)))
        check("transcript: refusal is visible to the grader",
              any(l["event"] == "tool_result" and l["result"].get("error") == "containment_violation"
                  for l in lines if l["event"] == "tool_result") or
              any("containment" in json.dumps(l) for l in lines), events)

    print("\nself-test: %d checks failed" % len(fails) if fails else "\nself-test: all checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
