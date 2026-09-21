# Collaboration plan

## Phase 1: private validation

1. Convert a small set of strict local frames into the line-oriented hex format
   accepted by `swannman/gridstream-protocol` by restoring the omitted `80 FF`
   sync bytes.
2. Run `tools/gridstream_parser.py` on individual frames. Initial comparison
   confirms matching family lengths and field positions.
3. Compare CRC parameters. This identified local initialization `0xD2B8`, which
   validates 1,782/1,782 strict frames, versus 0/1,782 for PSE's `0x142A`.
4. Run the remaining protocol-document checks against a private normalized log.
5. Record agreements and disagreements in field boundaries, CRC treatment,
   frame-family labels, timestamps, and counters.
6. Keep all original identifiers and raw captures outside Git.

The comparison confirms that our decoder emits frames beginning with the
recovered Gridstream `0x2A` lead byte while the reference parser includes
`80 FF` before `2A`. This normalization is structural only and does not alter
the CRC-covered body.

## Phase 2: sanitized publication

1. Produce a deterministic pseudonymization scheme that preserves repeated
   address relationships without exposing live identifiers.
2. Recalculate any checksum affected by pseudonymization, or clearly mark the
   example as structural rather than checksum-valid.
3. Publish only the minimum examples needed to reproduce a finding.
4. Run the repository privacy check with the private identifier list.
5. Manually review Git history, not merely the working tree.

## Phase 3: researcher contact

1. Ask the `swannman/gridstream-protocol` maintainer whether our recovered
   `0x2A`-leading frames map directly to their parser input after outer framing
   is restored or normalized.
2. Share aggregate family counts and the decoder methodology.
3. Ask what sanitized sample format would be most useful.
4. Contact RECESSIM and `rtl_433` maintainers after incorporating the first
   round of protocol feedback.

No outreach should attach unsanitized captures or identifiers.
