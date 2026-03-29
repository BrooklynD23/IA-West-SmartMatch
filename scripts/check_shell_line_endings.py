#!/usr/bin/env python3
"""Fail when shell scripts contain CRLF line endings."""

from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []

    for script in repo_root.rglob("*.sh"):
        if ".git" in script.parts:
            continue
        data = script.read_bytes()
        if b"\r\n" in data:
            offenders.append(str(script.relative_to(repo_root)))

    if offenders:
        print("CRLF line endings detected in shell scripts:")
        for path in sorted(offenders):
            print(f" - {path}")
        print("\nConvert these files to LF line endings.")
        return 1

    print("OK: all shell scripts use LF line endings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
