#!/usr/bin/env python3
import csv
import glob
import os
from collections import Counter

import numpy as np
from scipy.ndimage import label, uniform_filter1d

FS = 250000.0
BAUD = 9600.0
SPS = FS / BAUD
SYNC = np.array([int(c) for c in "1010101010101010000000000111111111111"], dtype=np.uint8)


def tone_threshold(values):
    values = values[np.isfinite(values)]
    values = values[(values > -120000) & (values < 120000)]
    if len(values) < 100:
        return None, None, None
    c = np.percentile(values, [25, 75]).astype(float)
    for _ in range(20):
        which = np.abs(values[:, None] - c[None, :]).argmin(axis=1)
        nc = np.array([values[which == k].mean() if np.any(which == k) else c[k] for k in range(2)])
        if np.max(np.abs(nc - c)) < 0.1:
            break
        c = nc
    c.sort()
    return float(c.mean()), float(c[0]), float(c[1])


def uart_decode(bits, start):
    vals = []
    valid = 0
    total = 0
    for j in range(start, len(bits) - 9, 10):
        x = bits[j:j + 10]
        total += 1
        valid += int(x[0] == 0 and x[9] == 1)
        vals.append(sum(int(x[k + 1]) << k for k in range(8)))
    return bytes(vals), valid, total


def decode_segment(z, a, b):
    dphi = np.angle(z[1:] * np.conj(z[:-1])) * FS / (2 * np.pi)
    dphi = uniform_filter1d(dphi, 9)
    lo = max(a + 10, 0)
    hi = min(b - 10, len(dphi))
    threshold, tone0, tone1 = tone_threshold(dphi[lo:hi])
    if threshold is None or tone1 - tone0 < 3000:
        return None

    best = None
    # The captures are already close to 9600 baud. Search sampling phase and polarity.
    for phase in np.arange(0, SPS, 0.5):
        count = int((b - a - phase) / SPS)
        if count < len(SYNC) + 20:
            continue
        pos = a + phase + np.arange(count) * SPS
        raw = (np.interp(pos, np.arange(len(dphi)), dphi) > threshold).astype(np.uint8)
        for polarity in (0, 1):
            bits = raw ^ polarity
            for si in range(len(bits) - len(SYNC) + 1):
                hd = int(np.count_nonzero(bits[si:si + len(SYNC)] != SYNC))
                if hd > 2:
                    continue
                # UART starts immediately after the 37-bit G5 synchronization sequence.
                payload, valid, total = uart_decode(bits, si + len(SYNC))
                if total < 2:
                    continue
                prefix = int(payload[0] == 0x2A) + int(len(payload) > 1 and payload[1] in (0xD5, 0x55))
                score = valid * 20 + prefix * 100 - hd * 10 - (total - valid) * 5
                item = (score, valid, total, -hd, payload, phase, polarity, si, tone0, tone1)
                if best is None or item[:4] > best[:4]:
                    best = item
    return best


def decode_file(path):
    u = np.fromfile(path, np.uint8)
    if len(u) % 2:
        u = u[:-1]
    q = u.astype(np.float32).reshape(-1, 2)
    z = (q[:, 0] - 127.5) + 1j * (q[:, 1] - 127.5)
    mag = np.abs(z)
    # Find transmitted bursts and ignore the low-level idle samples.
    active = uniform_filter1d((mag > 8).astype(np.float32), 25) > 0.70
    labs, count = label(active)
    candidates = []
    for k in range(1, count + 1):
        idx = np.flatnonzero(labs == k)
        if len(idx) < 1200:
            continue
        result = decode_segment(z, int(idx[0]), int(idx[-1] + 1))
        if result is not None:
            candidates.append((result, int(idx[0]), int(idx[-1] + 1)))
    return max(candidates, key=lambda x: x[0][:4]) if candidates else None


def addresses(payload):
    # Report all byte-aligned Gridstream-looking 0x90xxxxxx node identifiers.
    out = []
    for i in range(max(0, len(payload) - 3)):
        if payload[i] == 0x90:
            out.append((i, payload[i:i + 4].hex().upper()))
    return out


def main():
    paths = sorted(glob.glob("g*_916.15M_250k.cu8"), key=lambda p: int(os.path.basename(p).split("_")[0][1:]))
    rows = []
    decoded = 0
    for num, path in enumerate(paths, 1):
        got = decode_file(path)
        if got is None:
            continue
        result, a, b = got
        score, valid, total, neg_hd, payload, phase, polarity, si, tone0, tone1 = result
        # Require good UART framing and the Gridstream 0x2A lead byte.
        if not payload or payload[0] != 0x2A or valid / total < 0.85:
            continue
        decoded += 1
        rows.append({
            "file": os.path.basename(path), "start": a, "end": b,
            "sync_errors": -neg_hd, "uart_valid": valid, "uart_total": total,
            "tone_low_hz": round(tone0), "tone_high_hz": round(tone1),
            "phase": phase, "polarity": polarity,
            "addresses": ";".join(f"{i}:{addr}" for i, addr in addresses(payload)),
            "hex": payload.hex(" "),
        })
        if num % 100 == 0:
            print(f"processed {num}/{len(paths)} decoded={decoded}", flush=True)

    fields = ["file", "start", "end", "sync_errors", "uart_valid", "uart_total",
              "tone_low_hz", "tone_high_hz", "phase", "polarity", "addresses", "hex"]
    with open("decoded-frames.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    addr_counts = Counter()
    prefixes = Counter()
    frames = Counter()
    for r in rows:
        p = bytes.fromhex(r["hex"])
        for _, addr in addresses(p):
            addr_counts[addr] += 1
        prefixes[p[:6].hex(" ")] += 1
        frames[r["hex"]] += 1
    with open("decoded-summary.txt", "w") as f:
        f.write(f"files={len(paths)}\ndecoded={len(rows)}\nunique_frames={len(frames)}\n\n")
        f.write("Addresses:\n")
        for addr, n in addr_counts.most_common():
            f.write(f"{n:6d}  {addr}\n")
        f.write("\nFrame prefixes (first 6 bytes):\n")
        for prefix, n in prefixes.most_common():
            f.write(f"{n:6d}  {prefix}\n")
        f.write("\nMost common complete frames:\n")
        for frame, n in frames.most_common(30):
            f.write(f"{n:6d}  {frame}\n")
    print(f"done files={len(paths)} decoded={len(rows)} unique={len(frames)}")


if __name__ == "__main__":
    main()
