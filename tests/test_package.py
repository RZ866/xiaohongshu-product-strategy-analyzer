from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from package_release import public_files,audit

class PackageTests(unittest.TestCase):
    def test_private_paths_excluded(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for name in ['.qa/private.txt','outputs/report.html','private-inputs/photo.txt','dist/package.zip','scripts/main.py','README.md']:
                f=root/name; f.parent.mkdir(parents=True,exist_ok=True); f.write_text('public')
            self.assertEqual({p.relative_to(root).as_posix() for p in public_files(root)},{'scripts/main.py','README.md'})

    def test_secret_detection(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'README.md'; p.write_text('ghp_'+'a'*36)
            self.assertEqual(audit([p],Path(t)),['README.md'])

    def test_current_tree_clean(self): self.assertEqual(audit(public_files()),[])
