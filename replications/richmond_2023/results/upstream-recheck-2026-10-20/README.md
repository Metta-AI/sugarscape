# Later upstream source check

The author repository's release named `spe-publication` uses tag `v1`, already pinned by this study.
It does not identify a different model source.
The inspected master revision `f27414d0230fe7d7d9a5db4ca813da9d0b845a2c` is two commits ahead.
Its only changed file relative to `v1` is `CMakeLists.txt`, upgrading the engine from `v2.0.0-rc` to `v2.0.0-rc.1`.
Both complete `src/main.cu` files have SHA-256 `b2daf9e6ee2b3faf4a13e30ba19f4293e1f922a993d30cb5e72fb1d4c2b8f56d`.
Thus this later revision does not supply source corrections for the model-rule differences under investigation.

The upgrade commit cites a telemetry bug that reports submodel and individual ensemble runs separately, with potential runtime impact.
This is an author-reported reason for the update; no new runtime measurement or engine-level parity is established here.
The historical engine remains pinned, and instrumented control timings remain excluded from performance claims.

Sources:

- [Publication release](https://github.com/FLAMEGPU/FLAMEGPU2-submodel-benchmark/releases/tag/v1)
- [Exact source comparison](https://github.com/FLAMEGPU/FLAMEGPU2-submodel-benchmark/compare/290702073492677f2fc9164419e9d5900d119e02...f27414d0230fe7d7d9a5db4ca813da9d0b845a2c)
- [Telemetry issue](https://github.com/FLAMEGPU/FLAMEGPU2/issues/1079)

Complete API receipts and both downloaded source files remain in `richmond-upstream-recheck-20261020-001` retained evidence.
An initial lookup treated the issue number as a pull request and returned 404; the corrected issue endpoint succeeded.
No native execution or completed-study credit follows from this source check.
