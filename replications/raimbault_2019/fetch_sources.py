"""Download immutable source data and verify the recorded content hashes."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = json.loads((Path(__file__).parent / "sources.json").read_text())
    for source in sources["files"]:
        target = args.output / source["name"]
        subprocess.run(["curl", "-fLsS", source["url"], "-o", str(target)], check=True)
        assert target.stat().st_size == source["bytes"]
        assert hashlib.sha256(target.read_bytes()).hexdigest() == source["sha256"]
        print(f"Verified {source['name']}: {source['bytes']} bytes")


if __name__ == "__main__":
    main()
