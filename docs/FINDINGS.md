# Findings through capture 3,320

## Dataset

| Measure | Count |
|---|---:|
| CU8 recordings | 3,320 |
| Candidate decodes | 2,325 |
| Strict frames | 2,297 |
| Strict `METER_ID` frames | 1,779 |

Strict acceptance requires zero synchronization errors, valid UART framing for
all recovered bytes, and exact agreement between declared and recovered frame
length.

## Subject-meter frame families

| Prefix | Strict frames | Working description |
|---|---:|---|
| `2A D5 00 11` | 425 | Short traffic |
| `2A D5 00 16` | 815 | Medium traffic |
| `2A D5 00 17` | 188 | Medium traffic |
| `2A D5 00 47` | 66 | Long status frames |
| `2A 55 00 23` | 284 | Beacon/identity-like frames |
| `2A D5 00 1C` | 1 | Unclassified; insufficient evidence |

## Confirmed observations

- The physical layer is consistent with 9,600-symbol/s FSK and approximately
  104.17 microseconds per symbol.
- Direct demodulation recovers the Generation 5 synchronization sequence and
  8N1 UART bytes.
- A fixed source identifier at the expected field offset ties the strict frame
  set to the physical subject meter; that identifier is published only as
  `METER_ID`.
- CRC-16/CCITT with polynomial `0x1021` and initialization `0xD2B8` validates
  all 1,782 strict frames tested. The Washington/PSE initialization `0x142A`
  validates none of them.
- Restoring the omitted `80 FF` sync bytes aligns local frames with the
  Washington reference parser's family lengths and structural field offsets.
- The recurring local `1F 03` sequence is CRC-protected and is not a corrupted
  decoding of the Washington deployment's commonly observed `09 03` sequence.
- The longer status family contains fields consistent with Unix time and an
  uptime counter.
- Narrowband capture observes only a subset of a frequency-hopping network.

## Not yet established

- No payload field has been proven to represent instantaneous watts.
- No payload field has been proven to represent cumulative kWh.
- Apparent correlations require controlled-load trials and validation against
  an independent reference measurement.

These limits are intentional: field roles are not assigned from visual pattern
matching alone.
