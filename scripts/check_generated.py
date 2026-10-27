#!/usr/bin/env python3
"""Read a completed build only. Manifest contains public/private file,url entries."""
import argparse,json,re,subprocess,tempfile
from pathlib import Path
from urllib.parse import unquote,urlsplit

def check(build,manifest):
 root=Path(build).resolve();errors=[];html=list(root.rglob('*.html'))
 def locate(url):
  path=root/unquote(urlsplit(url).path).lstrip('/')
  return next((p for p in [path,path.with_suffix('.html'),path/'index.html'] if p.is_file()),None)
 search=root/'SearchData.json'
 try: data=json.loads(search.read_text());urls={unquote(x['url']).rstrip('/') for x in (data.values() if isinstance(data,dict) else data)}
 except (OSError,ValueError,KeyError,TypeError):urls=set();errors.append('missing or invalid SearchData.json')
 listing=locate('/notes');listing=unquote(listing.read_text()) if listing else ''
 for entry in manifest['public']:
  url=entry['url'];
  if not locate(url):errors.append('missing HTML: '+entry['file'])
  if unquote(url).rstrip('/') not in urls:errors.append('missing search: '+entry['file'])
  if unquote(url) not in listing:errors.append('missing notes listing: '+entry['file'])
 for entry in manifest['private']:
  if locate(entry['url']) or unquote(entry['url']).rstrip('/') in urls or entry['url'] in listing:errors.append('private exposed: '+entry['file'])
 scripts=0
 for path in html:
  text=path.read_text()
  if re.search(r'Your Name|fonts\.googleapis|fonts\.gstatic',text):errors.append('template/Google: '+str(path.relative_to(root)))
  for target in re.findall(r'(?:src|href)=[\'"]([^\'"]+)',text):
   parsed=urlsplit(target)
   if parsed.scheme or target.startswith('//') or not parsed.path:continue
   decoded=unquote(parsed.path)
   if Path(decoded).suffix.lower() not in {'.js','.css','.png','.jpg','.jpeg','.svg','.gif','.webp','.ico','.woff','.woff2','.pdf'}:continue
   dest=root/decoded.lstrip('/') if decoded.startswith('/') else path.parent/decoded
   if not dest.is_file():errors.append('missing resource: '+str(path.relative_to(root))+' -> '+target)
  for attrs,code in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',text,re.S|re.I):
   if 'src=' in attrs or ('type=' in attrs and not re.search(r'type=[\'"](?:module|text/javascript)',attrs)):continue
   scripts+=1
   with tempfile.NamedTemporaryFile(suffix='.js',mode='w') as f:
    f.write(code);f.flush();r=subprocess.run(['node','--check',f.name],capture_output=True)
   if r.returncode:errors.append('invalid built JS: '+str(path.relative_to(root)))
 return {'html_count':len(html),'inline_scripts_checked':scripts,'errors':sorted(set(errors))}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args();result=check(a.build,json.loads(a.manifest.read_text()));serialized=json.dumps(result,ensure_ascii=False,indent=2)
 if a.output:a.output.write_text(serialized+'\n')
 else:print(serialized)
 raise SystemExit(bool(result['errors']))
