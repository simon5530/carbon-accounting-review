#!/usr/bin/env python3
"""Deterministic repository/package checks; no model or external service calls."""
from pathlib import Path
import json,re,sys,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=Path('skill/carbon-accounting-review')

def safe_paths(values):
    if not isinstance(values,list) or not values or len(set(values))!=len(values):
        raise ValueError('Invalid or duplicate package allowlist')
    for value in values:
        if not isinstance(value,str) or value.startswith(('/', '-')) or '\\' in value or ':' in value or '..' in Path(value).parts:
            raise ValueError('Unsafe package path')
    return values

def heading_ids(text):
    seen={};ids=set()
    for line in text.splitlines():
        m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
        if not m:continue
        title=re.sub(r'<[^>]+>','',m.group(1)).replace(chr(96),'').strip().lower()
        slug=re.sub(r'[^\w\- ]','',title).replace(' ','-')
        n=seen.get(slug,0);seen[slug]=n+1;ids.add(slug+('-'+str(n) if n else ''))
    return ids

def check(root=ROOT):
    root=Path(root).resolve();package=root/PACKAGE;expected=safe_paths(json.loads((root/'skill-files.json').read_text()))
    actual={p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() or p.is_symlink()}
    if actual!=set(expected):raise ValueError('Package allowlist mismatch: '+str(sorted(actual^set(expected))))
    checks=0;links=0
    for name in expected:
        p=package/name
        if p.is_symlink() or p.stat().st_mode & 0o111:raise ValueError('Package is not plain non-executable text: '+name)
        raw=p.read_bytes();text=raw.decode('utf-8')
        if len(raw)>100000 or b'\x00' in raw:raise ValueError('Unexpected binary or oversized source: '+name)
        if re.search(r'/Users/[A-Za-z0-9]|/home/[A-Za-z0-9]|-----BEGIN [A-Z ]*PRIVATE KEY-----',text):raise ValueError('Private-pattern review required: '+name)
        if p.suffix=='.json':
            value=json.loads(text)
            if value.get('synthetic') is not True:raise ValueError('Example must be declared synthetic: '+name)
        checks+=1
    skill=(package/'SKILL.md').read_text();changelog=(package/'CHANGELOG.md').read_text()
    if not skill.startswith('---\n') or 'name: carbon-accounting-review' not in skill or 'license: MIT-0' not in skill:raise ValueError('Skill metadata mismatch')
    if 'MIT No Attribution' not in (package/'LICENSE').read_text():raise ValueError('License mismatch')
    if ('## Unreleased' in changelog)!=('Working-copy status:' in skill):raise ValueError('Unreleased notice/changelog mismatch')
    for path in [package/'README.md',package/'GOVERNANCE.md',package/'LICENSE']:
        if 'Simon Huang' not in path.read_text():raise ValueError('Original credit missing')
    for p in root.rglob('*.md'):
        if '.git' in p.parts or 'dist' in p.relative_to(root).parts:continue
        text=p.read_text()
        for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)',text):
            u=urllib.parse.urlsplit(target)
            if u.scheme or u.netloc:continue
            dest=(p.parent/urllib.parse.unquote(u.path)).resolve() if u.path else p.resolve()
            if not dest.is_relative_to(root) or not dest.is_file():raise ValueError('Broken/out-of-scope link: '+str(p.relative_to(root))+' -> '+target)
            if u.fragment and urllib.parse.unquote(u.fragment) not in heading_ids(dest.read_text()):raise ValueError('Missing fragment: '+target)
            links+=1
    return {'packageFilesChecked':checks,'localLinksChecked':links,'scope':'Static packaging, metadata and links only; not behavior or security certification'}

if __name__=='__main__':
    try:print(json.dumps({'passed':True,**check()},indent=2))
    except (OSError,ValueError,UnicodeError) as e:
        print(json.dumps({'passed':False,'error':str(e)}));sys.exit(1)
