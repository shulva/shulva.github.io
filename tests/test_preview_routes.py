"""Exercise real HTTP handler requests with an in-memory socket; never binds a port."""
import pathlib,tempfile,os,sys,io,unittest,functools
from http.server import SimpleHTTPRequestHandler
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from serve_preview import PreviewHandler
SCRATCH=pathlib.Path(os.environ['TEST_SCRATCH'])
class MemorySocket:
 def __init__(self,request):self.request=io.BytesIO(request);self.response=bytearray()
 def makefile(self,*args,**kwargs):return self.request
 def sendall(self,data):self.response.extend(data)
class QuietOriginal(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def request(handler,root,path):
 sock=MemorySocket(('GET '+path+' HTTP/1.0\r\nHost: localhost\r\n\r\n').encode('ascii'))
 handler(sock,('127.0.0.1',1),object(),directory=str(root));return bytes(sock.response)
class Routes(unittest.TestCase):
 def setUp(self):
  self.root=pathlib.Path(tempfile.mkdtemp(prefix='http-contract-',dir=SCRATCH));(self.root/'demo').mkdir();(self.root/'index.html').write_text('landing');(self.root/'demo/公开演示.html').write_text('demo route');(self.root/'index.css').write_text('body{}')
 def test_original_server_reproduces_real_404(self):self.assertIn(b' 404 ',request(QuietOriginal,self.root,'/demo/%E5%85%AC%E5%BC%80%E6%BC%94%E7%A4%BA').split(b'\r\n')[0])
 def test_extensionless_chinese_route_http200(self):
  response=request(PreviewHandler,self.root,'/demo/%E5%85%AC%E5%BC%80%E6%BC%94%E7%A4%BA');self.assertIn(b' 200 ',response.split(b'\r\n')[0]);self.assertTrue(response.endswith(b'demo route'))
 def test_existing_html_query_and_static_still_http200(self):
  for path in ['/demo/%E5%85%AC%E5%BC%80%E6%BC%94%E7%A4%BA.html?check=1','/index.css','/']:
   self.assertIn(b' 200 ',request(PreviewHandler,self.root,path).split(b'\r\n')[0])
 def test_unknown_route_stays404_not_spa_success(self):self.assertIn(b' 404 ',request(PreviewHandler,self.root,'/missing').split(b'\r\n')[0])
 def test_symlink_escape_and_directory_listing_denied(self):
  target=self.root.parent/(self.root.name+'-outside.html');target.write_text('OUTSIDE_HTTP_CANARY');(self.root/'escape.html').symlink_to(target);(self.root/'listing').mkdir()
  for path in ['/escape','/listing/']:
   response=request(PreviewHandler,self.root,path);self.assertIn(b' 404 ',response.split(b'\r\n')[0]);self.assertNotIn(b'OUTSIDE_HTTP_CANARY',response)
if __name__=='__main__':unittest.main(verbosity=2)
