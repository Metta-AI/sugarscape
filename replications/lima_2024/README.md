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

## Host scenario and entry-state fidelity

[Host preparation evidence](results/host-runtime-2026-10-18) records a successful
Java 15.0.2 / Gradle 7.4.2 compilation. Three exact source substitutions enable
the original GUI flag and use isolated loopback API port 25001. Hash checks
verify that these are the only changes in those source files. The separate
host scenario is running; compilation and process startup do not prove completion.
The UI automation tool lists JaCaMoLauncher but cannot select it by name or bundle
identifier, so visual confirmation remains outstanding.

The original NetLogo entry procedure deliberately redraws sugar in 5–25, while
copying incoming metabolism and vision. Incoming sugar remains accessible in
the API history. Our exact-delivery audit therefore covers the transported data,
not unchanged native sugar. The paper permits adaptation on entry; this source
finding alone does not establish a failed replication.

## Complete host-native trajectories

[The host-scenario evidence](results/host-native-complete-2026-10-18) verifies
both 1,000-step NetLogo trajectories with JaCaMo running outside Docker.
All 942 router deliveries reconcile. Every registered identity is accounted
for once: 244 model-1 survivors, 251 model-2 survivors, 303 queued agents and
one active miner. Twelve native JaCaMo creations match incoming attributes;
eleven agents returned. No incomplete transfer is counted as a completed one.

The GUI flag was enabled, but the UI tool could not select the Java application.
Visual GUI confirmation and native AgentSpeak reload remain outstanding. This
is not a completed-paper verdict.

After extracting the host archive, pass `--jacamo-log jacamo-host.log` to
`audit_native.py`; the host log is separate from Docker's service logs.

## Checkpoint reentry control

`reload-control-protocol.json` was frozen before execution. A separate full
architecture run relocates agent 399 into JaCaMo's initial queue with its saved
AgentSpeak file. Model 1 omits that identity from registration, preserving unique
IDs and the total of 799 agents. Both NetLogo trajectories still require 1,000
steps. The control must verify native file selection, retained beliefs and plans,
a second export, and final conservation. It supplements the original scenarios;
it does not establish a natural repeat visit under their original scheduling.

### First observed reload event

[The retained control event](results/reload-first-event-2026-10-18) confirms
that native JaCaMo selects `list/399.asl`, preserves the previous random belief,
and exports all 39 saved plans again. Plan text matches after removing only the
additional saved-file URL annotation. Both file hashes and the native log are
retained; the full generated AgentSpeak files remain in external run evidence.

The predeclared score-increment criterion **fails**: score remains 1, not 2.
The saved file contains `initial_print1`, whose initial-belief event invokes
the departure plan immediately on reload. Native logs show export and departure
without another mining completion. This behavior comes from the unmodified
author agent program, not a replication patch. It demonstrates file persistence
with a lifecycle caveat; it is not a whole-paper negative verdict. The full
control trajectories and final conservation audit are still pending.

### Complete reload-control trajectories

[The complete control evidence](results/reload-complete-2026-10-18) verifies
both 1,000-step NetLogo trajectories and 944 exact router deliveries. All 799
identities are accounted for once: 261 model-1 survivors, 242 model-2 survivors,
295 queued agents and one active miner. Thirteen JaCaMo creations reconstruct
their incoming attributes, and twelve return records are retained. The failed
score-increment criterion remains failed.

The auditors now accept explicit checkpoint records. Each must match an actual
initial database row in all declared fields; it contributes one initial identity
and is excluded from subsequent-delivery counts. Agent 399's fixture follows
the frozen protocol and executed seed SQL. It is not a new router delivery.
The default original-scenario audits still use only fresh registration records.

Extract the control archive and pass `--initial-checkpoints /run/initial-checkpoints.json`
to both `audit_snapshot.py` and `audit_native.py`.

## Packaged host attempt and collection failure

[Retained evidence](results/packaged-host-collection-failure-2026-10-18) records
a separate signed macOS application attempt. Both NetLogo processes exited zero,
and the database reconciles 969 router deliveries. Visual GUI confirmation remains
unavailable. Process exits alone do not establish complete trajectories.

The collector mistakenly used `docker compose start db`, which also restarted
the author's `clear_files` dependency. It deleted this attempt's trajectory,
survivor and exported AgentSpeak files before they were archived. Consequently,
this attempt receives no full-trajectory credit. Its surviving database and logs
are retained; earlier published scenario archives remain intact.

`collect_completed.py` now backs up native files before accessing the database,
starts its existing container directly, and verifies unchanged native hashes.
The complete collection workflow was exercised against the earlier host run:
all 15 native files remained unchanged, its snapshot matched the previous capture
byte-for-byte, and all containers were stopped afterward. The backup can contain
author-generated AgentSpeak code and should remain external to the public PR.

```sh
python replications/lima_2024/collect_completed.py /completed/run /new/collection
```

## Runnable container workflow

Requirements: Docker Compose, Git, Python 3.10 or later, and Pydantic 2 for the
auditors. Supply a clean author checkout at the revision in `source-pins.json`
and the official [NetLogo 6.0.4 archive](https://downloads.netlogo.org/6.0.4/NetLogo-6.0.4-64.tgz).
Preparation verifies both source hashes and the archive checksum. It copies
source into a fresh run directory and changes no model rules. The replacement
NetLogo Dockerfile matches the qualified runtime; other author dependencies
remain historically unpinned, so fresh builds need their own runtime evidence.

```sh
python replications/lima_2024/prepare_container.py /author/checkout /downloads/NetLogo-6.0.4-64.tgz /new/run --project sugarscape-lima-replay-001
docker compose -f /new/run/compose.json build
python replications/lima_2024/run_scenario.py /new/run
python replications/lima_2024/collect_completed.py /new/run /new/run/collection
cp /new/run/collection/snapshot-final.jsonl /new/run/snapshot-final.jsonl
python replications/lima_2024/audit_snapshot.py /new/run/snapshot-final.jsonl /new/run/snapshot-audit.json
python replications/lima_2024/audit_native.py /new/run /new/run/native-audit.json
```

The default port offset is 20,000; choose another with `--port-offset` when
occupied. The runner refuses existing project containers, stops its own services
within the one-hour protocol bound, and retains terminal states and logs.
Preparation and all nine image builds have passed. A fresh complete execution
with automatic collection and both auditors is in progress; no result is claimed
until those audits pass. This workflow covers the container scenario, while the
host-GUI setup and visual confirmation remain separate requirements.

### Host-JaCaMo workflow

Prepare a separate fresh directory with `prepare_container.py`, a unique project,
and a free port offset. Before building or launching it, run:

```sh
python replications/lima_2024/prepare_host.py /new/host-run --java-home /jdk15/Contents/Home --gradle-home /gradle-7.4.2 --gradle-cache /external/gradle-cache
docker compose -f /new/host-run/compose.json build
python replications/lima_2024/run_scenario.py /new/host-run --host
python replications/lima_2024/collect_completed.py /new/host-run /new/host-run/collection
cp /new/host-run/collection/snapshot-final.jsonl /new/host-run/snapshot-final.jsonl
python replications/lima_2024/audit_snapshot.py /new/host-run/snapshot-final.jsonl /new/host-run/snapshot-audit.json
python replications/lima_2024/audit_native.py /new/host-run /new/host-run/native-audit.json --jacamo-log jacamo-host.log
```

`prepare_host.py` verifies Java 15.0.2+7 and Gradle 7.4.2, removes the JaCaMo
container, enables the original GUI flag and redirects its two API callers to
the configured loopback port. It checks original source hashes before applying
the three substitutions, records resulting hashes, and compiles the model.
The shared runner launches host JaCaMo and stops its process group at termination.

[Preparation evidence](results/portable-host-preparation-2026-10-18) verifies
successful compilation and eight image builds. All three adaptations match the
earlier host run exactly. Full execution is queued behind the container validation;
compilation alone establishes neither native trajectories nor visible GUI behavior.
