#!/usr/bin/env python3
"""Explicit selection only; dry-run unless --write. Publication requires --publish and --write."""
import argparse,json,re
from pathlib import Path

def repair(text,title,publish=False):
 h=re.search(r"(?m)^# +(.+?)\s*$",text)
 title=h.group(1).strip() if h else title
 m=re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)',text,re.S)
 if m:
  yaml=m.group(1)
  flags = dict(re.findall(r'(?im)^\s*(private|publish|published|feed)\s*:\s*([^\n#]+)',yaml))
  flags = {k.lower():v.strip().strip("\"'").lower() for k,v in flags.items()}
  if flags.get('private') in ('true','yes') or any(flags.get(k) in ('false','no') for k in ('publish','published')) or flags.get('feed')=='hide':return text
  # Repair only known malformed keys; keep all other YAML and the body byte-for-byte.
  yaml=re.sub(r'(?m)^(title|feed):(?=\S)',r'\1: ',yaml)
  if not re.search(r'(?m)^title\s*:',yaml):yaml+='\ntitle: '+json.dumps(title,ensure_ascii=False)
  if publish:
   for key,value in [('published','true'),('feed','show')]:
    if re.search(r'(?m)^'+key+r'\s*:',yaml):yaml=re.sub(r'(?m)^'+key+r'\s*:[^\r\n]*',key+': '+value,yaml)
    else:yaml+='\n'+key+': '+value
  newline='\r\n' if '\r\n' in text[:m.end()] else '\n'
  yaml=yaml.replace('\r\n','\n').replace('\n',newline)
  return text[:m.start(1)]+yaml+text[m.end(1):]
 if publish:return '---\ntitle: '+json.dumps(title,ensure_ascii=False)+'\npublished: true\nfeed: show\n---\n'+text
 return '---\ntitle: '+json.dumps(title,ensure_ascii=False)+'\npublished: false\nfeed: hide\n---\n'+text

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default='_notes');p.add_argument('--file',action='append',default=[]);p.add_argument('--allowlist',type=Path);p.add_argument('--publish',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
 root=Path(a.root).resolve();names=a.file+(a.allowlist.read_text().splitlines() if a.allowlist else [])
 for name in names:
  if not name.strip() or name.startswith('#'):continue
  f=(root/name).resolve()
  if not f.is_relative_to(root) or f.suffix.lower()!='.md':p.error('selection must be Markdown inside root')
  raw=f.read_bytes();old=raw.decode('utf-8');new=repair(old,f.stem,publish=a.publish)
  print(json.dumps({'file':name,'changed':old!=new,'write':a.write},ensure_ascii=False))
  if a.write and old!=new:f.write_bytes(new.encode('utf-8'))
if __name__=='__main__':main()
