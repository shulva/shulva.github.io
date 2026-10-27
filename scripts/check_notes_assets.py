#!/usr/bin/env python3
"""Read-only inventory. Missing private attachments are reported, never fetched.
Wiki names are matched by basename/path; fragments and aliases are ignored.
Markdown links inside code fences may appear in this conservative inventory.
"""
import json,re,argparse
from pathlib import Path
from urllib.parse import unquote,urlsplit

def scan(root):
 root=Path(root).resolve();notes=list((root/'_notes').rglob('*.md'))
 files=[p for p in root.rglob('*') if p.is_file() and not any(x in p.relative_to(root).parts for x in ['.git','vendor','_site'])]
 names={p.stem.casefold() for p in notes};allnames={p.name.casefold() for p in files}
 routes={'/','/SearchData.json'}
 for p in files:
  if p.suffix in ['.md','.html']:
   m=re.search(r'(?m)^permalink:\s*[\'"]?([^\s\'"]+)',p.read_text(errors='replace'))
   if m:routes.add(m.group(1).rstrip('/') or '/')
 out={k:[] for k in ['unresolved_wiki','missing_note_attachments','missing_local_assets','missing_template_targets']}
 for p in files:
  if p.suffix.lower() not in ['.md','.html','.css']:continue
  text=p.read_text(errors='replace');rel=str(p.relative_to(root));isnote=rel.startswith('_notes/')
  def add(key,target):out[key].append({'source':rel,'target':target})
  if isnote:
   for embed,target in re.findall(r'(!?)\[\[([^\]]+)\]\]',text):
    target=target.split('|')[0].split('#')[0].strip()
    if not target:continue
    if embed and Path(target).suffix:
     if Path(target).name.casefold() not in allnames:add('missing_note_attachments',target)
    elif Path(target).stem.casefold() not in names:add('unresolved_wiki',target)
  targets=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text)
  targets+=re.findall(r'(?:src|href)=[\'"]([^\'"]+)',text)
  if p.suffix=='.css':targets+=re.findall(r'url\([\'"]?([^\)\'\"]+)',text)
  for target in targets:
   target=target.replace('{{ site.baseurl }}','').replace('{{site.baseurl}}','').strip('<> ')
   if '{{' in target or '{%' in target or urlsplit(target).scheme or target.startswith('//'):continue
   path=unquote(urlsplit(target).path)
   if not path:continue
   dest=root/path.lstrip('/') if path.startswith('/') else p.parent/path
   if dest.exists() or (path.rstrip('/') or '/') in routes:continue
   add('missing_note_attachments' if isnote else 'missing_local_assets' if Path(path).suffix else 'missing_template_targets',target)
 out['counts']={'notes':len(notes),'without_front_matter':sum(not p.read_bytes().startswith(b'---\n') for p in notes),**{k:len(v) for k,v in out.items()}}
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default='.');p.add_argument('--output',type=Path);a=p.parse_args();data=scan(a.root);result=json.dumps(data,ensure_ascii=False,indent=2)
 if a.output:a.output.write_text(result+'\n')
 else:print(result)
