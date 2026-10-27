import unittest, tempfile, subprocess, sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
class Repairs(unittest.TestCase):
 def test_metadata(self):
  from repair_metadata import repair
  body='\n# 中文\n原文 [[附件]]\n'
  self.assertEqual(repair(body,'中文'), '---\ntitle: "中文"\npublished: false\nfeed: hide\n---\n'+body)
  old='---\ntitle:zk\nfeed:show\ntags: [中文]\n---\n'+body
  fixed=repair(old,'unused');self.assertIn('title: zk\nfeed: show',fixed);self.assertTrue(fixed.endswith(body));self.assertIn('tags: [中文]',fixed)
  for marker in ['private: true','publish: false','published: false','feed: hide', 'feed: "hide"', "private: 'true'", 'publish: "false"']:
   s='---\n'+marker+'\n---\n'+body;self.assertEqual(repair(s,'x'),s)
  self.assertIn('published: false',repair(body,'x'))
 def test_safe_cli(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'中文.md';p.write_text('正文')
   r=subprocess.run([sys.executable,str(ROOT/'scripts/repair_metadata.py'),'--root',d],capture_output=True)
   self.assertEqual(r.returncode,0);self.assertEqual(p.read_text(),'正文')
   r=subprocess.run([sys.executable,str(ROOT/'scripts/repair_metadata.py'),'--root',d,'--file','中文.md'],capture_output=True)
   self.assertEqual(r.returncode,0);self.assertEqual(p.read_text(),'正文')
 def test_site(self):
  css=(ROOT/'assets/css/style.css').read_text();layout=(ROOT/'_layouts/Post.html').read_text()
  self.assertNotIn('fonts.googleapis',css+layout);self.assertNotIn('fonts.gstatic',css+layout)
  self.assertNotIn('ie-target.css',layout)
  self.assertNotIn('prism.css',layout)
  self.assertTrue((ROOT/'assets/img/favicon.svg').exists())
  self.assertIn('favicon:',(ROOT/'_config.yml').read_text())
  self.assertIn('/notes',(ROOT/'pages/index.md').read_text());self.assertIn('搜索',(ROOT/'pages/index.md').read_text())
  self.assertNotIn('Your Name',(ROOT/'_config.yml').read_text())
 def test_menu(self):
  self.assertEqual(subprocess.run(['node',str(ROOT/'tests/menu.cjs')],capture_output=True,cwd=ROOT).returncode,0)
if __name__=='__main__':unittest.main()
