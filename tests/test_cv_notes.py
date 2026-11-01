"""Real export/demo/build routing regression; synthetic fixtures outside checkout."""
import pathlib,sys,os,tempfile,subprocess,unittest,json
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from selective_export import export
from add_demo import add
from check_stage import check
class Navigation(HTMLParser):
 def __init__(self,text):
  super().__init__();self.in_nav=False;self.links=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='nav' and a.get('aria-label')=='Primary':self.in_nav=True
  if self.in_nav and tag=='a':self.links.append(a)
 def handle_endtag(self,tag):
  if tag=='nav':self.in_nav=False
class CVNotes(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=pathlib.Path(os.environ['TEST_SCRATCH']).resolve()
  if base==ROOT or ROOT in base.parents:raise RuntimeError('fixtures must be outside checkout')
  cls.case=pathlib.Path(tempfile.mkdtemp(prefix='cv-notes-',dir=base));cls.v=cls.case/'synthetic';cls.v.mkdir();cls.stage=cls.case/'content';cls.output=cls.case/'public'
  (cls.v/'selected.md').write_text('---\npublish: true\n---\nSynthetic selected note.\n')
  # Repeat the documented clean-export/demo workflow: neither route may regress.
  for _ in range(2):
   export(cls.v,cls.stage);add(cls.stage);check(cls.stage)
  subprocess.run([sys.executable,str(ROOT/'scripts/site-build.py'),str(cls.stage),str(cls.output)],cwd=ROOT,check=True)
 def test_root_is_blank_cv(self):
  md=(self.stage/'index.md').read_text();html=(self.output/'index.html').read_text()
  self.assertIn('title: Shulva',md);self.assertIn('## Education',md)
  self.assertNotIn('publish: true',md);self.assertNotIn('公开演示',md)
  for feature in ('class="graph"','class="search"','class="backlinks"','class="explorer"'):
   self.assertNotIn(feature,html)
 def test_cv_does_not_inherit_viewport_sidebars(self):
  # Empty Quartz sidebars still carry height:100vh and stronger display rules.
  # A block CV must omit them rather than rely on a weaker display:none rule.
  html=(self.output/'index.html').read_text()
  self.assertNotIn('class="left sidebar"',html)
  self.assertNotIn('class="right sidebar"',html)
  self.assertIn('class="left sidebar"',(self.output/'notes/index.html').read_text())
  self.assertIn('class="right sidebar"',(self.output/'notes/index.html').read_text())
 def test_notes_and_demo_persist(self):
  self.assertTrue((self.output/'notes/index.html').is_file())
  notes=(self.stage/'notes/index.md').read_text()
  self.assertIn('当前明确选中了 1 篇用户笔记',notes);self.assertIn('../demo/公开演示.md',notes)
  self.assertIn('class="graph"',(self.output/'notes/selected.html').read_text())
  for feature in ('class="search"','class="graph"','class="backlinks"'):
   self.assertIn(feature,(self.output/'notes/index.html').read_text())
  self.assertEqual(json.loads((self.stage/'publication.json').read_text())['selected_notes'],1)
 def test_shared_navigation_every_generated_page(self):
  for p in self.output.rglob('*.html'):
   with self.subTest(page=p.relative_to(self.output).as_posix()):
    text=p.read_text();nav=Navigation(text)
    self.assertEqual([a.get('href') for a in nav.links],['/','/notes/'])
    current=[a['href'] for a in nav.links if a.get('aria-current')=='page']
    self.assertEqual(current,['/' if p==self.output/'index.html' else '/notes/'])
    self.assertLess(text.index('aria-label="Primary"'),text.index('id="quartz-root"'))
if __name__=='__main__':unittest.main()
