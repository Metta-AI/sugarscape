"""Independently audit complete native exports and the frozen statistical targets."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runs", type=Path, nargs="+")
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--allow-prefix", action="store_true")
args = parser.parse_args()
assets = Path(__file__).resolve().parent
protocol = json.loads((assets / "ensemble-protocol.json").read_text())
pins = json.loads((assets / "source-manifest.json").read_text())["source_sha256"]
results = []
indices = set()
scenarios = set()
provenance = []
for root in args.runs:
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["protocol"] == protocol and manifest["source_sha256"] == pins
    assert manifest["compiler"] == "8.4.4"
    assert (
        hashlib.sha256((root / "run_ensemble.py").read_bytes()).hexdigest()
        == manifest["runner_sha256"]
    )
    scenario_name = manifest["scenario"]
    scenarios.add(scenario_name)
    assert len(scenarios) == 1, "Audit each scenario separately"
    scenario = protocol["scenarios"][scenario_name]
    start, stop = manifest["interval"]
    ledger = (root / "completed.jsonl").read_bytes()
    assert ledger.endswith(b"\n")
    records = [json.loads(line) for line in ledger.splitlines()]
    assert 0 < len(records) <= stop - start
    assert [row["index"] for row in records] == list(range(start, start + len(records)))
    if not args.allow_prefix:
        assert len(records) == stop - start
        assert json.loads((root / "complete.json").read_text()) == {
            "completed_runs": stop - start
        }
    provenance.append(
        {
            "root": str(root.resolve()),
            "manifest_sha256": hashlib.sha256(
                (root / "manifest.json").read_bytes()
            ).hexdigest(),
            "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
            "binary_sha256": manifest["binary_sha256"],
        }
    )
    for record in records:
        index = record["index"]
        assert index not in indices, "Repeated seed index must not inflate sample size"
        indices.add(index)
        seed = protocol["seeds"][index]
        assert seed == record["seed"] and scenario_name == record["scenario"]
        folder = root / f"{index:03d}-{seed}"
        for name, digest in record["files_sha256"].items():
            assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
        command = json.loads((folder / "command.json").read_text())
        assert command[:6] == [
            manifest["binary"],
            "-s",
            scenario["native_name"],
            "-f",
            str(scenario["steps"]),
            "-o",
        ]
        assert (
            Path(command[6]).name == "dynamics.m"
            and Path(command[6]).parent.name == folder.name
        )
        assert command[7:] == ["-r", str(seed)]
        assert json.loads((folder / "exit.json").read_text()) == {"exit_code": 0}
        raw = (folder / "dynamics.m").read_bytes()
        assert gzip.decompress((folder / "dynamics.m.gz").read_bytes()) == raw
        text = raw.decode()
        assert text.startswith("clear;\ndynamics = {\n") and text.endswith("};\n")
        body = text.removeprefix("clear;\ndynamics = {\n").removesuffix("};\n")
        blocks = re.findall(r"^\{ (\d+),\n(.*?)^\}\n", body, re.M | re.S)
        assert "".join(f"{{ {t},\n{rows}}}\n" for t, rows in blocks) == body
        assert [int(t) for t, _ in blocks] == list(range(1, scenario["steps"] + 1))
        populations = []
        for t, rows in blocks:
            agents = set()
            sugar = []
            prices = []
            for line in rows.splitlines():
                match = re.fullmatch(
                    r"\[(\d+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), ([^,]+), "
                    r"\{\[([01,]*)\]\}, \{\[([^\]]*)\]\}\], ",
                    line,
                )
                assert match, line
                agent_id = int(match[1])
                assert agent_id not in agents
                agents.add(agent_id)
                assert np.isfinite([float(match[x]) for x in range(2, 8)]).all()
                sugar.append(float(match[3]))
                if match[9]:
                    assert match[9].endswith(",")
                    trades = np.array([float(x) for x in match[9][:-1].split(",")])
                    assert len(trades) % 3 == 0 and np.isfinite(trades).all()
                    prices.extend(trades[::3].tolist())
            populations.append(len(agents))
        assert len(blocks) == record["steps"]
        assert sum(populations) == record["agent_observations"]
        assert populations[-1] == record["final_population"]
        row = {
            "index": index,
            "seed": seed,
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "steps": len(blocks),
            "agent_observations": sum(populations),
            "populations": populations,
            "final_sugar": sugar,
            "final_trade_prices": prices,
            "status": "defined",
        }
        if scenario_name == "carrying":
            values = np.array(populations[100:], dtype=float)
            assert len(values) == 300
            row["statistics"] = {
                "population_mean": float(values.mean()),
                "population_sample_variance": float(values.var(ddof=1)),
                "population_sample_std": float(values.std(ddof=1)),
            }
        elif scenario_name == "wealth":
            values = np.sort(np.array(sugar))
            n = len(values)
            assert n > 1 and values.sum() > 0 and values.var() > 0
            gini = float(
                2 * np.sum(np.arange(1, n + 1) * values) / (n * values.sum())
                - (n + 1) / n
            )
            pairwise = float(
                np.abs(values[:, None] - values[None, :]).sum() / (2 * n * values.sum())
            )
            assert abs(gini - pairwise) < 1e-12
            row["statistics"] = {
                "gini": gini,
                "skewness": float(stats.skew(values, bias=True)),
                "kurtosis": float(stats.kurtosis(values, fisher=True, bias=True)),
            }
        elif len(prices) < 2:
            row["status"] = "undefined_fewer_than_two_prices"
            row["source_std_convention"] = 0
            row["statistics"] = {}
        else:
            row["statistics"] = {"price_sample_std": float(np.std(prices, ddof=1))}
        results.append(row)
complete = indices == set(range(100))
assert args.allow_prefix or complete, "All100 distinct seeds required"
comparisons = []
if complete and all(row["status"] == "defined" for row in results):
    targets = (
        {"population_mean": [204, 210]}
        if scenario_name == "carrying"
        else {key: [value] for key, value in scenario["targets"].items()}
        if scenario_name == "wealth"
        else {"price_sample_std": [0.05]}
    )
    for metric, references in targets.items():
        values = np.array([row["statistics"][metric] for row in results])
        mean = float(values.mean())
        sem = float(values.std(ddof=1) / np.sqrt(len(values)))
        margin = float(stats.t.ppf(0.975, 99) * sem)
        comparison = {
            "metric": metric,
            "n": 100,
            "mean": mean,
            "ci95": [mean - margin, mean + margin],
        }
        if scenario_name == "trading":
            upper = mean + float(stats.t.ppf(0.95, 99) * sem)
            comparison.update(
                {
                    "upper95": upper,
                    "upper_below_target": upper < 0.05,
                    "source_individual_pass_count": int(np.sum(values <= 0.05)),
                }
            )
        else:
            comparison["targets"] = [
                {"target": x, "inside_ci95": mean - margin <= x <= mean + margin}
                for x in references
            ]
        comparisons.append(comparison)
report = {
    "scenario": scenario_name,
    "validated_runs": len(results),
    "required_runs": 100,
    "complete_ensemble": complete,
    "agent_observations": sum(row["agent_observations"] for row in results),
    "provenance": provenance,
    "results": sorted(results, key=lambda row: row["index"]),
    "comparisons": comparisons,
    "scope": "Frozen quantitative target only; not full-paper completion. Target inclusion does not prove equality.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps(
        {
            key: value
            for key, value in report.items()
            if key not in ["results", "provenance"]
        }
    )
)
