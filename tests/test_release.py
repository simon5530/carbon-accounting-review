import copy,hashlib,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import release
from check_repo import safe_paths,heading_ids

def local():
    return {'schemaVersion':1,'owner':'simon5530','slug':'carbon-accounting-review','version':'1.2.0','files':[{'path':'SKILL.md','size':2,'sha256':'a'*64}]}
def remote():
    return {'owner':{'handle':'simon5530'},'skill':{'slug':'carbon-accounting-review'},'version':{'version':'1.2.0','files':[{'path':'SKILL.md','sha256':'a'*64},{'path':'skill-card.md','sha256':'b'*64}]}}

class ReleaseContracts(unittest.TestCase):
    def test_same_source_and_generated_card(self):
        self.assertTrue(release.compare(local(),remote())['registryVerified'])
    def test_hash_mismatch(self):
        r=remote();r['version']['files'][0]['sha256']='c'*64
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_missing_file(self):
        r=remote();r['version']['files']=r['version']['files'][1:]
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_extra_file_not_silently_ignored(self):
        r=remote();r['version']['files'].append({'path':'unexpected.py','sha256':'c'*64})
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_wrong_owner(self):
        r=remote();r['owner']['handle']='other-publisher'
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_wrong_slug(self):
        r=remote();r['skill']['slug']='different-skill'
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_wrong_version(self):
        r=remote();r['version']['version']='1.2.1'
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_duplicate_registry_path(self):
        r=remote();r['version']['files'].append(r['version']['files'][0])
        with self.assertRaises(ValueError):release.compare(local(),r)
    def test_unsafe_paths(self):
        for name in ['../private','/outside','x/../../secret','C:secret','x\\secret','-option']:
            with self.subTest(path=name),self.assertRaises(ValueError):safe_paths([name])
    def test_duplicate_allowlist(self):
        with self.assertRaises(ValueError):safe_paths(['x','x'])
    def test_unsafe_versions(self):
        for v in ['latest','../x','1.0.0/secret','--help']:
            with self.subTest(version=v),self.assertRaises(ValueError):release.valid_version(v)
    def test_heading_fragments(self):
        self.assertEqual(heading_ids('# Same\n# Same\n## Hello, world!'),{'same','same-1','hello-world'})
    def test_record_conflict_preserves_original(self):
        with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)):
            p=Path(t)/'release-manifests';p.mkdir();f=p/'1.2.0.json';f.write_text(json.dumps(local()));before=f.read_bytes();changed=local();changed['files'][0]['sha256']='d'*64
            with self.assertRaises(ValueError):release.record(changed)
            self.assertEqual(f.read_bytes(),before)
    def test_pack_contains_only_source_blobs_no_publish(self):
        blobs={'SKILL.md':b'Version: 1.2.0','CHANGELOG.md':b'# 1.2.0'};m=local();m['gitCommit']='f'*40;m['files']=[{'path':n,'size':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in sorted(blobs.items())]
        with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)),patch.object(release,'check'),patch.object(release,'git',return_value=b''),patch.object(release,'source',return_value=(m,blobs)),patch.object(release,'lookup') as lookup:
            (Path(t)/'private-test-marker.txt').write_text('not part of payload')
            result=release.pack('1.2.0','test-ref')
            with zipfile.ZipFile(Path(t)/result['zip']) as z:self.assertEqual(set(z.namelist()),set(blobs))
            self.assertFalse(result['published']);lookup.assert_not_called()
    def test_pack_refuses_dirty_tree(self):
        with patch.object(release,'check'),patch.object(release,'git',return_value=b' M SKILL.md'):
            with self.assertRaises(ValueError):release.pack('1.2.0','HEAD')
    def test_pack_refuses_unreleased(self):
        with patch.object(release,'check'),patch.object(release,'git',return_value=b''),patch.object(release,'source',return_value=(local(),{'SKILL.md':b'Working-copy status: Unreleased','CHANGELOG.md':b'## Unreleased'})):
            with self.assertRaises(ValueError):release.pack('1.2.0','HEAD')

if __name__=='__main__':unittest.main()
