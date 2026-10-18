# D-MASON dependency and identity qualification

The exact DMASON-3.2.zip asset named by OpenABL's dependency Makefile was recovered
from its [alpha3 release](https://github.com/OpenABL/OpenABL/releases/tag/v0.0.1alpha3).
Its 164,419,036 bytes hash to
`96cc3453709bc9c48a16e12bcbc68f54c4e52dcdbabe7edcd15b1243f74f8af7`.
The bundle compiles the generated Sugarscape backend under Java 17. Native
250-cell execution exits successfully; this alone does not verify every worker.

The released launcher calls `System.exit(0)` from each worker. A separate observer
control waits for both worker threads before exiting and records owned cell
fields at initialization and completion. Both partitions reach 400 scheduler
steps, corresponding to 100 four-stage model steps.

| Requested cells | Initial unique positions | Final field records | Final unique positions |
| --- | ---: | ---: | ---: |
| 250, native identity | 225 | 375 | 225 |
| 4,000, native identity | 3,969 | 4,999 | 3,969 |
| 4,000, hash control | 3,969 | 3,969 | 3,969 |

The generated `RemoteAgent` overrides `equals` using identity and position but
omits `hashCode`. A diagnostic override using `Objects.hash(id,pos)` removes the
duplicate-position census in the larger condition. Repeated records in the
native census agree in their recorded state fields. This is evidence about
field identity and representation, not proof that scientific outcomes changed.
Random initial states differ across executions; no paired numerical equivalence
is claimed. Both source patches remain explicit, and native outputs are retained.

State range and resource bounds pass for all recorded cells. Model dynamics,
initialization RNG, cross-partition behavior and large-scale timings still need
independent validation. The paper's million-cell, 1,000-step, 2–128-core scaling
experiment has not been reproduced or replaced by these small qualifications.

The archive retains generated Java, compiled classes, observers and all execution
logs. Every member was compared byte-for-byte with the retained native file.
The large dependency bundle is identified by its source URL and checksum rather
than duplicated in Git. Three study completions remain unchanged.
