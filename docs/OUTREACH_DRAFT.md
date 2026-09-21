# Researcher outreach draft

Subject: Independent Gridstream Gen-5 SDR dataset and decoder results

Hello,

We have been independently collecting and decoding receive-only Landis+Gyr
Gridstream RF Generation 5 traffic with an RTL-SDR-class receiver. Our current
dataset contains 3,320 narrowband CU8 recordings, producing 2,297 strict frames
and six recurring subject-meter frame families.

In comparing our strict frames with your reference parser, restoring the outer
`80 FF` sync bytes aligned the family lengths and field offsets. We also found
that CRC-16/CCITT initialization `0xD2B8` validates all 1,782 strict frames in
the available decoded-frame tables, while the PSE initialization `0x142A`
validates none. Our deployment also carries a recurring CRC-protected `1F 03`
sequence where the PSE documentation commonly shows `09 03`.

We have published a sanitized methodology, decoder, and aggregate results here:

`REPOSITORY_URL`

The fixed meter address and other live RF identifiers have been removed. Raw
captures remain private pending privacy review. We would particularly value
comparison with your parser and dataset, advice on whether CRC initialization
is provisioned per deployment, and any insight into the `1F 03` versus `09 03`
variation and observed `D5`/`55` families. We have not yet established an
instantaneous-watts or cumulative-kWh field and do not want to overstate the
evidence.

Would you be interested in comparing results or suggesting a minimal sanitized
sample format that would be useful for collaborative analysis?

Thank you.

---

This is a draft. Replace `REPOSITORY_URL`, select the appropriate recipient,
and obtain final approval before posting or sending it.
