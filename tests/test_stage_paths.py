"""Regression for coordinator's ../ candidate path, retaining integrity checks."""
import hashlib,json,os,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_stage import check
from selective_export import export

class StagePaths(unittest.TestCase):
 def setUp(self):
  base=pathlib.Path(os.environ['TEST_SCRATCH']).resolve()
  if base==ROOT or ROOT in base.parents:raise RuntimeError('fixtures must be outside checkout')
  self.case=pathlib.Path(tempfile.mkdtemp(prefix='stage-path-',dir=base))
  self.stage=self.case/'content'
  (self.case/'other').mkdir()
  vault=self.case/'empty-fixture';vault.mkdir();export(vault,self.stage)
 def test_parent_relative_path(self):
  path=self.case/'other'/'..'/'content'
  self.assertEqual(check(path),check(self.stage))
 def test_root_symlink_rejected(self):
  link=self.case/'link';link.symlink_to(self.stage,target_is_directory=True)
  with self.assertRaises(ValueError):check(link)
 def test_ancestor_symlink_rejected(self):
  link=self.case/'link';link.symlink_to(self.case,target_is_directory=True)
  with self.assertRaises(ValueError):check(link/'content')
 def test_tampering_rejected(self):
  (self.stage/'index.md').write_text('Changed')
  with self.assertRaises(ValueError):check(self.stage)

if __name__=='__main__':unittest.main()
