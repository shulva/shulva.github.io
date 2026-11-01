"""Run the real Quartz compiler, then scan staged sources and every emitted file."""
import pathlib,sys,os,tempfile,subprocess,json
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from selective_export import export
from test_selective_export import png,CANARIES
from check_resources import check
from check_http_routes import check as check_http
base=pathlib.Path(os.environ['TEST_SCRATCH']).resolve()
if base==ROOT or ROOT in base.parents:raise RuntimeError('private fixtures must be outside checkout')
case=pathlib.Path(tempfile.mkdtemp(prefix='real-build-',dir=base));vault=case/'vault';vault.mkdir()
(vault/'PRIVATE_FILE_8e71.md').write_text('---\ntitle: PRIVATE_TITLE_8e71\naliases: [PRIVATE_ALIAS_8e71]\n---\nPRIVATE_BODY_8e71')
(vault/'UNREFERENCED_8e71.png').write_bytes(png())
(vault/'PRIVATE_ALIAS_8e71.png').write_bytes(png(b'PRIVATE_TITLE_8e71'))
(vault/'公开 笔记.md').write_text('---\npublish: true\n---\n> [!tip] Synthetic acceptance fixture\n> Not a user note.\n\n$E=mc^2$\n\n[[中文 路径|继续阅读]]\n\n![PRIVATE_ALIAS_8e71](PRIVATE_ALIAS_8e71.png)\n')
(vault/'中文 路径.md').write_text('---\npublish: true\n---\nSynthetic Chinese target.\n')
stage=case/'content';artifact=case/'public';counts=export(vault,stage)
subprocess.run([sys.executable,str(ROOT/'scripts/site-build.py'),str(stage),str(artifact)],check=True,cwd=ROOT)
for tree in (stage,artifact):
 for path in tree.rglob('*'):
  if path.is_file():
   for canary in CANARIES:
    if canary in str(path) or canary.encode() in path.read_bytes():raise AssertionError('private canary in real staged/generated output')
if not (artifact/'static/contentIndex.json').is_file():raise AssertionError('missing real search/graph contentIndex')
index=json.loads((artifact/'static/contentIndex.json').read_text())
if not any('公开' in k for k in index):raise AssertionError('missing real generated Chinese search/graph entry')
result={'fixture':'synthetic, outside public checkout','export':counts,'checks':check(artifact),'http_routes':check_http(artifact),'search_graph_entries':len(index),'artifact':str(artifact)}
(case/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
