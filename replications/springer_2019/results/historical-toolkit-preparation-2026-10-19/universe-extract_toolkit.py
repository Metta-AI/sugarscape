import hashlib,json,subprocess,urllib.request
from pathlib import Path
base=Path('/root/sugarscape/dynasoar-cuda91-002')
rootfs=base/'image/rootfs'
packages=base/'packages'
packages.mkdir()
records=json.loads(Path('selected-packages.json').read_text())['records']
for record in records:
    url='https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/'+record['Filename'][2:]
    output=packages/Path(record['Filename']).name
    with urllib.request.urlopen(url,timeout=60) as response, output.open('xb') as destination:
        while True:
            block=response.read(1024*1024)
            if not block: break
            destination.write(block)
    assert output.stat().st_size==int(record['Size'])
    assert hashlib.sha256(output.read_bytes()).hexdigest()==record['SHA256']
    subprocess.run(['dpkg-deb','--extract',str(output),str(rootfs)],check=True,timeout=120)
Path('verified-packages.json').write_text(json.dumps(records,indent=2)+'\n')
