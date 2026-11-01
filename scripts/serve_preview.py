#!/usr/bin/env python3
"""Loopback-only Quartz preview with exact .html fallback, no SPA catch-all."""
import argparse,pathlib
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
class PreviewHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def translate_path(self,path):
  root=pathlib.Path(self.directory).resolve();target=pathlib.Path(super().translate_path(path))
  if not target.exists() and not target.name.endswith('.html'):
   candidate=target.with_name(target.name+'.html')
   if candidate.is_file():target=candidate
  if not target.resolve().is_relative_to(root):raise PermissionError('outside preview root')
  return str(target)
 def send_head(self):
  try:return super().send_head()
  except PermissionError:self.send_error(404);return None
 def list_directory(self,path):self.send_error(404);return None

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=pathlib.Path,required=True);parser.add_argument('--bind',choices=['127.0.0.1'],default='127.0.0.1');parser.add_argument('--port',type=int,default=8080);args=parser.parse_args();root=args.directory.resolve()
 if not (root/'index.html').is_file() or any(p.is_symlink() for p in root.rglob('*')):raise SystemExit('A real sanitized, symlink-free build is required')
 from functools import partial
 server=ThreadingHTTPServer((args.bind,args.port),partial(PreviewHandler,directory=str(root)))
 print(f'Quartz preview: http://{args.bind}:{args.port}/ (Ctrl-C stops)',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
