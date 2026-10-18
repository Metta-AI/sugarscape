# Lima and Aguiar (2024)

“Towards a Docker-based architecture for open multi-agent systems,” IAES International Journal of Artificial Intelligence 13(1), 45–56. [Paper](https://doi.org/10.11591/ijai.v13.i1.pp45-56); [author code](https://github.com/GustavoLLima/open_mas_docker_opt).

Status: runtime qualification in progress. No replication credit is claimed.

The architecture connects two NetLogo Sugarscape models and a JaCaMo Gold Miners model through registration, routing, persistence and reporting services. Both container-only and host-GUI scenarios are required. `protocol.json` freezes observations and execution bounds. The study tests feasibility and state transfer; it invents no numerical benchmark target.

`source-pins.json` identifies the last commit before acceptance and hashes inspected files. This does not authenticate the authors’ experiment revision. Implementation code remains external.

`dependency-probe.json` records the unavailable original `openjdk:8-jdk` image manifest; the Gradle manifest resolves. Any repaired execution must disclose replacements and preserve NetLogo 6.0.4 and Java 8. Released experiments stop at 1,000 steps, while the paper describes indefinite operation. Historical dependency digests and random seeds remain unknown.

## Runtime recovery

[Build evidence](results/runtime-build-2026-10-18) records a successful Linux/amd64
NetLogo image build and Java/Python version output. The original distribution URL
redirects to 404; the official archive supplies the same NetLogo version.
The replacement base is pinned by digest. Historical dependency equivalence is
unproven, and the changed runtime is explicitly recorded.

The isolated container scenario retains all nine author services and unmodified
model source. Its private project uses loopback ports and fresh data, with a
7.5 GiB aggregate container-memory limit and a one-hour execution deadline.
Service startup alone does not validate model execution or agent transfer.

## First native transfer snapshot

[The consistent database snapshot](results/native-snapshot-2026-10-18) contains
2,142 rows. Independent reconciliation matches all 665 processed router deliveries
to destination records, including identity, data, history and ASL-path strings.
Two return records originate from JaCaMo. Its file-watcher exception did not stop
startup: the native Gold Miners model subsequently created and processed agents.

Initialization registers 799 unique agents: 399 in model 1 and 400 in model 2.
The released API uses Python's exclusive upper range bound; the model requests
IDs 1–399 and 400–799. This is observed source behavior, not an adjusted population.
There are 220 queued JaCaMo records, eight queued model-2 records and 13 router
records awaiting processing at this snapshot. These are unfinished transfers.

All ASL-path fields in this snapshot are empty, so matching them establishes no
file-payload preservation. Native attribute reconstruction, complete 1,000-step
runs, dashboard observation and the host-GUI scenario remain unvalidated.

```sh
python replications/lima_2024/audit_snapshot.py \
  replications/lima_2024/results/native-snapshot-2026-10-18/snapshot-001.jsonl \
  /new/audit.json
```
