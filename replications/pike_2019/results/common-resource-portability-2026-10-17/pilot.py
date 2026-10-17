from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys,tarfile,time
root=Path("/root/sugarscape/pike-common-cloud-portability-001")
source=Path("/root/sugarscape/pike-portability-001")
commands=[["/root/sugarscape/pike-venv/bin/python",str(root/"run.py"),str(source/"engine"),str(source/"library"),variant,"1",str(root/variant)] for variant in ["common-one","common-multi"]]
(root/"plan.json").write_text(json.dumps({"commands":commands,"scope":"Two seed1 portability controls against completed local native conditions; never count as new grid coverage."},indent=2)+"\n")
started=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(lambda command:subprocess.run(command,capture_output=True,text=True,env=__import__("os").environ|{"PYTHONHASHSEED":"0","PYTHONDONTWRITEBYTECODE":"1"},timeout=240),commands))
for index,result in enumerate(results):
    (root/f"worker-{index}.log").write_text(result.stdout+result.stderr)
(root/"terminal.json").write_text(json.dumps({"exit_codes":[r.returncode for r in results],"elapsed_seconds":time.time()-started})+"\n")
archive=Path("/root/sugarscape/pike-common-portability-evidence-001.tar.gz")
with tarfile.open(archive,"w:gz") as t:t.add(root,arcname=root.name)
print(json.dumps({"archive":str(archive),"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"bytes":archive.stat().st_size}),flush=True)
assert all(r.returncode==0 for r in results)
