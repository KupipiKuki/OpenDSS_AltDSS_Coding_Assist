# IEEE 34-node feeder, Mod 1 fixture provenance

- **Upstream commit** `3b208397160213cae4a9e2d0a7d1aa3528ce26e1` (2024-06-24)
- **Retrieved** 2026-11-22
- **License** BSD-3-Clause
- **Copyright** (c) 2018-2024, DSS-Extensions contributors
- **Copyright** (c) 2008-2024, Electric Power Research Institute, Inc.

The files retain the upstream directory structure, filename case, and bytes. Both fixtures share the original license notice. [Pinned upstream repository](https://github.com/dss-extensions/electricdss-tst/tree/3b208397160213cae4a9e2d0a7d1aa3528ce26e1) · [License notice](../License.txt)

| Upstream path | Fixture path | Bytes | SHA-256 |
|---|---|---:|---|
| `License.txt` | `../License.txt` | 1816 | `f13543277f32a6437d4f583200858f0988d3acc9598a6a1a292d710009ec21ef` |
| `Version8/Distrib/IEEETestCases/IEEELineCodes.DSS` | `IEEETestCases/IEEELineCodes.DSS` | 12032 | `71bc16ef9c6084b9e3bab74fbdf967080b79624683465e1483b787ff160f58b3` |
| `Version8/Distrib/IEEETestCases/34Bus/ieee34Mod1.dss` | `IEEETestCases/34Bus/ieee34Mod1.dss` | 14341 | `648f12f7f611ccf89bce68aea2142f0225ddcba78e81d16bd02e52e3a4b058f8` |
| `Version8/Distrib/IEEETestCases/34Bus/IEEELineCodes.DSS` | `IEEETestCases/34Bus/IEEELineCodes.DSS` | 30 | `40ef533dfcb22738edb1125b1e15e4a1a5d41b2cca4a2f969f5d955c9784daeb` |
| `Version8/Distrib/IEEETestCases/34Bus/IEEE34_BusXY.csv` | `IEEETestCases/34Bus/IEEE34_BusXY.csv` | 506 | `6e022bbb3adb3c7f29ccb7bbdee2013517ae55e19ad25cda815616c5d4a37958` |

## Deliberately omitted upstream files

| Upstream path | Reason |
|---|---|
| `34Bus/Run_IEEE34Mod1.dss` | Plot commands require a display and the driver compiles the feeder twice with forced regulator taps. |
| `34Bus/Run_IEEE34Mod2.dss` | Plot-bearing driver for the alternate feeder variant. |
| `34Bus/ieee34Mod2.dss` | Alternate model reserved for a later scenario. |
| `34Bus/nmsu_linecode2_ABC.txt` | Neither fixture circuit references this auxiliary file. |
