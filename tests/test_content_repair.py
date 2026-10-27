import unittest,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class Publication(unittest.TestCase):
 def test_publish(self):
  from repair_metadata import repair
  for body in ['# 中文\n正文\n','# 中文\r\n正文\r\n']:
   result=repair(body,'fallback',publish=True)
   self.assertIn('published: true',result);self.assertIn('feed: show',result)
   self.assertIn('title: "中文"',result);self.assertTrue(result.endswith(body))
  for flag in ['private: true','publish:false','published: false','feed:hide']:
   old='---\n'+flag+'\n---\nbody';self.assertEqual(repair(old,'x',publish=True),old)
 def test_generated(self):
  from check_generated import check
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'notes').mkdir();(root/'notes/index.html').write_text('<a href="/notes/a">A</a>')
   (root/'notes/a.html').write_text('<img src="/assets/missing.png">')
   (root/'SearchData.json').write_text('{"0":{"url":"/notes/a"}}')
   manifest={'public':[{'file':'a.md','url':'/notes/a'}],'private':[]}
   self.assertTrue(check(root,manifest)['errors'])
   (root/'assets').mkdir();(root/'assets/missing.png').write_bytes(b'x')
   self.assertEqual(check(root,manifest)['errors'],[])
