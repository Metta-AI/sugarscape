from pathlib import Path
import hashlib, json, subprocess, sys, tarfile, time
source=Path("/root/sugarscape/blueprints-portability-001")
root=Path("/root/sugarscape/blueprints-raw50000-001")
root.mkdir()
(root/"run.py").write_bytes(Path(__file__).read_bytes())
assert hashlib.sha256((source/"run_runtime.py").read_bytes()).hexdigest()=="df86e98f480c68abae4a3a647bcfe53bbce287c16850802e11c38eef8e6dd8d2"
command=[str(source/"venv/bin/python"),str(source/"run_runtime.py"),str(source/"engine"),str(source/"blueprints-runtimes.zip"),"rawSugarscape","50000",str(root/"rawSugarscape"),"--seconds","21600"]
(root/"plan.json").write_text(json.dumps({"command":command,"indices":[0,100],"steps":50000,"model":"rawSugarscape","workers":1,"seconds":21600,"scope":"Previously unstarted deposited50000-step group. Different horizon/configurations from the completed5000-step group; no duplicated condition."},indent=2)+"\n")
started=time.time()
with (root/"run.log").open("x") as log:
    result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(root/"terminal.json").write_text(json.dumps({"exit_code":result.returncode,"elapsed_seconds":time.time()-started})+"\n")
archive=Path("/root/sugarscape/blueprints-raw50000-evidence-001.tar.gz")
with tarfile.open(archive,"w:gz") as bundle:bundle.add(root,arcname=root.name)
print(json.dumps({"archive":str(archive),"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"exit_code":result.returncode}),flush=True)
sys.exit(result.returncode)
