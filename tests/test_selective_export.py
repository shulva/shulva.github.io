"""Behavior tests create private synthetic sources outside the sanitized checkout.
Set TEST_SCRATCH to a task-owned directory outside this repository.
"""
import pathlib,unittest,os,tempfile,sys,json,struct,zlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from selective_export import export,ExportError
SCRATCH=pathlib.Path(os.environ['TEST_SCRATCH']).resolve()
REPO=pathlib.Path(__file__).resolve().parents[1]
if SCRATCH==REPO or REPO in SCRATCH.parents:raise RuntimeError('fixtures must be outside public worktree')
CANARIES=['PRIVATE_BODY_8e71','PRIVATE_ALIAS_8e71','PRIVATE_TITLE_8e71','PRIVATE_FILE_8e71','UNREFERENCED_8e71']
def png(text=b''):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'tEXt',text)+chunk(b'IDAT',zlib.compress(b'\0\0\0\0'))+chunk(b'IEND',b'')
class Publication(unittest.TestCase):
 def setUp(self):
  self.case=pathlib.Path(tempfile.mkdtemp(dir=SCRATCH));self.v=self.case/'vault';self.v.mkdir();self.out=self.case/'staged'
  self.note('PRIVATE_FILE_8e71.md','---\ntitle: PRIVATE_TITLE_8e71\naliases: [PRIVATE_ALIAS_8e71]\n---\nPRIVATE_BODY_8e71')
 def note(self,n,t):
  p=self.v/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);return p
 def public(self,body='',name='公开 笔记.md'):return self.note(name,'---\npublish: true\n---\n'+body)
 def clean(self):
  for p in self.out.rglob('*'):
   if p.is_file():
    for c in CANARIES:self.assertNotIn(c.encode(),p.read_bytes());self.assertNotIn(c,str(p))
 def test_literal_boolean_only_and_legacy_not_consent(self):
  for i,fm in enumerate(['publish: false','publish: "true"','feed: show\npublished: true','title: missing','publish: null']):self.note(f'{i}.md',f'---\n{fm}\n---\nPRIVATE_BODY_8e71')
  self.public('Hello');r=export(self.v,self.out);self.assertEqual(r['selected_notes'],1);self.clean()
 def test_private_wikilinks_aliases_titles_and_embeds_fail_sanitized(self):
  for target in CANARIES[:4]:
   for prefix in ('','!'):
    with self.subTest(target=target,prefix=prefix):
     self.public(prefix+'[['+target+'|PRIVATE_ALIAS_8e71]]')
     with self.assertRaises(ExportError) as caught:export(self.v,self.out)
     for c in CANARIES:self.assertNotIn(c,str(caught.exception))
     self.assertFalse(self.out.exists())
 def test_markdown_private_links_and_alt_never_exported(self):
  for ref in ['[PRIVATE_ALIAS_8e71](PRIVATE_FILE_8e71.md)','![PRIVATE_ALIAS_8e71](PRIVATE_FILE_8e71.md)']:
   self.public(ref)
   with self.assertRaises(ExportError):export(self.v,self.out)
   self.assertFalse(self.out.exists())
 def test_referenced_media_only_names_and_metadata_sanitized(self):
  (self.v/'PRIVATE_ALIAS_8e71.png').write_bytes(png(b'PRIVATE_TITLE_8e71'));(self.v/'UNREFERENCED_8e71.png').write_bytes(png())
  self.public('![PRIVATE_ALIAS_8e71](PRIVATE_ALIAS_8e71.png)')
  r=export(self.v,self.out);self.assertEqual(r['selected_assets'],1);self.clean();self.assertEqual(len(list((self.out/'media').glob('*.png'))),1)
 def test_private_only_attachment_not_copied(self):
  (self.v/'UNREFERENCED_8e71.png').write_bytes(png());self.note('private.md','![[UNREFERENCED_8e71.png]]');self.public('Hello');r=export(self.v,self.out);self.assertEqual(r['selected_assets'],0);self.clean()
 def test_traversal_and_encoded_traversal_fail(self):
  (self.case/'escape.png').write_bytes(png())
  for target in ['../escape.png','%2e%2e/escape.png','/escape.png','file:///escape.png']:
   self.public('![]('+target+')')
   with self.assertRaises(ExportError):export(self.v,self.out)
 def test_symlink_escape_fails(self):
  (self.case/'escape.png').write_bytes(png());(self.v/'escape.png').symlink_to(self.case/'escape.png');self.public('![[escape.png]]')
  with self.assertRaises(ExportError):export(self.v,self.out)
 def test_ambiguous_basename_fails(self):
  self.public('[[same]]');self.public('a','a/same.md');self.public('b','b/same.md')
  with self.assertRaises(ExportError):export(self.v,self.out)
 def test_revocation_deletes_stale_notes_and_assets(self):
  (self.v/'image.png').write_bytes(png());p=self.public('![[image.png]]');export(self.v,self.out);p.write_text('private now');r=export(self.v,self.out);self.assertEqual(r['selected_notes'],0);self.assertEqual(sorted(p.name for p in (self.out/'notes').iterdir()),['index.md']);self.assertFalse((self.out/'media').exists())
 def test_failure_clears_previous_managed_output(self):
  self.public('okay');export(self.v,self.out);self.public('[[PRIVATE_FILE_8e71]]')
  with self.assertRaises(ExportError):export(self.v,self.out)
  self.assertFalse(self.out.exists())
 def test_chinese_space_filenames_and_selected_link(self):
  self.public('[[目录/另 一页|继续阅读]]');self.public('中文内容','目录/另 一页.md');r=export(self.v,self.out);self.assertEqual(r['selected_notes'],2);self.assertTrue((self.out/'notes/目录/另 一页.md').exists());self.clean()
 def test_code_examples_not_references(self):
  self.public('`[[not-a-note]]`\n\n```md\n![[no-asset.png]]\n```\n');self.assertEqual(export(self.v,self.out)['selected_notes'],1)
 def test_app_owned_notes_landing_collision_fails_closed(self):
  self.public('Selected index fixture','index.md')
  with self.assertRaises(ExportError):export(self.v,self.out)
  self.assertFalse(self.out.exists())
 def test_empty_selection_landing_only(self):
  r=export(self.v,self.out);self.assertEqual(r['selected_notes'],0);self.assertTrue((self.out/'index.md').exists());self.clean();self.assertEqual(sorted(p.name for p in self.out.iterdir()),['index.md','notes','publication.json'])
 def test_dry_run_does_not_touch_output(self):
  self.public('Hello');r=export(self.v,self.out,dry_run=True);self.assertEqual(r['selected_notes'],1);self.assertFalse(self.out.exists())
 def test_duplicate_frontmatter_and_unsafe_constructs_fail_closed(self):
  for body in ['---\npublish: true\npublish: false\n---\nx','---\npublish: true\n---\n<script>alert(1)</script>','---\npublish: true\n---\n[x][id]\n[id]: PRIVATE_FILE_8e71.md']:
   self.note('public.md',body)
   with self.assertRaises(ExportError):export(self.v,self.out)
 def test_output_marker_symlink_is_never_read(self):
  from unittest.mock import patch
  self.out.mkdir();target=self.case/'outside-marker';target.write_text('{"schema":"shulva-selective-v1"}');marker=self.out/'publication.json';marker.symlink_to(target)
  original=pathlib.Path.read_text;reads=[]
  def track(path,*a,**kw):
   reads.append(path);return original(path,*a,**kw)
  with patch.object(pathlib.Path,'read_text',track):
   with self.assertRaises(ExportError):export(self.v,self.out)
  self.assertNotIn(marker,reads)
 def test_integrity_rejects_injected_symlink_directory(self):
  from check_stage import check
  export(self.v,self.out);(self.out/'injected').symlink_to(self.v,target_is_directory=True)
  with self.assertRaises(ValueError):check(self.out)
 def test_unmanaged_output_not_deleted(self):
  self.out.mkdir();(self.out/'keep').write_text('keep')
  with self.assertRaises(ExportError):export(self.v,self.out)
  self.assertEqual((self.out/'keep').read_text(),'keep')
if __name__=='__main__':unittest.main(verbosity=2)
