"""Observe native levy transfers and verify the observer leaves trajectories unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
source = engine / "sugarscape_ai_tax/model.py"
assert hashlib.sha256(source.read_bytes()).hexdigest() == "a3e264cb1640691451b2936cd85a17f21bc8b17f5a2f36977dc8ee1db698ed24"
sys.path.insert(0, str(engine))
from sugarscape_ai_tax.model import SugarscapeAITax

args.output.mkdir(parents=True, exist_ok=False)
events = []
pending = {}
code = SugarscapeAITax._apply_displacement.__code__


def trace(frame, event, arg):
    if frame.f_code is not code:
        return None
    if event == "line" and frame.f_lineno == 693:
        model = frame.f_locals["self"]
        pending.update({"event": model.cumulative_displacement_conversions + 1,
                        "nominal": float(frame.f_locals["levy_amount"]),
                        "owner_before": float(frame.f_locals["new_owner"].wealth),
                        "treasury_before": float(model.treasury),
                        "tax_before": float(model.step_tax_revenue)})
    elif event == "line" and frame.f_lineno == 700:
        model = frame.f_locals["self"]
        record = dict(pending)
        record["owner_after"] = float(frame.f_locals["new_owner"].wealth)
        record["owner_deduction"] = record["owner_before"] - record["owner_after"]
        record["treasury_credit"] = float(model.treasury) - record["treasury_before"]
        record["reported_tax"] = float(model.step_tax_revenue) - record["tax_before"]
        record["paper_transfer"] = min(record["nominal"], record["owner_before"])
        events.append(record)
        pending.clear()
    return trace


parameters = {"tax_regime": "displacement_levy", "redistribution_mode": "means_tested",
              "k": 5, "m": 20, "displacement_levy_rate": 50.0, "seed": 0}
# No labour or wealth tax applies to this regime; their calibration thresholds are unused.
for mode in ["native", "observed"]:
    model = SugarscapeAITax(**parameters)
    if mode == "observed":
        sys.settrace(trace)
    try:
        model.run_model(300)
    finally:
        sys.settrace(None)
    model.datacollector.get_model_vars_dataframe().to_csv(args.output / f"{mode}.csv", index=False)
    print(f"Completed {mode}", flush=True)
assert (args.output / "native.csv").read_bytes() == (args.output / "observed.csv").read_bytes()
assert len(events) == 60 and not pending
assert [e["event"] for e in events] == list(range(1, 61))
assert all(abs(e["owner_deduction"] - e["paper_transfer"]) < 1e-9 for e in events)
assert all(abs(e["treasury_credit"] - e["reported_tax"]) < 1e-9 for e in events)
report = {"parameters": parameters, "steps": 300, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
          "native_observed_byte_identical": True, "events": events,
          "total_owner_deductions": sum(e["owner_deduction"] for e in events),
          "total_treasury_credits": sum(e["treasury_credit"] for e in events),
          "capped_events": sum(e["nominal"] > e["owner_before"] for e in events),
          "nonconserving_events": sum(abs(e["owner_deduction"] - e["treasury_credit"]) > 1e-9 for e in events),
          "interpretation": "Original-source execution diagnostic; native model unchanged. Does not quantify effects of correcting levy accounting."}
(args.output / "events.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "events"}))
