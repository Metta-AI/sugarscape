# Lima and Aguiar (2024)

“Towards a Docker-based architecture for open multi-agent systems,” IAES International Journal of Artificial Intelligence 13(1), 45–56. [Paper](https://doi.org/10.11591/ijai.v13.i1.pp45-56); [author code](https://github.com/GustavoLLima/open_mas_docker_opt).

Status: source audit only. No simulation has run; no replication credit is claimed.

The architecture connects two NetLogo Sugarscape models and a JaCaMo Gold Miners model through registration, routing, persistence and reporting services. Both container-only and host-GUI scenarios are required. `protocol.json` freezes observations and execution bounds. The study tests feasibility and state transfer; it invents no numerical benchmark target.

`source-pins.json` identifies the last commit before acceptance and hashes inspected files. This does not authenticate the authors’ experiment revision. Implementation code remains external.

`dependency-probe.json` records the unavailable original `openjdk:8-jdk` image manifest; the Gradle manifest resolves. Any repaired execution must disclose replacements and preserve NetLogo 6.0.4 and Java 8. Released experiments stop at 1,000 steps, while the paper describes indefinite operation. Historical dependency digests and random seeds remain unknown.
