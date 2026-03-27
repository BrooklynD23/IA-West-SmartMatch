#!/usr/bin/env python3
"""Start CAT3 FastAPI + React dev stack with Windows/WSL-aware behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import webbrowser
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence
from urllib.error import URLError
from urllib.request import urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"
FULLSTACK_REQUIREMENTS_FILE = ROOT_DIR / "requirements-fullstack.txt"
INSTALL_STATE_FILE = ROOT_DIR / ".venv" / ".cat3-fullstack-install-state.json"
LOG_DIR = Path(tempfile.gettempdir()) / "cat3-fullstack"
PYTHON_READINESS_MODULES = ("dotenv", "fastapi", "uvicorn", "numpy", "pandas", "qrcode")
BACKEND_READY_TIMEOUT_SECONDS = 30.0
FRONTEND_READY_TIMEOUT_SECONDS = 45.0
EXISTING_BACKEND_PROBE_SECONDS = 1.5
BACKEND_PORT_CONFLICT_GRACE_SECONDS = 5.0
LOG_TAIL_LINES = 12


@dataclass
class StatusStep:
    key: str
    label: str
    status: str = "pending"
    detail: str = ""


class StatusBoard:
    """Render a compact multi-step status board for interactive terminals."""

    _ICONS = {
        "pending": "○",
        "running": "…",
        "done": "✔",
        "error": "✖",
    }

    def __init__(self, title: str) -> None:
        self.title = title
        self.steps: list[StatusStep] = []
        self._rendered_lines = 0
        self._interactive = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"

    def add(self, key: str, label: str) -> None:
        self.steps.append(StatusStep(key=key, label=label))

    def update(self, key: str, status: str, detail: str = "") -> None:
        step = self._step(key)
        step.status = status
        step.detail = detail
        self.render()

    def render(self) -> None:
        lines = self._build_lines()
        if self._interactive:
            if self._rendered_lines:
                sys.stdout.write(f"\x1b[{self._rendered_lines}F")
            sys.stdout.write("\n".join(lines))
            sys.stdout.write("\n\x1b[J")
            sys.stdout.flush()
            self._rendered_lines = len(lines)
            return

        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    def _step(self, key: str) -> StatusStep:
        for step in self.steps:
            if step.key == key:
                return step
        raise KeyError(f"Unknown status key: {key}")

    def _build_lines(self) -> list[str]:
        total = max(len(self.steps), 1)
        completed = sum(1 for step in self.steps if step.status == "done")
        filled = min(10, round((completed / total) * 10))
        progress_bar = ("#" * filled) + ("-" * (10 - filled))
        lines = [f"{self.title} [{progress_bar}] {completed}/{len(self.steps)}"]
        for step in self.steps:
            icon = self._ICONS.get(step.status, "?")
            detail = f" | {self._trim(step.detail)}" if step.detail else ""
            lines.append(f"{icon} {step.label}{detail}")
        return lines

    @staticmethod
    def _trim(value: str, limit: int = 92) -> str:
        if len(value) <= limit:
            return value
        return value[: limit - 3] + "..."


def detect_environment() -> str:
    if os.name == "nt":
        return "windows"
    release = platform.release().lower()
    if "microsoft" in release or os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
        return "wsl"
    return "linux"


def run(cmd: Sequence[str], cwd: Path) -> None:
    subprocess.check_call(list(cmd), cwd=str(cwd))


def path_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_install_state() -> dict[str, dict[str, str]]:
    if not INSTALL_STATE_FILE.exists():
        return {}
    try:
        return json.loads(INSTALL_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_install_state(state: dict[str, dict[str, str]]) -> None:
    INSTALL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_STATE_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def install_signature(path: Path) -> dict[str, str]:
    return {
        "path": path_label(path),
        "sha256": hash_file(path),
    }


def python_runtime_ready(python_cmd: str) -> bool:
    probe = (
        "import importlib.util, sys; "
        "missing=[name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]; "
        "raise SystemExit(0 if not missing else 1)"
    )
    result = subprocess.run(
        [python_cmd, "-c", probe, *PYTHON_READINESS_MODULES],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def frontend_runtime_ready() -> bool:
    candidates = (
        FRONTEND_DIR / "node_modules" / ".bin" / "vite",
        FRONTEND_DIR / "node_modules" / ".bin" / "vite.cmd",
        FRONTEND_DIR / "node_modules" / ".bin" / "vite.ps1",
    )
    return any(candidate.exists() for candidate in candidates)


def default_requirements_file(full_install: bool) -> Path:
    if not full_install and FULLSTACK_REQUIREMENTS_FILE.exists():
        return FULLSTACK_REQUIREMENTS_FILE
    return REQUIREMENTS_FILE


def parse_pip_detail(line: str) -> str | None:
    clean = line.strip()
    if not clean:
        return None
    if clean.startswith("Collecting "):
        return clean.split(" (from", 1)[0]
    if clean.startswith("Downloading "):
        return clean
    if clean.startswith("Using cached "):
        return clean
    if clean.startswith("Installing collected packages:"):
        return "Installing resolved packages"
    if clean.startswith("INFO: pip is looking at multiple versions"):
        return "Resolving dependency versions"
    return None


def parse_npm_detail(line: str) -> str | None:
    clean = line.strip()
    if not clean:
        return None
    if clean.startswith("added ") or clean.startswith("removed "):
        return clean
    if clean.startswith("up to date"):
        return clean
    if clean.startswith("changed "):
        return clean
    if clean.startswith("npm WARN"):
        return clean
    return None


def ensure_log_dir() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def new_log_path(stem: str) -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return ensure_log_dir() / f"{timestamp}-{stem}.log"


def read_log_tail(log_path: Path, max_lines: int = LOG_TAIL_LINES) -> list[str]:
    if not log_path.exists():
        return []
    with log_path.open(encoding="utf-8", errors="replace") as fh:
        return list(deque((line.rstrip() for line in fh if line.strip()), maxlen=max_lines))


def run_logged_command(
    cmd: Sequence[str],
    cwd: Path,
    board: StatusBoard,
    step_key: str,
    log_stem: str,
    parser: Callable[[str], str | None] | None = None,
) -> Path:
    log_path = new_log_path(log_stem)
    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        process = subprocess.Popen(
            list(cmd),
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        assert process.stdout is not None
        for raw_line in process.stdout:
            log_file.write(raw_line)
            if parser is None:
                continue
            detail = parser(raw_line)
            if detail:
                board.update(step_key, "running", detail)

        return_code = process.wait()

    if return_code != 0:
        tail = read_log_tail(log_path)
        detail = tail[-1] if tail else f"Command exited with code {return_code}"
        board.update(step_key, "error", detail)
        raise RuntimeError(f"Command failed. See log: {log_path}")

    return log_path


def find_python(env_name: str) -> str:
    candidates: list[Path] = []
    if env_name == "windows":
        candidates.append(ROOT_DIR / ".venv" / "Scripts" / "python.exe")
    else:
        candidates.append(ROOT_DIR / ".venv" / "bin" / "python")

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    for executable in ("python3", "python"):
        path = shutil.which(executable)
        if path:
            return path

    raise RuntimeError("No Python runtime found. Install Python 3.11+ and retry.")


def ensure_venv(env_name: str, python_cmd: str) -> str:
    if env_name == "windows":
        venv_python = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = ROOT_DIR / ".venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)

    if env_name == "windows":
        py_launcher = shutil.which("py")
        if py_launcher:
            run([py_launcher, "-3", "-m", "venv", ".venv"], ROOT_DIR)
        else:
            run([python_cmd, "-m", "venv", ".venv"], ROOT_DIR)
    else:
        run([python_cmd, "-m", "venv", ".venv"], ROOT_DIR)

    if not venv_python.exists():
        raise RuntimeError("Virtualenv creation completed but no .venv python executable was found.")
    return str(venv_python)


def ensure_python_requirements(
    python_cmd: str,
    requirements_path: Path,
    board: StatusBoard,
    force_install: bool,
) -> None:
    if not requirements_path.exists():
        raise RuntimeError(f"Missing requirements file: {requirements_path}")

    state = load_install_state()
    signature = install_signature(requirements_path)
    if not force_install and state.get("python") == signature and python_runtime_ready(python_cmd):
        board.update("python_deps", "done", f"Already current ({path_label(requirements_path)})")
        return

    board.update("python_deps", "running", f"Syncing {path_label(requirements_path)}")
    run_logged_command(
        [
            python_cmd,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--progress-bar",
            "off",
            "-r",
            str(requirements_path),
        ],
        ROOT_DIR,
        board,
        "python_deps",
        "python-deps",
        parser=parse_pip_detail,
    )
    state["python"] = signature
    save_install_state(state)
    board.update("python_deps", "done", f"Ready ({path_label(requirements_path)})")


def ensure_frontend_requirements(
    npm_cmd: str,
    board: StatusBoard,
    force_install: bool,
) -> None:
    if not FRONTEND_DIR.exists():
        raise RuntimeError(f"Missing frontend directory: {FRONTEND_DIR}")

    package_lock = FRONTEND_DIR / "package-lock.json"
    package_manifest = package_lock if package_lock.exists() else FRONTEND_DIR / "package.json"
    state = load_install_state()
    signature = install_signature(package_manifest)

    if not force_install and state.get("frontend") == signature and frontend_runtime_ready():
        board.update("frontend_deps", "done", f"Already current ({path_label(package_manifest)})")
        return

    board.update("frontend_deps", "running", f"Syncing {path_label(package_manifest)}")
    run_logged_command(
        [npm_cmd, "install", "--no-fund", "--no-audit"],
        FRONTEND_DIR,
        board,
        "frontend_deps",
        "frontend-deps",
        parser=parse_npm_detail,
    )
    state["frontend"] = signature
    save_install_state(state)
    board.update("frontend_deps", "done", f"Ready ({path_label(package_manifest)})")


def open_browser(url: str, env_name: str) -> None:
    if env_name == "windows":
        webbrowser.open(url)
        return
    if env_name == "wsl":
        cmd_exe = shutil.which("cmd.exe")
        if cmd_exe:
            subprocess.Popen(
                [cmd_exe, "/c", "start", "", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
    try:
        webbrowser.open(url)
    except Exception:
        pass


def build_backend_command(python_cmd: str, backend_host: str, backend_port: int) -> list[str]:
    return [
        python_cmd,
        "-m",
        "uvicorn",
        "src.api.main:app",
        "--host",
        backend_host,
        "--port",
        str(backend_port),
        "--reload",
    ]


def build_frontend_command(npm_cmd: str, frontend_host: str, frontend_port: int) -> list[str]:
    return [
        npm_cmd,
        "run",
        "dev",
        "--",
        "--host",
        frontend_host,
        "--port",
        str(frontend_port),
        "--strictPort",
    ]


def wait_for_http(url: str, timeout_seconds: float, process: subprocess.Popen[object] | None = None) -> tuple[bool, str]:
    deadline = time.monotonic() + timeout_seconds
    last_error = "Timed out waiting for service readiness"
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            return False, f"Process exited with code {process.poll()}"
        try:
            with urlopen(url, timeout=2) as response:
                status = getattr(response, "status", 200)
                if 200 <= status < 500:
                    return True, f"{status}"
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            last_error = str(reason)
        except OSError as exc:
            last_error = str(exc)
        time.sleep(0.5)
    return False, last_error


def service_ready(url: str, timeout_seconds: float) -> bool:
    ready, _ = wait_for_http(url, timeout_seconds)
    return ready


def service_reuse_detail(url: str) -> str:
    return f"Already running | {url}"


def maybe_reuse_backend(board: StatusBoard, api_url: str) -> bool:
    if not service_ready(api_url, EXISTING_BACKEND_PROBE_SECONDS):
        return False
    board.update("backend", "done", service_reuse_detail(api_url))
    return True


def startup_failure_detail(default_detail: str, log_path: Path | None) -> str:
    tail = read_log_tail(log_path) if log_path is not None else []
    return tail[-1] if tail else default_detail


def log_contains_phrase(log_path: Path | None, phrase: str, max_lines: int = LOG_TAIL_LINES * 4) -> bool:
    if log_path is None:
        return False
    return any(phrase in line for line in read_log_tail(log_path, max_lines=max_lines))


def resolve_backend_port_conflict(
    api_url: str,
    backend_host: str,
    backend_port: int,
    log_path: Path | None,
    timeout_seconds: float = BACKEND_PORT_CONFLICT_GRACE_SECONDS,
) -> tuple[bool, str]:
    if service_ready(api_url, timeout_seconds):
        return True, service_reuse_detail(api_url)

    detail = f"Port {backend_host}:{backend_port} already in use"
    if log_path is not None:
        detail = f"{detail} | {log_path}"
    return False, detail


def terminate_processes(processes: Sequence[subprocess.Popen[object] | None]) -> None:
    for process in processes:
        if process is not None and process.poll() is None:
            process.terminate()
    time.sleep(0.5)
    for process in processes:
        if process is not None and process.poll() is None:
            process.kill()


def launch_logged_process(cmd: Sequence[str], cwd: Path, log_stem: str) -> tuple[subprocess.Popen[object], Path, object]:
    log_path = new_log_path(log_stem)
    log_handle = log_path.open("w", encoding="utf-8", errors="replace", buffering=1)
    process = subprocess.Popen(
        list(cmd),
        cwd=str(cwd),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    return process, log_path, log_handle


def start_windows(
    python_cmd: str,
    npm_cmd: str,
    env_name: str,
    backend_host: str,
    backend_port: int,
    frontend_host: str,
    frontend_port: int,
    board: StatusBoard,
    auto_open_browser: bool,
) -> int:
    creation_flags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
    ui_url = f"http://127.0.0.1:{frontend_port}"
    api_url = f"http://127.0.0.1:{backend_port}/api/health"

    backend_proc: subprocess.Popen[object] | None = None
    if maybe_reuse_backend(board, api_url):
        pass
    else:
        board.update("backend", "running", f"Launching FastAPI on {backend_host}:{backend_port}")
        backend_proc = subprocess.Popen(
            build_backend_command(python_cmd, backend_host, backend_port),
            cwd=str(ROOT_DIR),
            creationflags=creation_flags,
        )
        backend_ok, backend_detail = wait_for_http(api_url, BACKEND_READY_TIMEOUT_SECONDS, process=backend_proc)
        if not backend_ok:
            board.update("backend", "error", backend_detail)
            terminate_processes((backend_proc,))
            return 1
        board.update("backend", "done", api_url)

    board.update("frontend", "running", f"Launching React on {frontend_host}:{frontend_port}")
    frontend_proc = subprocess.Popen(
        build_frontend_command(npm_cmd, frontend_host, frontend_port),
        cwd=str(FRONTEND_DIR),
        creationflags=creation_flags,
    )
    frontend_ok, frontend_detail = wait_for_http(ui_url, FRONTEND_READY_TIMEOUT_SECONDS, process=frontend_proc)
    if not frontend_ok:
        board.update("frontend", "error", frontend_detail)
        terminate_processes((backend_proc, frontend_proc))
        return 1
    board.update("frontend", "done", ui_url)

    if auto_open_browser:
        open_browser(ui_url, env_name)

    if backend_proc is None:
        board.update("ready", "done", "Frontend launched | reused backend on :8000")
        return 0

    board.update("ready", "done", "Running in separate terminal windows")
    return 0


def start_unix(
    python_cmd: str,
    npm_cmd: str,
    env_name: str,
    backend_host: str,
    backend_port: int,
    frontend_host: str,
    frontend_port: int,
    board: StatusBoard,
    auto_open_browser: bool,
) -> int:
    ui_url = f"http://127.0.0.1:{frontend_port}"
    api_url = f"http://127.0.0.1:{backend_port}/api/health"

    backend_proc: subprocess.Popen[object] | None = None
    frontend_proc: subprocess.Popen[object] | None = None
    backend_log_handle: object | None = None
    frontend_log_handle: object | None = None
    backend_log_path: Path | None = None
    frontend_log_path: Path | None = None
    stopping = False
    interrupted = False

    def close_logs() -> None:
        for handle in (backend_log_handle, frontend_log_handle):
            if handle is None:
                continue
            try:
                handle.close()  # type: ignore[call-arg]
            except Exception:
                pass

    def stop_processes() -> None:
        nonlocal stopping
        if stopping:
            return
        stopping = True
        terminate_processes((backend_proc, frontend_proc))
        close_logs()

    def handle_signal(signum: int, _frame: object) -> None:
        nonlocal interrupted
        interrupted = True
        board.update("ready", "running", f"Stopping services (signal {signum})")
        stop_processes()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        if maybe_reuse_backend(board, api_url):
            pass
        else:
            board.update("backend", "running", f"Starting FastAPI on {backend_host}:{backend_port}")
            backend_proc, backend_log_path, backend_log_handle = launch_logged_process(
                build_backend_command(python_cmd, backend_host, backend_port),
                ROOT_DIR,
                "backend",
            )
            backend_ok, backend_detail = wait_for_http(
                api_url,
                BACKEND_READY_TIMEOUT_SECONDS,
                process=backend_proc,
            )
            if not backend_ok:
                if log_contains_phrase(backend_log_path, "Address already in use"):
                    backend_reused, backend_detail = resolve_backend_port_conflict(
                        api_url,
                        backend_host,
                        backend_port,
                        backend_log_path,
                    )
                    if backend_reused:
                        board.update("backend", "done", backend_detail)
                        backend_proc = None
                    else:
                        board.update("backend", "error", backend_detail)
                        stop_processes()
                        return 1
                else:
                    failure_detail = startup_failure_detail(backend_detail, backend_log_path)
                    board.update("backend", "error", f"{failure_detail} | {backend_log_path}")
                    stop_processes()
                    return backend_proc.poll() or 1
            else:
                board.update("backend", "done", api_url)

        board.update("frontend", "running", f"Starting React on {frontend_host}:{frontend_port}")
        frontend_proc, frontend_log_path, frontend_log_handle = launch_logged_process(
            build_frontend_command(npm_cmd, frontend_host, frontend_port),
            FRONTEND_DIR,
            "frontend",
        )
        frontend_ok, frontend_detail = wait_for_http(
            ui_url,
            FRONTEND_READY_TIMEOUT_SECONDS,
            process=frontend_proc,
        )
        if not frontend_ok:
            failure_detail = startup_failure_detail(frontend_detail, frontend_log_path)
            board.update("frontend", "error", f"{failure_detail} | {frontend_log_path}")
            stop_processes()
            return frontend_proc.poll() or 1
        board.update("frontend", "done", ui_url)

        if auto_open_browser:
            open_browser(ui_url, env_name)

        board.update("ready", "done", f"Ctrl+C to stop | logs in {LOG_DIR}")

        while True:
            backend_code = None if backend_proc is None else backend_proc.poll()
            frontend_code = None if frontend_proc is None else frontend_proc.poll()
            if (backend_proc is not None and backend_code is not None) or (
                frontend_proc is not None and frontend_code is not None
            ):
                if stopping and interrupted:
                    board.update("ready", "done", "Stopped")
                    return 0
                if backend_code is not None:
                    detail = f"Exited {backend_code}"
                    if backend_log_path is not None:
                        detail = f"{detail} | {backend_log_path}"
                    board.update("backend", "error", detail)
                if frontend_code is not None:
                    detail = f"Exited {frontend_code}"
                    if frontend_log_path is not None:
                        detail = f"{detail} | {frontend_log_path}"
                    board.update("frontend", "error", detail)
                board.update("ready", "error", "A service exited")
                stop_processes()
                return backend_code or frontend_code or 0
            time.sleep(1.0)
    finally:
        stop_processes()


def _default_bind_host(env_name: str) -> str:
    """Return the default bind host for the detected environment.

    On Windows the process listens only on the loopback adapter since Windows
    handles its own port-forwarding.  On WSL2 / Linux the process must bind on
    all interfaces (0.0.0.0) so that WSL2's automatic port-forwarding makes the
    service reachable from the Windows host browser via 127.0.0.1 or the WSL2
    NAT address.
    """
    return "127.0.0.1" if env_name == "windows" else "0.0.0.0"


def parse_args() -> argparse.Namespace:
    env_name = detect_environment()
    default_host = _default_bind_host(env_name)
    parser = argparse.ArgumentParser(
        description="Start CAT3 React frontend + FastAPI backend with Windows/WSL-aware defaults."
    )
    parser.add_argument("--backend-port", type=int, default=8000, help="FastAPI port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=5173, help="React/Vite port (default: 5173)")
    parser.add_argument(
        "--backend-host",
        default=default_host,
        help=f"FastAPI bind host (default: {default_host} for {env_name})",
    )
    parser.add_argument(
        "--frontend-host",
        default=default_host,
        help=f"React/Vite bind host (default: {default_host} for {env_name})",
    )
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency install checks")
    parser.add_argument("--force-install", action="store_true", help="Force dependency sync even when cached state matches")
    parser.add_argument(
        "--full-install",
        action="store_true",
        help="Install the full requirements.txt instead of the slim fullstack dependency set",
    )
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_name = detect_environment()
    board = StatusBoard("CAT3 Fullstack")
    board.add("environment", "Environment")
    board.add("python", "Python runtime")
    board.add("python_deps", "Python deps")
    board.add("frontend_deps", "Frontend deps")
    board.add("backend", "Backend")
    board.add("frontend", "Frontend")
    board.add("ready", "Ready")
    board.render()

    board.update("environment", "done", env_name.upper())

    board.update("python", "running", "Locating interpreter")
    python_cmd = find_python(env_name)
    python_cmd = ensure_venv(env_name, python_cmd)
    board.update("python", "done", path_label(Path(python_cmd)))

    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        raise RuntimeError("npm is not installed or not on PATH. Install Node.js 18+ and retry.")

    if args.skip_install:
        board.update("python_deps", "done", "Skipped (--skip-install)")
        board.update("frontend_deps", "done", "Skipped (--skip-install)")
    else:
        requirements_path = default_requirements_file(args.full_install)
        ensure_python_requirements(
            python_cmd,
            requirements_path,
            board,
            force_install=args.force_install,
        )
        ensure_frontend_requirements(
            npm_cmd,
            board,
            force_install=args.force_install,
        )

    if env_name == "windows":
        return start_windows(
            python_cmd=python_cmd,
            npm_cmd=npm_cmd,
            env_name=env_name,
            backend_host=args.backend_host,
            backend_port=args.backend_port,
            frontend_host=args.frontend_host,
            frontend_port=args.frontend_port,
            board=board,
            auto_open_browser=not args.no_browser,
        )

    return start_unix(
        python_cmd=python_cmd,
        npm_cmd=npm_cmd,
        env_name=env_name,
        backend_host=args.backend_host,
        backend_port=args.backend_port,
        frontend_host=args.frontend_host,
        frontend_port=args.frontend_port,
        board=board,
        auto_open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[start_fullstack] ERROR: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
