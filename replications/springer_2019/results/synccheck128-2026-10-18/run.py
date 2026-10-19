import hashlib,json,shutil,subprocess,sys
from pathlib import Path
source=Path("/root/sugarscape/dynasoar-grid128-native-007/diagnostic/native")
records=json.loads((source/"records.json").read_text())
assert len(records)==1
record=records[0]
assert record["grid_side"]==128
binary=source/"debug-128"
assert hashlib.sha256(binary.read_bytes()).hexdigest()==record["binary_sha256"]
shutil.copy2(binary,"debug-128")
shutil.copy2(source/"records.json","parent-records.json")
Path("sanitizer-version.txt").write_text(subprocess.check_output(["compute-sanitizer","--version"],text=True))
cmd=["timeout","90","compute-sanitizer","--tool","synccheck","--error-exitcode","86","./debug-128"]
Path("command.json").write_text(json.dumps(cmd,indent=2)+"\n")
with Path("sanitizer.log").open("x") as log:
    result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=110)
Path("result.json").write_text(json.dumps({"returncode":result.returncode,"binary_sha256":record["binary_sha256"],"scope":"Synchronization diagnostic of unchanged grid128 binary; no benchmark or model-correctness verdict."},indent=2)+"\n")
sys.exit(result.returncode)
