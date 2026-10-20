set -eu; export DEBIAN_FRONTEND=noninteractive; apt-get update -qq; apt-get install -y -qq python3 git cmake; exec /usr/bin/python3 -c 'from pathlib import Path
import hashlib,tarfile,urllib.request,os
archive=Path("/root/sugarscape/richmond-initializer-boot-input-002.tar.gz")
archive.write_bytes(urllib.request.urlopen('"'"'https://raw.githubusercontent.com/Metta-AI/sugarscape/c9b27f47eed2fdce8902102b8e6b950641961fba/replications/richmond_2023/results/initializer-native-queued-2026-10-20/input.tar.gz'"'"',timeout=60).read())
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='"'"'41a745cb99a3531e5d4d90428a6f2c7785e42f8bdfefb4888b2ee2fc2d84391b'"'"'
root=Path("/root/sugarscape/richmond-initializer-native-controls-001")
root.mkdir()
with tarfile.open(archive) as bundle:
    assert all(m.isfile() or m.isdir() for m in bundle.getmembers())
    assert all(not Path(m.name).is_absolute() and ".." not in Path(m.name).parts for m in bundle.getmembers())
    bundle.extractall(root)
os.execv("/usr/bin/python3",["/usr/bin/python3",str(root/"run_controls.py")])'
