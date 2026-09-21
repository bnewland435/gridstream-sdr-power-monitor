# Privacy policy

The public-facing name for the subject meter is `METER_ID`.

The repository must not contain:

- the real subject-meter RF identifier or its byte representation;
- neighboring meter or network-node identifiers;
- raw `.cu8`, `.iq`, `.bin`, or packet-capture files;
- precise home location or utility-account information;
- a private mapping from aliases to real identifiers;
- detailed capture times that could reveal household activity.

Aggregate counts, frame-family prefixes, radio parameters, decoder logic, and
non-identifying methodology may be published.

Before any public release, run:

```bash
python scripts/privacy_check.py .
```

For a private local check against one or more known identifiers, supply them
only through an environment variable; never commit the value:

```bash
PRIVATE_METER_IDS='ID1,ID2' python scripts/privacy_check.py .
```
