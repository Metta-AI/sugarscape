# Lima and Aguiar (2024)

“Towards a Docker-based architecture for open multi-agent systems,” IAES International Journal of Artificial Intelligence 13(1), 45–56. [Paper](https://doi.org/10.11591/ijai.v13.i1.pp45-56); [author code](https://github.com/GustavoLLima/open_mas_docker_opt).

Status: completed qualified author-code feasibility reproduction. [The claim-level audit](results/claim-audit-2026-10-18) verifies all six original protocol requirements. This is not an independent engine replication or proof of historical binary equivalence. Earlier sections retain their dated partial assessments.

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
Preparation, all nine image builds, native execution, collection and both auditors
have passed, as documented below. This workflow covers the container scenario;
host-GUI execution and visual confirmation remain separate requirements.

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

### Portable container workflow verified end to end

[The completed fresh execution](results/portable-container-complete-2026-10-18)
passes preparation, nine-image build, native execution, automatic collection and
both independent audits. Both NetLogo models complete all 1,000 ordered steps.
All 883 router deliveries reconcile, and all 799 identities are accounted for:
246 model-1 survivors, 245 model-2 survivors, 307 queued agents and one active miner.
Eleven JaCaMo creations reconstruct incoming attributes; ten agents return.

Collection preserves every backed-up native file and leaves all containers
stopped. Fresh extraction of the public archive reproduces both audits
byte-for-byte. The archive includes the frozen executed harness, including its
original `run_container.py` filename, so the subsequent shared-runner refactor
is not silently substituted into this evidence. Host execution and visual GUI
confirmation remain separate; this does not complete the paper.

### Portable host execution verified

[The completed host workflow](results/portable-host-complete-2026-10-18) verifies
both 1,000-step trajectories, 1,019 exact router deliveries and conservation of
all 799 identities: 249 model-1 survivors, 235 model-2 survivors, 314 queued
agents and one active miner. Eleven native creations match incoming attributes;
ten return records remain. Both audits reproduce byte-for-byte from a fresh
public extraction, and the owned host processes and containers are stopped.

The GUI-enabled model logs successful world creation without an initialization
exception. The UI tool lists JaCaMoLauncher but cannot select it by either name
or reported bundle identifier. This establishes no visible-rendering result.
The host-native execution is validated; the GUI observation requirement remains open.

### Runnable saved-agent control

In another fresh prepared container directory, supply the exact retained
`agent-399-input.asl` checkpoint. `prepare_reload.py` checks its frozen SHA-256,
excludes identity 399 from model-1 registration, and writes the explicit initial
checkpoint fixture. The input remains in external evidence because it contains
the author's AgentSpeak plans; its required hash is in the frozen protocol.

```sh
python replications/lima_2024/prepare_reload.py /new/control /retained/agent-399-input.asl
docker compose -f /new/control/compose.json build
python replications/lima_2024/run_scenario.py /new/control --reload
python replications/lima_2024/collect_completed.py /new/control /new/control/collection
cp /new/control/collection/snapshot-final.jsonl /new/control/snapshot-final.jsonl
python replications/lima_2024/audit_snapshot.py /new/control/snapshot-final.jsonl /new/control/snapshot-audit.json --initial-checkpoints /new/control/initial-checkpoints.json
python replications/lima_2024/audit_native.py /new/control /new/control/native-audit.json --initial-checkpoints /new/control/initial-checkpoints.json
python replications/lima_2024/audit_reload.py /new/control /new/control/reload-audit.json --native-log native.log --reexport shared_volume/jacamo/jacamo_model/src/agt/list/399.asl
```

The runner first starts cleanup, database and API, verifies cleanup completion,
then installs the checkpoint and seeds the database. Remaining services start
without restarting dependencies. [Preparation evidence](results/portable-reload-preparation-2026-10-18)
checks the same source substitution and nine image builds. Re-auditing the prior
control preserves every metric, including its failed score criterion. The fresh
control is complete; its results follow below.

### Portable saved-agent control completed

[The completed control](results/portable-reload-complete-2026-10-18) verifies
both 1,000-step trajectories and 953 exact router deliveries. All 799 identities
remain accounted for: 238 model-1 survivors, 245 model-2 survivors, 315 queued
agents and one active miner. Twelve native creations match incoming attributes;
eleven agents return. Collection leaves all containers stopped.

The checkpoint preserves its retained belief and all 39 plans. Its saved
departure trigger again causes reexport without a mining completion: score
remains 1, failing the declared increment-to-2 criterion. This repeats the
first control's discrepancy, without establishing a whole-paper negative result.

Fresh public-archive extraction reproduces the snapshot and native audits
byte-for-byte. Author AgentSpeak input and reexport remain external; the
reload audit records their hashes. Visible host-GUI validation and historical
runtime fidelity remain unresolved. This study is not counted as completed.

### Native GUI observed

[Window evidence](results/host-gui-observation-2026-10-18) captures the actual
JaCaMo Mining World during a fresh, isolated host scenario. Two screenshots
show the agent at different grid positions, gold cells, the speed control and
the collected-gold counter. The capture targets window 3082, owned by Java
process 95799; retained parent-process provenance connects it to this run's
Gradle launcher. No interface input was injected.

This resolves the earlier native-window observation gap without manual user
assistance. It does not yet establish completion of this new scenario: its
1000-step trajectories and state-transfer reconciliation remain under execution
and audit. Earlier completed scenarios and their evidence remain unchanged.
Historical revision and dependency equivalence also remain unproven.

### Historical lifecycle cross-check

[The October-2022 citation-date source audit](results/historical-lifecycle-2026-10-18)
finds the same save-and-depart trigger in the earlier miner. The paper claims
restored information, not a second mining score. The additional score criterion
remains failed, but does not independently contradict that published claim.
Complete historical runtime equivalence remains unproven.

### Native NetLogo creation reconciliation

[All three completed portable scenarios](results/native-creation-reconciliation-2026-10-18)
pass the strengthened auditor: 4,282 native creation records match consumed
database identities, incoming attributes and paths. Existing trajectory and
conservation checks also pass. The incoming sugar tuple is observed; newly
randomized sugar remains source-supported, not directly printed. Paper page 51
explicitly specifies that sugar adaptation.

### Complete visually observed host scenario

[The fresh GUI scenario](results/host-visual-complete-2026-10-18) now completes
both 1,000-step trajectories. All 934 deliveries reconcile; native logs verify
1,423 NetLogo creations and 11 JaCaMo creations. All 799 identities are conserved
once at shutdown. The 36-file archive includes the observed window, native logs
and auditors; both audit reports reproduce byte-for-byte after fresh extraction.
The owned host processes and containers are stopped. Historical dependency
equivalence remains unproven; no additional completed-study credit is assigned.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/363175bde20af32cda1530af8f95bf7809f57c43/replications/lima_2024/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show 363175bde20af32cda1530af8f95bf7809f57c43:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.
