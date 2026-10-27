#!/usr/bin/env python3
"""Read a completed build only. Manifest contains public/private file,url entries."""
import argparse,json,re,subprocess,tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit

class ResourceAttributes(HTMLParser):
 # Keep targets unchanged for the missing-resource and inventory contracts.
 google_attributes={
  'src':{'audio','embed','iframe','img','input','script','source','track','video','frame'},
  'href':{'a','area','base','link','image','use'},
  'srcset':{'img','source'},'imagesrcset':{'link'},'poster':{'video'},'data':{'object'},
  'background':{'body','table','td','th'},'manifest':{'html'},'code':{'applet'},
  'codebase':{'applet','object'},'archive':{'applet','object'},'classid':{'object'},
  'profile':{'head'},'ping':{'a','area'},'longdesc':{'img','iframe','frame'},
  'lowsrc':{'img'},'dynsrc':{'img'},'action':{'form'},'formaction':{'button','input'},
  'cite':{'blockquote','q','del','ins'},'usemap':{'img','input','object'},
  'icon':{'command'},'xlink:href':{'image','use','script','a','feimage'}}
 def __init__(self,text):
  super().__init__();self.targets=[];self.google_targets=[];self.styles=[];self.stylesheets=[];self.in_style=False;self.feed(text)
 def handle_starttag(self,tag,attrs):
  self.targets.extend(value for name,value in attrs if name in {"src","href"} and value)
  self.google_targets.extend(value for name,value in attrs if tag in self.google_attributes.get(name,set()) and value)
  self.styles.extend(value for name,value in attrs if name=='style' and value)
  if tag=='style':self.in_style=True
  attributes=dict(attrs)
  if tag=='link' and 'stylesheet' in (attributes.get('rel') or '').lower().split() and attributes.get('href'):
   self.stylesheets.append(attributes['href'])
 def handle_endtag(self,tag):
  if tag=='style':self.in_style=False
 def handle_data(self,data):
  if self.in_style:self.styles.append(data)

def has_google_resources(resources,path,root):
 """Inspect resource attributes and active CSS, never rendered HTML text."""
 google=re.compile(r'fonts\.googleapis|fonts\.gstatic',re.I)
 if any(google.search(target) for target in resources.google_targets):return True
 pending=[(target,path) for target in resources.stylesheets];seen=set()
 def inspect_css(css,source):
  # Tokenize strings/comments before looking for functions so examples in content
  # strings cannot masquerade as resource requests. Track nested image-set calls.
  # Preserve raw escape boundaries while scanning; decode only semantic values.
  escape=r'\\(?:[0-9a-f]{1,6}(?:\r\n|[ \t\r\n\f])?|\r\n|.)'
  string=r'"(?:'+escape+r'|[^"\\\r\n\f])*"|\x27(?:'+escape+r'|[^\x27\\\r\n\f])*\x27'
  gap=r'(?:\s|/\*.*?\*/)*'
  # Recognize escaped spellings without decoding the surrounding CSS syntax.
  url_name=''.join(r'(?:'+c+r'|\\'+c+r'|\\0{0,4}(?:'+format(ord(c),'x')+'|'+format(ord(c.upper()),'x')+r')(?:\r\n|[ \t\r\n\f])?)' for c in 'url')
  name_escape=r'\\(?:[0-9a-f]{1,6}(?:\r\n|[ \t\r\n\f])?|[^\r\n\f0-9a-f])'
  prefix=r'(?:@import\b'+gap+r'(?=["\x27]|'+url_name+r'\()(?:'+url_name+r'\(\s*)?|'+url_name+r'\(\s*)'
  token=re.compile(r'(?P<comment>/\*.*?(?:\*/|\Z))|(?P<request>'+prefix+r'(?:'+string+r'|(?:'+escape+r'|[^\s)\x27";\\])+))|(?P<function>(?:'+name_escape+r'|[-\w])+\()|(?P<string>'+string+r')|(?P<paren>[()])',re.I|re.S)
  def decode(value):
   def replace(match):
    raw=match.group()[1:]
    digits=re.match(r'[0-9a-f]{1,6}',raw,re.I)
    if digits:
     point=int(digits.group(),16)
     return chr(point) if 0<point<=0x10ffff and not 0xd800<=point<=0xdfff else '\ufffd'
    return '' if raw in {'\n','\r','\r\n','\f'} else raw
   return re.sub(escape,replace,value,flags=re.I|re.S)
  stack=[]
  for match in token.finditer(css):
   target=None
   if match.lastgroup=='comment':continue
   if match.lastgroup=='function':stack.append(decode(match.group()[:-1]).lower());continue
   if match.lastgroup=='paren':
    if match.group()=='(':stack.append('')
    elif stack:stack.pop()
    continue
   if match.lastgroup=='request':
    target=re.sub('^'+prefix,'',match.group(),flags=re.I|re.S)
    if target[:1] in {'"',"'"}:target=target[1:-1]
    # The request token consumes url( but leaves its closing parenthesis.
    if re.match(r'(?:@import\b'+gap+r')?'+url_name+r'\(',match.group(),re.I|re.S):stack.append('url')
   elif match.lastgroup=='string' and stack and stack[-1] in {'image-set','-webkit-image-set'}:
    target=match.group()[1:-1]
   if target is None:continue
   target=decode(target)
   if google.search(target):return True
   if match.group().lower().startswith('@import') or urlsplit(target).path.lower().endswith('.css'):
    pending.append((target,source))
  return False
 for css in resources.styles:
  if inspect_css(css,path):return True
 while pending:
  target,source=pending.pop();parsed=urlsplit(target)
  if parsed.scheme or target.startswith('//') or not parsed.path:continue
  decoded=unquote(parsed.path)
  stylesheet=(root/decoded.lstrip('/') if decoded.startswith('/') else source.parent/decoded).resolve()
  if not stylesheet.is_relative_to(root) or stylesheet in seen or not stylesheet.is_file():continue
  seen.add(stylesheet)
  if inspect_css(stylesheet.read_text(),stylesheet):return True
 return False

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
  resources=ResourceAttributes(text)
  if re.search(r'Your Name',text) or has_google_resources(resources,path,root):errors.append('template/Google: '+str(path.relative_to(root)))
  for target in resources.targets:
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
