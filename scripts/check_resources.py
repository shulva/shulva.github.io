#!/usr/bin/env python3
"""Check real generated HTML/CSS resources and local links. No browser simulation."""
import pathlib,json,re,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
class References(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for key in ('href','src','poster'):
   if key in a:self.refs.append((a[key],tag!='a'))
def check(root):
 root=pathlib.Path(root).resolve();html=list(root.rglob('*.html'));errors=[];count=0
 if not html:raise ValueError('no generated HTML')
 def reference(value,page,active):
  nonlocal count
  if not value:return
  if value.startswith(('data:','#','mailto:','tel:')):return
  url=urlsplit(value)
  if url.scheme or url.netloc:
   if active:errors.append('external active resource')
   return
  target=(root/unquote(url.path.lstrip('/'))) if url.path.startswith('/') else page.parent/unquote(url.path)
  if not url.path:return
  count+=1
  candidates=[target,target.with_suffix('.html'),target/'index.html']
  if not any(x.is_file() and x.resolve().is_relative_to(root) for x in candidates):errors.append('missing local resource/link')
 for page in html:
  parser=References();parser.feed(page.read_text())
  for value,active in parser.refs:reference(value,page,active)
 for page in root.rglob('*.css'):
  for value in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',page.read_text()):reference(value,page,True)
 for p in list(root.rglob('*.html'))+list(root.rglob('*.css')):
  text=p.read_text()
  if re.search(r'(?:https?:)?//(?:fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com)',text):errors.append('external font/CDN request')
 if errors:raise ValueError(json.dumps({'errors':len(errors),'kinds':sorted(set(errors))}))
 return {'html_pages':len(html),'local_references_checked':count,'resource_errors':0}
if __name__=='__main__':print(json.dumps(check(sys.argv[1] if len(sys.argv)>1 else 'public')))
