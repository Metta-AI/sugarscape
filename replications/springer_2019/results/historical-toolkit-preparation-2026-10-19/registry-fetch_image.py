import hashlib,json,urllib.request
from pathlib import Path
base=Path('/root/sugarscape/dynasoar-cuda91-003/ubuntu')
blobs=base/'blobs/sha256'
blobs.mkdir(parents=True)
pinned=json.loads(Path('ubuntu16-amd64.json').read_text())
token=json.load(urllib.request.urlopen('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/ubuntu:pull',timeout=60))['token']
headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.docker.distribution.manifest.v2+json'}
url='https://registry-1.docker.io/v2/library/ubuntu/'
raw=urllib.request.urlopen(urllib.request.Request(url+'manifests/'+pinned['digest'],headers=headers),timeout=60).read()
assert 'sha256:'+hashlib.sha256(raw).hexdigest()==pinned['digest']
manifest=json.loads(raw)
assert manifest==pinned['manifest']
for item in [manifest['config']]+manifest['layers']:
    output=blobs/item['digest'].split(':')[1]
    with urllib.request.urlopen(urllib.request.Request(url+'blobs/'+item['digest'],headers=headers),timeout=60) as response, output.open('xb') as destination:
        while True:
            block=response.read(1024*1024)
            if not block:break
            destination.write(block)
    assert output.stat().st_size==item['size']
    assert 'sha256:'+hashlib.sha256(output.read_bytes()).hexdigest()==item['digest']
manifest['mediaType']='application/vnd.oci.image.manifest.v1+json'
manifest['config']['mediaType']='application/vnd.oci.image.config.v1+json'
for layer in manifest['layers']:layer['mediaType']='application/vnd.oci.image.layer.v1.tar+gzip'
raw=json.dumps(manifest,separators=(',',':')).encode()
digest=hashlib.sha256(raw).hexdigest()
(blobs/digest).write_bytes(raw)
(base/'oci-layout').write_text(json.dumps({'imageLayoutVersion':'1.0.0'}))
(base/'index.json').write_text(json.dumps({'schemaVersion':2,'manifests':[{'mediaType':manifest['mediaType'],'digest':'sha256:'+digest,'size':len(raw),'annotations':{'org.opencontainers.image.ref.name':'16.04'}}]}))
Path('image-verification.json').write_text(json.dumps({'docker_manifest':pinned['digest'],'oci_manifest':'sha256:'+digest,'verified_blobs':len(manifest['layers'])+1,'scope':'Verified original image content; manifest media-type conversion only, no layer changes'},indent=2)+'\n')
