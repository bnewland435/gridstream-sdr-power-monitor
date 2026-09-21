# Deployment-specific CRC initialization

## Result

The strict frames in this dataset use CRC-16/CCITT with polynomial `0x1021`
and initialization value **`0xD2B8`**. This differs from the `0x142A`
initialization reported for the Puget Sound Energy deployment in Woodinville,
Washington.

Across the available decoded-frame tables:

| CRC initialization | Strict frames validated |
|---|---:|
| `0xD2B8` | 1,782 / 1,782 |
| `0x142A` | 0 / 1,782 |

CRC bytes are interpreted in big-endian order. Coverage begins with the CI byte
and ends immediately before the final two CRC bytes. The outer `80 FF 2A`
synchronization, type byte, reserved byte, and length byte are outside CRC
coverage for these `0x55`/`0xD5` families.

## Frame normalization

The local direct-demodulation output begins with `2A`; the Washington reference
parser expects `80 FF 2A`. Prepending `80 FF` makes the local frames align with
the reference parser's family lengths, address locations, timestamps, counters,
and payload layouts.

## Interpretation

One CRC seed validating every strict frame while the comparison seed validates
none is strong independent confirmation that:

- the direct demodulator is recovering coherent packet bytes;
- the final two bytes are the expected CRC field;
- CRC initialization is deployment-specific or provisioned differently; and
- recurring local values such as `1F 03` are authentic CRC-protected protocol
  data rather than corrupted instances of the Washington deployment's `09 03`.

The public repository does not include the source frames because they contain
live RF identifiers. The included `find_crc_init.py` script allows the test to
be repeated against a private decoded-frame CSV.
