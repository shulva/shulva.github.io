#!/usr/bin/env python3
"""Fail-closed Obsidian export. Diagnostics intentionally omit source identifiers."""
import argparse,hashlib,json,os,pathlib,re,shutil,struct,zlib
from urllib.parse import unquote,urlsplit,quote
import yaml
class ExportError(Exception):pass
class UniqueLoader(yaml.SafeLoader):pass
def mapping(loader,node,deep=False):
 result={}
 for key,value in node.value:
  k=loader.construct_object(key,deep=deep)
  if not isinstance(k,str) or k in result or k=='<<':raise ExportError('E_METADATA: unsupported or duplicate metadata')
  result[k]=loader.construct_object(value,deep=deep)
 return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
CV_SOURCE=pathlib.Path(__file__).resolve().parents[1]/'cv.md'
def read_cv():
 # Check the lexical path before resolving: no symlink source or ancestor.
 path=CV_SOURCE.absolute()
 try:
  if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():
   fail('E_CV: missing or unsafe repository-root cv.md')
  data=path.read_bytes()
  data.decode('utf-8')
  return data
 except ExportError:raise
 except Exception:fail('E_CV: missing or unsafe repository-root cv.md')
LANDING='''---
title: Shulva · 知识花园
---
# 留一点空间，慢慢生长

这里收集经过明确选择、愿意公开分享的学习与思考。

> [!info] 当前没有选中的用户笔记
> 所有笔记默认私密。只有 YAML 中明确写入布尔值 `publish: true` 的笔记，才会进入发布流程。旧的展示设置不代表公开授权。

## 如何更新

在 Obsidian 中逐篇审核正文、链接与图片，再明确选择需要公开的笔记。先进行本地预检，检查导出内容与预览，最后再决定是否发布。

公开笔记指向未公开笔记时，导出会停止，并给出不含私人名称的错误。笔记撤回选择后，下一次导出会移除旧页面及不再引用的附件。

*Shulva · 用自己的节奏整理知识。*
'''
def fail(code):raise ExportError(code)
def metadata(text):
 if not text.startswith('---\n'):return {},text
 end=re.search(r'^---\s*$',text[4:],re.M)
 if end is None:fail('E_METADATA: unclosed frontmatter')
 try:data=yaml.load(text[4:4+end.start()],Loader=UniqueLoader)
 except Exception:fail('E_METADATA: unsupported metadata')
 if data is None:data={}
 if not isinstance(data,dict):fail('E_METADATA: expected mapping')
 return data,text[4+end.end():].lstrip('\r\n')
def safe_png(data):
 if not data.startswith(b'\x89PNG\r\n\x1a\n'):fail('E_ASSET: unsupported image')
 out=data[:8];pos=8;types=[]
 while pos<len(data):
  if pos+12>len(data):fail('E_ASSET: invalid PNG')
  n=struct.unpack('>I',data[pos:pos+4])[0];t=data[pos+4:pos+8];end=pos+12+n
  if end>len(data) or n>20_000_000:fail('E_ASSET: invalid PNG')
  payload=data[pos+8:pos+8+n];crc=struct.unpack('>I',data[pos+8+n:end])[0]
  if zlib.crc32(t+payload)&0xffffffff!=crc:fail('E_ASSET: invalid PNG')
  types.append(t)
  if t in (b'IHDR',b'PLTE',b'IDAT',b'IEND',b'tRNS'):out+=data[pos:end]
  elif t[:1].isupper():fail('E_ASSET: unsupported PNG chunk')
  pos=end
 if not types or types[0]!=b'IHDR' or types[-1]!=b'IEND' or b'IDAT' not in types:fail('E_ASSET: invalid PNG')
 return out
def protected_parts(body):
 # Fenced/indented code and inline code are literal examples, never reference sources.
 parts=[];plain=[];lines=body.splitlines(keepends=True);i=0
 def flush():
  if plain:parts.append((False,''.join(plain)));plain.clear()
 while i<len(lines):
  line=lines[i];fence=re.match(r'^ {0,3}(`{3,}|~{3,})',line)
  if fence:
   flush();mark=fence.group(1);block=[line];i+=1;closed=False
   while i<len(lines):
    block.append(lines[i]);closed=bool(re.match(r'^ {0,3}'+re.escape(mark[0])+'{'+str(len(mark))+r',}\s*$',lines[i]));i+=1
    if closed:break
   if not closed:fail('E_MARKDOWN: unclosed code fence')
   parts.append((True,''.join(block)));continue
  if line.startswith('    ') or line.startswith('\t'):flush();parts.append((True,line));i+=1;continue
  plain.append(line);i+=1
 flush();result=[]
 for literal,text in parts:
  if literal:result.append((True,text));continue
  start=0
  for match in re.finditer(r'(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)',text):
   result.append((False,text[start:match.start()]));result.append((True,match.group()));start=match.end()
  result.append((False,text[start:]))
 return result
def export(vault,output,dry_run=False):
 vault=pathlib.Path(vault).absolute();output=pathlib.Path(output).absolute()
 if vault.resolve()!=vault or not vault.is_dir() or output.resolve()!=output:fail('E_PATH: symlink or missing root')
 if vault==output or vault in output.parents or output in vault.parents:fail('E_PATH: overlapping roots')
 marker=output/'publication.json'
 if output.exists():
  if any(p.is_symlink() for p in output.rglob('*')):fail('E_OUTPUT: unsafe destination')
  try:managed=json.loads(marker.read_text()).get('schema')=='shulva-selective-v1'
  except Exception:managed=False
  if not managed or any(p.is_symlink() for p in output.rglob('*')):fail('E_OUTPUT: unmanaged destination')
  if not dry_run:shutil.rmtree(output)
 notes={};selected={};assets={};rendered={}
 try:
  cv=read_cv()
  for root,dirs,files in os.walk(vault,followlinks=False):
   dirs[:]=[d for d in dirs if not d.startswith('.') and d not in ('node_modules','config','secrets') and not (pathlib.Path(root)/d).is_symlink()]
   for name in files:
    path=pathlib.Path(root)/name
    if name.startswith('.') or path.suffix.lower()!='.md' or path.is_symlink():continue
    # Only frontmatter is read for unselected notes; private bodies are never loaded.
    with path.open(encoding='utf-8-sig') as handle:
     first=handle.readline();header=first
     if first.strip()=='---':
      for index,line in enumerate(handle):
       header+=line
       if line.strip()=='---':break
       if index>=199:fail('E_METADATA: frontmatter limit')
     else:header=''
    meta,_=metadata(header)
    rel=path.relative_to(vault).as_posix();notes[rel]=meta
    # Exact literal true is additionally required: YAML 1.1 yes/on cannot grant consent.
    if meta.get('publish') is True and re.search(r'^publish: +true\s*(?:#.*)?$',header,re.M):
     selected[rel]=metadata(path.read_text(encoding='utf-8-sig'))[1]
  def path_target(raw):
   value=unquote(raw.strip())
   if any(x in value for x in ('\\','\0','\n','\r')):fail('E_REFERENCE: unsafe target')
   value=value.split('#',1)[0]
   if value.startswith('/') or '..' in value.split('/') or any(x.startswith('.') for x in value.split('/')):fail('E_REFERENCE: unsafe target')
   return value
  def resolve_note(target,current):
   target=path_target(target)
   if not target:return current
   if not target.endswith('.md'):target+='.md'
   options={target,(pathlib.PurePosixPath(current).parent/target).as_posix()}
   candidates={n for n in notes if n in options or ('/' not in target and pathlib.PurePosixPath(n).name==target)}
   if len(candidates)!=1 or not candidates<=selected.keys():fail('E_REFERENCE: target is not uniquely approved')
   return next(iter(candidates))
  def image(raw,current):
   target=path_target(raw)
   if urlsplit(target).scheme or pathlib.PurePosixPath(target).suffix.lower()!='.png':fail('E_ASSET: only local PNG attachments supported')
   candidates=[]
   for rel in {target,(pathlib.PurePosixPath(current).parent/target).as_posix()}:
    p=vault/rel
    if p.is_file():candidates.append(p)
   if len(candidates)!=1:fail('E_ASSET: attachment must resolve uniquely')
   p=candidates[0]
   if p.resolve()!=p or not p.is_relative_to(vault) or any(x.startswith('.') for x in p.relative_to(vault).parts):fail('E_ASSET: unsafe attachment path')
   if p.stat().st_size>20_000_000:fail('E_ASSET: attachment size limit')
   data=safe_png(p.read_bytes());name='media/'+hashlib.sha256(data).hexdigest()+'.png';assets[name]=data
   # Remove source filename and all author-provided alt/title text from public metadata.
   return '![image]('+quote('../'*(len(pathlib.PurePosixPath(current).parts))+name,safe='/')+')'
  for current,body in selected.items():
   pieces=[]
   for literal,text in protected_parts(body):
    if literal:pieces.append(text);continue
    if '<' in text or re.search(r'^\s*\[[^\]]+\]:',text,re.M):fail('E_MARKDOWN: raw HTML or reference-style links unsupported')
    def wiki(match):
     embed,target=match.group(1),match.group(2);target,*alias=target.split('|',1)
     if pathlib.PurePosixPath(target.split('#',1)[0]).suffix.lower()=='.png':return image(target,current)
     dest=resolve_note(target,current)
     if embed:fail('E_REFERENCE: note embeds require manual rewriting')
     label=alias[0] if alias else pathlib.PurePosixPath(dest).stem
     if any(x in label for x in '[]<>'):fail('E_REFERENCE: unsupported link label')
     relative=os.path.relpath('notes/'+dest,'notes/'+str(pathlib.PurePosixPath(current).parent))
     return '['+label+']('+quote(relative,safe='/')+')'
    # Process ordinary inline links; wiki replacements have already resolved selected notes.
    def inline(match):
     embed,label,raw=match.groups();target=raw.strip()
     if target.startswith('<') or '"' in target or "'" in target:fail('E_REFERENCE: link titles/angle targets unsupported')
     parsed=urlsplit(unquote(target))
     if parsed.scheme:
      if embed or parsed.scheme not in ('https','http','mailto'):fail('E_REFERENCE: unsupported external reference')
      return match.group()
     if embed:return image(target,current)
     if target.startswith('#'):return match.group()
     dest=resolve_note(unquote(target),current)
     relative=os.path.relpath('notes/'+dest,'notes/'+str(pathlib.PurePosixPath(current).parent))
     return '['+label+']('+quote(relative,safe='/')+')'
    text=re.sub(r'(?<!\\)(!?)\[([^\]\n]*)\]\(([^)\n]+)\)',inline,text)
    text=re.sub(r'(?<!\\)(!?)\[\[([^\]\n]+)\]\]',wiki,text)
    if re.search(r'(?<!\\)\[\[|!\[|\]\(',re.sub(r'(?<!\\)!?\[[^\]\n]*\]\([^\n)]*\)','',text)):fail('E_MARKDOWN: unsupported reference syntax')
    pieces.append(text)
   rendered['notes/'+current]='---\ntitle: '+json.dumps(pathlib.PurePosixPath(current).stem,ensure_ascii=False)+'\n---\n'+''.join(pieces)
  landing=LANDING if not selected else LANDING.replace('当前没有选中的用户笔记',f'当前明确选中了 {len(selected)} 篇用户笔记')
  if 'notes/index.md' in rendered:fail('E_ROUTE: selected note conflicts with app-owned landing')
  payload={'index.md':cv,'notes/index.md':landing,**rendered,**assets}
  receipt={'cv_source':{'mode':'repository-root-cv-v1','sha256':hashlib.sha256(cv).hexdigest()},'schema':'shulva-selective-v1','selected_notes':len(selected),'selected_assets':len(assets),'default_private':True,'files':{name:hashlib.sha256(data.encode() if isinstance(data,str) else data).hexdigest() for name,data in payload.items()}}
  if not dry_run:
   output.mkdir(parents=True,exist_ok=False)
   for name,data in payload.items():
    dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,str):dest.write_text(data)
    else:dest.write_bytes(data)
   marker.write_text(json.dumps(receipt,indent=2)+'\n')
  return receipt
 except ExportError:
  if not dry_run and output.exists():shutil.rmtree(output)
  raise
 except Exception:
  if not dry_run and output.exists():shutil.rmtree(output)
  raise ExportError('E_EXPORT: export stopped; no source identifiers disclosed') from None
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('vault',type=pathlib.Path);parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path('content'));parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
 try:print(json.dumps(export(args.vault,args.output,args.dry_run),ensure_ascii=False))
 except ExportError as error:print(str(error));raise SystemExit(2)
if __name__=='__main__':main()
