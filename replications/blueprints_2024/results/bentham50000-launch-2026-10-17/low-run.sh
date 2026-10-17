set -eu
timeout 12000 bash -c 'until test -f /home/dev/sugarscape/blueprints-runtime-round2-002/runs/terminal.json; do sleep 30; done'
printf '%s\n' '9ea2faf63c401d270726e6acc3df9986a1d7c2b9c1b6235fd5372a652a5d2ea9  /home/dev/sugarscape/blueprints-runtime-round2-001/runs/run_recovery.py' 'df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2  /home/dev/sugarscape/blueprints-runtime2-source-001/run_runtime.py' | sha256sum -c -
timeout --signal=TERM --kill-after=30 22000 /home/dev/sugarscape/blueprints-runtime2-source-001/venv/bin/python /home/dev/sugarscape/blueprints-runtime-round2-001/runs/run_recovery.py /home/dev/sugarscape/blueprints-runtime2-source-001 /home/dev/sugarscape/blueprints-bentham50k-input/low-plan.json /home/dev/sugarscape/blueprints-bentham50k-001/low
