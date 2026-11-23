#!/usr/bin/env python3
"""Build immutable skill payloads or inspect a named public release. Never publish."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,zipfile
from check_repo import ROOT,PACKAGE,safe_paths,check
SLUG='carbon-accounting-review';OWNER='simon5530';GENERATED={'skill-card.md'}

def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True).stdout

def commit_for(ref):
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]{0,159}',ref):raise ValueError('Invalid Git reference')
    value=git('rev-parse','--verify','--end-of-options',ref+'^{commit}').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40,64}',value):raise ValueError('Invalid resolved commit')
    return value

def source(ref=None):
    commit=commit_for(ref) if ref else None
    def read(path):return git('show',commit+':'+path) if commit else (ROOT/path).read_bytes()
    paths=safe_paths(json.loads(read('skill-files.json')))
    if commit:
        listed=git('ls-tree','-r','--name-only',commit,'--',PACKAGE.as_posix()).decode().splitlines()
        actual={name[len(PACKAGE.as_posix())+1:] for name in listed}
    else:actual={p.relative_to(ROOT/PACKAGE).as_posix() for p in (ROOT/PACKAGE).rglob('*') if p.is_file() or p.is_symlink()}
    if actual!=set(paths):raise ValueError('Source snapshot does not match package allowlist')
    blobs={name:read((PACKAGE/name).as_posix()) for name in paths}
    text=blobs['SKILL.md'].decode();m=re.search(r'Version:\s*(\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?)',text)
    if not m:raise ValueError('Missing explicit package version')
    manifest={'schemaVersion':1,'slug':SLUG,'owner':OWNER,'version':m.group(1),'gitCommit':commit,'sourcePath':PACKAGE.as_posix(),'workingTree':commit is None,'files':[{'path':n,'size':len(blobs[n]),'sha256':hashlib.sha256(blobs[n]).hexdigest()} for n in sorted(blobs)]}
    return manifest,blobs

def compare(local,remote):
    version=remote.get('version') or {};owner=remote.get('owner') or {};skill=remote.get('skill') or {}
    if owner.get('handle')!=OWNER or skill.get('slug')!=SLUG or version.get('version')!=local['version']:raise ValueError('Registry owner, slug or named version mismatch')
    values=version.get('files')
    if not isinstance(values,list) or len({v['path'] for v in values})!=len(values):raise ValueError('Invalid/duplicate registry file list')
    actual={v['path']:v['sha256'] for v in values if v['path'] not in GENERATED};expected={v['path']:v['sha256'] for v in local['files']}
    mismatch=sorted(n for n in set(actual)|set(expected) if actual.get(n)!=expected.get(n))
    if mismatch:raise ValueError('Registry content mismatch: '+', '.join(mismatch))
    return {**local,'registryVerified':True,'registryGeneratedExcluded':sorted(v['path'] for v in values if v['path'] in GENERATED),'validationBoundary':'Exact published content identity only; not behavioral accuracy or security certification'}

def lookup(version):
    try:p=subprocess.run(['clawhub','inspect',SLUG,'--version',version,'--files','--json'],check=True,capture_output=True,text=True,timeout=45)
    except (OSError,subprocess.SubprocessError) as e:raise ValueError('Registry inspection unavailable; no publication or retry was attempted') from e
    try:return json.loads(p.stdout)
    except ValueError as e:raise ValueError('Registry inspection returned invalid JSON; not verified') from e

def valid_version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?',value):raise ValueError('Expected a semantic version')
    return value

def pack(version,ref):
    check();version=valid_version(version)
    if git('status','--porcelain').strip():raise ValueError('Commit/preserve all local changes before packing')
    manifest,blobs=source(ref)
    if manifest['version']!=version:raise ValueError('Requested version differs from source metadata')
    if 'Working-copy status:' in blobs['SKILL.md'].decode() or '## Unreleased' in blobs['CHANGELOG.md'].decode():raise ValueError('Refusing to package an Unreleased working copy')
    dist=ROOT/'dist'
    if not dist.resolve().is_relative_to(ROOT):raise ValueError('Unsafe output directory')
    dist.mkdir(exist_ok=True);name=SLUG+'-'+version;stage=dist/name;archive=dist/(name+'.zip');receipt=dist/(name+'.manifest.json')
    if any(p.exists() or p.is_symlink() for p in [stage,archive,receipt]):raise ValueError('Output already exists; inspect it instead of overwriting')
    stage.mkdir()
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(blobs.items()):
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);z.writestr(name,data)
    receipt.write_text(json.dumps(manifest,indent=2)+'\n')
    return {'packageDirectory':str(stage.relative_to(ROOT)),'zip':str(archive.relative_to(ROOT)),'manifest':str(receipt.relative_to(ROOT)),'sourceCommit':manifest['gitCommit'],'files':len(blobs),'published':False}

def record(result):
    path=ROOT/'release-manifests'/(valid_version(result['version'])+'.json')
    if not path.parent.resolve().is_relative_to(ROOT) or path.is_symlink():raise ValueError('Unsafe receipt path')
    if path.exists():
        old=json.loads(path.read_text())
        if old['version']!=result['version'] or old['files']!=result['files']:raise ValueError('Conflicting release record; no overwrite')
        return {'record':str(path.relative_to(ROOT)),'existingMatchingRecordPreserved':True}
    path.write_text(json.dumps(result,indent=2)+'\n');return {'record':str(path.relative_to(ROOT)),'written':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['manifest','pack','verify','record']);parser.add_argument('version',nargs='?');parser.add_argument('--ref');a=parser.parse_args()
    if a.command=='manifest':return source(a.ref)[0]
    if not a.version:raise ValueError('Named version required')
    version=valid_version(a.version);ref=a.ref or ('HEAD' if a.command=='pack' else 'v'+version)
    if a.command=='pack':return pack(version,ref)
    local,_=source(ref)
    if local['version']!=version:raise ValueError('Version differs from selected Git source')
    result=compare(local,lookup(version));return record(result) if a.command=='record' else result

if __name__=='__main__':
    try:print(json.dumps(main(),indent=2))
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as e:
        print(json.dumps({'passed':False,'error':str(e),'published':False}));sys.exit(1)
