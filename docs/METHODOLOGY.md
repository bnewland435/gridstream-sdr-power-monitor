# Methodology

## Capture

- Receive-only RTL-SDR-class hardware
- Center frequency: 916.15 MHz
- Sample rate: 250 kS/s
- Sample format: unsigned 8-bit interleaved I/Q (CU8)
- Short, numbered captures named `g*_916.15M_250k.cu8`

## Decoder

The decoder detects active bursts, calculates phase difference, smooths the
instantaneous-frequency estimate, separates the two FSK tones, and searches
sampling phase and polarity for the Generation 5 synchronization sequence.
Recovered bits are decoded as 8N1 UART bytes.

Candidate scoring favors valid UART frames and expected Gridstream lead bytes.
Scientific analysis applies stricter criteria after decoding: zero sync errors,
fully valid UART framing, and exact declared-length agreement.

## Interpretation discipline

Packet structure is inferred only when repeated frames support the same field
offset and semantics. Energy-related fields require controlled changes in load,
repeatability, and comparison with an independent power measurement. Unknown
fields remain unknown.

## Reproducibility limits

Raw captures are not public because they contain live RF node identifiers and
potentially time-linked household information. Sanitized, minimal examples may
be added after deterministic pseudonymization and a second privacy review.
