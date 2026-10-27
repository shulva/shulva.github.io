import unittest,json,subprocess,os,sys,tempfile,textwrap,re
from html import escape
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
 def test_complete_visible_attachment_coverage(self):
  from build_attachment_inventory import scan
  inventory=scan(ROOT)
  rows=json.loads((ROOT/'_data/unavailable_attachments.yml').read_text())
  expected={(r['page'],r['url'],r['kind']) for r in inventory['candidates'] if r['missing']}
  actual={(r['page'],url,r['kind']) for r in rows for url in r['urls']}
  self.assertEqual(len(expected-actual),0,"missing page/url/kind mappings")
  self.assertEqual(len(actual-expected),0,"stale or existing-resource mappings")
  for name in ('02.Vector.pdf','03.List.pdf'):
   self.assertTrue(any(r['target'].endswith(name) for r in rows),name)
  self.assertEqual(rows,inventory['mapping'])
 def test_every_mapped_url_renders_with_full_parameters(self):
  for row in json.loads((ROOT/'_data/unavailable_attachments.yml').read_text()):
   tags=[]
   for url in row['urls']:
    encoded=escape(url,quote=True)
    tags.append(f'<img src="{encoded}" alt="original" />' if row['kind']=='image' else f'<a href="{encoded}">PDF</a>')
   out=self.render(row['page'],''.join(tags))
   attrs=[a for _,a in Tags(out).tags if 'data-missing-resource' in a]
   self.assertEqual([a['data-missing-resource'] for a in attrs],row['urls'])
 def test_generated_diagnostics_summary_and_full_json(self):
  workflow=(ROOT/'.github/workflows/verify-pages.yml').read_text()
  script=textwrap.dedent(re.search(r"          python3 -B - <<'PYREPORT'\n(.*?)          PYREPORT",workflow,re.S)[1])
  with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
   path=Path(directory)/'generated-check.json'
   original=json.dumps({'errors':[f'missing resource: notes/p.html -> files/t{i%10}.pdf#page={i}' for i in range(23)]})
   path.write_text(original)
   result=subprocess.run([sys.executable,'-B','-c',script],cwd=directory,text=True,capture_output=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertIn('total errors=23; unique missing-resource targets=10',result.stdout)
   self.assertIn('Full errors: generated-check.json artifact; JSON is not truncated.',result.stdout)
   self.assertEqual(result.stdout.count('::error::Generated: missing resource:'),8)
   self.assertNotIn('#page=',result.stdout)
   self.assertEqual(path.read_text(),original)
 def test_generated_diagnostics_resolves_each_build_page_parent(self):
  workflow=(ROOT/'.github/workflows/verify-pages.yml').read_text()
  script=textwrap.dedent(re.search(r"          python3 -B - <<'PYREPORT'\n(.*?)          PYREPORT",workflow,re.S)[1])
  with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
   path=Path(directory)/'generated-check.json'
   path.write_text(json.dumps({'errors':[
    'missing resource: notes/a.html -> files/same.pdf#page=1',
    'missing resource: notes/deep/b.html -> files/same.pdf#page=2']}))
   result=subprocess.run([sys.executable,'-B','-c',script],cwd=directory,text=True,capture_output=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertIn('total errors=2; unique missing-resource targets=2',result.stdout)
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
