#!/usr/bin/env python3
"""Exercise generated local links through actual HTTP handlers, without port binding.
Complements disk checks; browser/live-server acceptance is still required.
"""
import io,pathlib,json,sys
from urllib.parse import urljoin,urlsplit,quote
from check_resources import References,check as check_disk
from serve_preview import PreviewHandler
class MemorySocket:
 def __init__(self,raw):self.raw=io.BytesIO(raw);self.response=bytearray()
 def makefile(self,*a,**kw):return self.raw
 def sendall(self,data):self.response.extend(data)
def response(root,path,handler=PreviewHandler):
 sock=MemorySocket(('GET '+path+' HTTP/1.0\r\nHost: localhost\r\n\r\n').encode('ascii'))
 handler(sock,('127.0.0.1',1),object(),directory=str(root));return bytes(sock.response)
def check(root,handler=PreviewHandler):
 root=pathlib.Path(root).resolve();disk=check_disk(root);requests=0
 for page in root.rglob('*.html'):
  parser=References();parser.feed(page.read_text());origin='/'+page.relative_to(root).as_posix()
  for value,_ in parser.refs:
   if not value or value.startswith(('#','data:','mailto:','tel:')) or urlsplit(value).scheme or urlsplit(value).netloc:continue
   route=urljoin(origin,value);path=urlsplit(route).path;path=quote(path,safe='/%')
   for attempt in range(4):
    raw=response(root,path,handler);requests+=1;headers=raw.split(b'\r\n\r\n',1)[0].decode('latin1');status=int(headers.split(' ',2)[1])
    if status==200:break
    if status in (301,302,307,308):
     location=next((line.split(':',1)[1].strip() for line in headers.split('\r\n') if line.lower().startswith('location:')),None)
     if location and not urlsplit(location).netloc and not urlsplit(location).scheme:path=urljoin(path,location);continue
    raise ValueError('HTTP route acceptance failed with status '+str(status))
   else:raise ValueError('HTTP route redirect limit')
 return {**disk,'http_handler_requests':requests,'http_route_errors':0,'live_socket_used':False,'handler':handler.__name__}
if __name__=='__main__':
 handler=PreviewHandler
 if '--original' in sys.argv:
  from http.server import SimpleHTTPRequestHandler
  class Original(SimpleHTTPRequestHandler):
   def log_message(self,*a):pass
  handler=Original
 print(json.dumps(check(sys.argv[1] if len(sys.argv)>1 else 'public',handler)))
