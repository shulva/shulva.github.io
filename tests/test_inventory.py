import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class Inventory(unittest.TestCase):
 def test_links(self):
  from check_notes_assets import scan
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'_notes').mkdir();(r/'assets').mkdir()
   (r/'_notes/a.md').write_text('[[missing]] ![[private.png]] [[b|别名]] [图片](../assets/ok.svg)')
   (r/'_notes/b.md').write_text('ok');(r/'assets/ok.svg').write_text('ok')
   data=scan(r);self.assertEqual(len(data['unresolved_wiki']),1);self.assertEqual(len(data['missing_note_attachments']),1);self.assertEqual(data['missing_local_assets'],[])
if __name__=='__main__':unittest.main()
