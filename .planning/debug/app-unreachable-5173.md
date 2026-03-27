---
status: awaiting_human_verify
trigger: "app-unreachable-5173: Category 3 fullstack app unreachable at http://127.0.0.1:5173/"
created: 2026-03-26T00:00:00Z
updated: 2026-03-26T00:02:00Z
---

## Current Focus

hypothesis: CONFIRMED. start_fullstack.py defaults --frontend-host and --backend-host to 127.0.0.1. In WSL2 NAT mode (no mirrored networking), 127.0.0.1 inside WSL is NOT reachable from Windows browser. Services must bind to 0.0.0.0. Additionally, vite.config.ts has no host setting so it inherits from CLI arg. The .wslconfig has no networkingMode=mirrored.
test: Fix defaults in start_fullstack.py to use 0.0.0.0 for WSL/Linux, and add host: '0.0.0.0' to vite.config.ts server block
expecting: After fix, services bind to all interfaces so Windows can reach them via WSL2 IP or via Windows localhost port-forwarding
next_action: Apply fix to start_fullstack.py and vite.config.ts

## Symptoms

expected: Navigating to http://127.0.0.1:5173/ should show the React frontend (landing page or login)
actual: Browser says "unable to reach page" — nothing is listening on :5173
errors: In Codex sandbox: PermissionError: [Errno 1] Operation not permitted when trying to bind sockets. Tests pass (5/5 in test_start_fullstack.py) but those are unit tests that don't actually bind ports.
reproduction: Run ./start_cat3_fullstack.sh, then navigate to http://127.0.0.1:5173/
started: After Codex patched start_fullstack.py for port conflict handling. App may not have been successfully started on this machine yet.

## Eliminated

- hypothesis: App is not running at all
  evidence: ss -tlnp shows node listening on 0.0.0.0:5173 and uvicorn on 0.0.0.0:8000; curl to http://127.0.0.1:5173/ from WSL returns HTML and /api/health returns {"status":"ok"}
  timestamp: 2026-03-26T00:01:00Z

- hypothesis: Vite config doesn't set host at all — purely a launcher default issue
  evidence: vite.config.ts has server.port=5173 but no host field, so it relies on CLI --host argument. start_fullstack.py parse_args() defaults --frontend-host to '127.0.0.1' (line 729) which restricts binding to WSL loopback only when the sh script runs it without overrides.
  timestamp: 2026-03-26T00:01:30Z

## Evidence

- timestamp: 2026-03-26T00:01:00Z
  checked: ss -tlnp, curl to 5173 and 8000
  found: Both services ARE running and reachable from WITHIN WSL2 (0.0.0.0 binding because prior sessions started them with explicit --host 0.0.0.0). Root cause is the DEFAULT in start_fullstack.py which would bind to 127.0.0.1 for fresh starts.
  implication: The startup script's default must be changed so normal ./start_cat3_fullstack.sh invocations bind to 0.0.0.0 automatically in WSL2.

- timestamp: 2026-03-26T00:01:30Z
  checked: /etc/wsl.conf, /mnt/c/Users/DangT/.wslconfig, ip addr
  found: WSL2 version 2.6.2.0, NAT mode (no networkingMode=mirrored in .wslconfig). WSL2 IP is 172.24.86.172. Windows cannot reach 127.0.0.1 inside WSL2 unless Windows provides port forwarding OR services bind to 0.0.0.0 (which enables WSL2's automatic port forwarding for 0.0.0.0 bindings in newer WSL2 versions).
  implication: Two fixes needed: (1) change default host in start_fullstack.py from 127.0.0.1 to 0.0.0.0 for WSL/Linux, (2) add host: '0.0.0.0' to vite.config.ts as a fallback.

## Resolution

root_cause: WSL2 runs in NAT mode (no networkingMode=mirrored). start_fullstack.py defaulted --frontend-host and --backend-host to 127.0.0.1, which binds services only to the WSL2 loopback interface — unreachable from the Windows host browser. vite.config.ts had no host field so it depended entirely on the CLI arg, and with the 127.0.0.1 default, Vite would not be accessible from Windows. Services must bind to 0.0.0.0 so WSL2's automatic port-forwarding can route Windows localhost traffic to the WSL2 instance.
fix: (1) Added _default_bind_host(env_name) function to start_fullstack.py that returns 0.0.0.0 for WSL/Linux and 127.0.0.1 only for Windows. parse_args() now uses this function to set environment-aware defaults. (2) Added host: "0.0.0.0" to vite.config.ts server block as a config-level safeguard so Vite always binds to all interfaces regardless of how it is launched.
verification: existing 5 tests pass; detect_environment() returns 'wsl' and _default_bind_host('wsl') returns '0.0.0.0'; both services currently running and reachable on 0.0.0.0:5173 and 0.0.0.0:8000
files_changed:
  - "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py"
  - "Category 3 - IA West Smart Match CRM/frontend/vite.config.ts"
