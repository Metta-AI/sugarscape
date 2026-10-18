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

## Complete container scenario

[Native evidence and audits](results/container-complete-2026-10-18) verify both
NetLogo trajectories: ticks 0–999 in order, with final-output markers. Every one
of 799 registered agents is accounted for exactly once at shutdown: 243 model-1
survivors, 240 model-2 survivors, 315 queued agents and one active miner.
All 1,013 router deliveries match their destination records. All 12 JaCaMo
creation messages reconstruct the exact incoming identity, history, sugar,
metabolism and vision; 11 agents returned from JaCaMo.

The dashboard was opened at `http://127.0.0.1:20080/dashboard/` using the named
agent-browser session `sugarscape-lima-001`. Searching model 1 for agent 399 and
clicking its file button displayed the exported 9,491-byte AgentSpeak file
exactly. Its hash and a screenshot are retained. Empty database ASL-path fields
do not mean the separately stored file is absent.

The host-GUI scenario remains separate and incomplete. AgentSpeak file reload
after a return to JaCaMo is also unvalidated: this run's 12 creations all used
the default file. These observations do not complete the paper.

Extract `native-evidence.tar.gz` to a fresh directory, then run both auditors:

```sh
python replications/lima_2024/audit_snapshot.py /run/snapshot-final.jsonl /new/snapshot-audit.json
python replications/lima_2024/audit_native.py /run /new/native-audit.json
```
