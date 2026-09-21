#!/usr/bin/env python3
"""Fail when a repository contains raw captures or private identifiers."""

from __future__ import annotations

import os
import pathlib
import re
import sys


BLOCKED_SUFFIXES = {".cu8", ".iq", ".pcap", ".pcapng"}
SKIP_DIRS = {".git", ".venv", "__pycache__"}


def compact_forms(value: str) -> set[bytes]:
    compact = re.sub(r"[^0-9A-Fa-f]", "", value).upper()
    if not compact:
        return set()
    forms = {compact.encode()}
    if len(compact) % 2 == 0:
        forms.add(" ".join(compact[i : i + 2] for i in range(0, len(compact), 2)).encode())
        forms.add(":".join(compact[i : i + 2] for i in range(0, len(compact), 2)).encode())
    return {item.lower() for item in forms}


def main(root: pathlib.Path) -> int:
    private = os.environ.get("PRIVATE_METER_IDS", "")
    needles = set()
    for item in private.split(","):
        if item.strip():
            needles.update(compact_forms(item))

    problems: list[str] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts) or not path.is_file():
            continue
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            problems.append(f"blocked capture type: {path}")
            continue
        try:
            data = path.read_bytes().lower()
        except OSError as exc:
            problems.append(f"unable to inspect {path}: {exc}")
            continue
        for needle in needles:
            if needle in data:
                problems.append(f"private identifier found in {path}")
                break

    if problems:
        print("Privacy check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Privacy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
