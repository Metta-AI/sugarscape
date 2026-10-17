import json, os, signal, subprocess, time
from pathlib import Path
root=Path(__file__).resolve().parent
plan=json.loads((root/"plan.json").read_text())
started=time.time()
with (root/"run.log").open("x") as log:
    process=subprocess.Popen(plan["command"],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,"PYTHONHASHSEED":"0","PYTHONDONTWRITEBYTECODE":"1"})
    (root/"process.json").write_text(json.dumps({"pid":process.pid,"started":started})+"\n")
    try:
        process.wait(timeout=plan["timeout_seconds"])
    finally:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL)
            process.wait()
        (root/"exit.json").write_text(json.dumps({"exit_code":process.returncode,"elapsed_seconds":time.time()-started})+"\n")
