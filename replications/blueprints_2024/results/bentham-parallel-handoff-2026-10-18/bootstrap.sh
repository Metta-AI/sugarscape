#!/bin/bash
set -eu
cd /home/ubuntu/blueprints-bentham-parallel-001
exec >> workflow.log 2>&1
trap 'exit 124' TERM
trap 'rc=$?; printf "%s\n" "$rc" > exit-code.txt; tar -czf /home/ubuntu/blueprints-bentham-parallel-evidence-001.partial.tar.gz .; mv /home/ubuntu/blueprints-bentham-parallel-evidence-001.partial.tar.gz /home/ubuntu/blueprints-bentham-parallel-evidence-001.tar.gz; exit "$rc"' EXIT
qualification=/home/ubuntu/blueprints-bentham-qualification-001
"$qualification/venv/bin/python" run_parallel_handoff.py \
  "$qualification/engine" "$qualification/blueprints-homogeneous.zip" "$qualification" \
  plan.json stop-receipt.json local-completed.jsonl runs
