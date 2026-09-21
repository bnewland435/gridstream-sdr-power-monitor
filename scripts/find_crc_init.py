#!/usr/bin/env python3
"""Infer and verify the CRC-16/CCITT initialization used by decoded frames."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def crc16_ccitt(data: bytes, init: int) -> int:
    crc = init
    for value in data:
        crc ^= value << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def crc_body(frame: bytes) -> bytes:
    if frame.startswith(bytes.fromhex("80 FF 2A")):
        return frame[6:-2]
    if frame.startswith(bytes.fromhex("2A")):
        return frame[4:-2]
    raise ValueError("frame does not begin with 80 FF 2A or 2A")


def normalized_length_ok(frame: bytes) -> bool:
    if frame.startswith(bytes.fromhex("80 FF 2A")):
        return len(frame) >= 8 and len(frame) == frame[5] + 6
    return len(frame) >= 6 and len(frame) == frame[3] + 4


def read_csv(path: Path) -> list[bytes]:
    frames: list[bytes] = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            if not row.get("hex"):
                continue
            frame = bytes.fromhex(row["hex"])
            if row.get("sync_errors") not in (None, "0"):
                continue
            if row.get("uart_valid") and row.get("uart_total"):
                if row["uart_valid"] != row["uart_total"]:
                    continue
            if normalized_length_ok(frame):
                frames.append(frame)
    return frames


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, nargs="+", help="decoded-frame CSV files")
    parser.add_argument("--compare", default="0x142A", help="comparison init (default: 0x142A)")
    args = parser.parse_args()

    frames = [frame for path in args.csv for frame in read_csv(path)]
    if not frames:
        parser.error("no strict, length-consistent frames found")

    first = frames[0]
    expected = int.from_bytes(first[-2:], "big")
    matches = [value for value in range(0x10000) if crc16_ccitt(crc_body(first), value) == expected]
    if len(matches) != 1:
        raise SystemExit(f"expected one initialization candidate; found {len(matches)}")

    inferred = matches[0]
    compare = int(args.compare, 0)
    inferred_ok = sum(crc16_ccitt(crc_body(frame), inferred) == int.from_bytes(frame[-2:], "big") for frame in frames)
    compare_ok = sum(crc16_ccitt(crc_body(frame), compare) == int.from_bytes(frame[-2:], "big") for frame in frames)

    print(f"strict_frames={len(frames)}")
    print(f"inferred_init=0x{inferred:04X} valid={inferred_ok}/{len(frames)}")
    print(f"comparison_init=0x{compare:04X} valid={compare_ok}/{len(frames)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
