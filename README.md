# Gridstream SDR Power Monitor

Receive-only research into Landis+Gyr Gridstream RF Generation 5 traffic using
low-cost SDR hardware. The immediate goal is to characterize frame families and
determine whether passively received traffic can support safe, reproducible
electricity-load analysis.

## Current status

- 3,320 narrowband CU8 recordings collected at 916.15 MHz and 250 kS/s.
- 2,325 candidate frames recovered by direct FSK demodulation.
- 2,297 frames passed strict synchronization, UART-framing, and length checks.
- 1,779 strict frames were attributed to the subject meter.
- Six recurring frame families have been observed.
- CRC-16/CCITT initialization `0xD2B8` validates all 1,782 strict frames tested;
  the Puget Sound Energy deployment's reported `0x142A` seed validates none.
- No instantaneous watts or cumulative kWh field has yet been established.

The subject meter is identified only as `METER_ID`. Raw RF captures, actual RF
identifiers, precise location, utility-account information, and detailed
occupancy-linked timestamps are deliberately excluded.

## Reproduce the decoding

The decoder expects files named `g*_916.15M_250k.cu8` in the working directory:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/decode_gridstream.py
```

It writes `decoded-frames.csv` and `decoded-summary.txt`. These generated files
are ignored by Git because they may contain real RF node identifiers.

## Repository layout

- `scripts/` — receive-side decoder and privacy checks
- `docs/` — aggregate findings, methodology, privacy rules, and outreach draft
- `examples/` — schema documentation only; no live RF identifiers

## Scope and ethics

This project is receive-only. It does not transmit to, authenticate with, alter,
or control utility infrastructure. Analysis is limited to over-the-air traffic
received at the research site. See [docs/PRIVACY.md](docs/PRIVACY.md).

The staged technical comparison and researcher-contact sequence is documented
in [docs/COLLABORATION_PLAN.md](docs/COLLABORATION_PLAN.md).
The deployment-specific CRC finding is documented in
[docs/CRC_VARIANT.md](docs/CRC_VARIANT.md).

## Related work

- [`swannman/gridstream-protocol`](https://github.com/swannman/gridstream-protocol)
- [RECESSIM Gridstream protocol notes](https://wiki.recessim.com/view/Landis%2BGyr_GridStream_Protocol)
- [`rtl_433`](https://github.com/merbanan/rtl_433), including the Gridstream decoder

## License

Code is available under the MIT License. Documentation is available under
CC BY 4.0; see [LICENSE-DOCS](LICENSE-DOCS).
