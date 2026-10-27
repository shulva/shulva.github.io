import unittest,json,subprocess,os,sys,tempfile
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
class Tags(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tags=[];self.feed(text)
 def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))
class Attachments(unittest.TestCase):
 def render(self,page,html):
  r=subprocess.run(['ruby','tests/fixtures/render_unavailable.rb'],cwd=ROOT,input=json.dumps({'page':page,'html':html}),capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr);return r.stdout
 def test_rendered_html(self):
  rows=json.loads((ROOT/'_data/unavailable_attachments.yml').read_text())
  for row in rows:
   url=row['urls'][0];encoded=url.replace('&','&amp;');p=row['page']
   tag=f'<img alt="original" src="{encoded}" />' if row['kind']=='image' else f'<a href="{encoded}">PDF</a>'
   code='<pre><code>'+tag.replace('<','&lt;').replace('>','&gt;')+'</code></pre>'
   rawcode='<pre><code>'+tag+'</code></pre>'
   normal='<img src="/assets/ok.svg" alt="OK"><a href="/assets/ok.pdf">OK</a>'
   out=self.render(p,tag+tag+normal+code+rawcode)
   parsed=Tags(out);changed=[v for t,v in parsed.tags if 'data-missing-resource' in v]
   self.assertEqual(len(changed),2)
   self.assertIn(normal,out);self.assertIn(code,out);self.assertIn(rawcode,out)
   self.assertEqual(self.render('_notes/other.md',tag).strip(),tag)
   for attrs in changed:
    self.assertEqual(attrs['data-missing-resource'],url)
    if row['kind']=='image':
     self.assertEqual(attrs['alt'],'original');self.assertEqual(attrs['src'],'/assets/images/attachment-unavailable.svg')
     self.assertTrue((ROOT/attrs['src'].lstrip('/')).is_file())
    else:self.assertNotIn('href',attrs);self.assertEqual(attrs['aria-disabled'],'true')
   if row['kind']=='document':self.assertEqual(out.count('</a><span class="unavailable-attachment">附件未收录</span>'),2)
 def test_checker_attributes(self):
  from check_generated import check
  with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as d:
   root=Path(d);(root/'SearchData.json').write_text('{}');(root/'index.html').write_text('<a aria-disabled="true" data-missing-resource="missing.pdf">PDF</a>&lt;img src="example.png"&gt;')
   self.assertEqual(check(root,{'public':[],'private':[]})['errors'],[])
   (root/'index.html').write_text('<img src="real-missing.png">')
   self.assertTrue(check(root,{'public':[],'private':[]})['errors'])
if __name__=='__main__':unittest.main()
