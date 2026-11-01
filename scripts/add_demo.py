#!/usr/bin/env python3
"""Add only a first-party-authored public demonstration. Never reads a vault."""
import pathlib,struct,zlib,hashlib,json,sys
from check_stage import check

def illustration():
 w,h=360,120;rows=[]
 for y in range(h):
  row=bytearray()
  for x in range(w):
   color=(241,246,240)
   if 40<=x<=320 and 57<=y<=63:color=(146,178,154)
   for cx in (60,180,300):
    if (x-cx)**2+(y-60)**2<25**2:color=(53,107,96)
    if (x-cx)**2+(y-60)**2<12**2:color=(222,234,209)
   row.extend(color)
  rows.append(b'\0'+row)
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
def add(root):
 root=pathlib.Path(root);check(root);manifest=json.loads((root/'publication.json').read_text())
 files={
  'demo/公开演示.md':'''---
title: 公开演示 · 非用户笔记
---
这是一篇为迁移验证新写的公开示例，不来自 Shulva 的私人笔记库。

> [!tip] 先选择，再分享
> 真实笔记默认私密。这里仅演示排版与功能，不代表任何笔记已获公开授权。

## 从想法到理解

![本地学习流程示意](./learning.png)

每次学习，都可以留下一条可验证的联系：

$$a^2+b^2=c^2$$

通过双向链接继续阅读：[[中文 路径|中文与空格路径示例]]。

`[[示例中的文字不会触发笔记导出]]`
''',
  'demo/中文 路径.md':'''---
title: 中文与空格 · 演示
---
这也是公开合成示例，不是用户选择的笔记。中文标题和带空格的文件名可以正常阅读与链接。

[[公开演示|返回功能演示]] · [回到知识花园](../notes/index.md)
''',
  'demo/learning.png':illustration(),
 }
 for name,data in files.items():
  path=root/name;path.parent.mkdir(exist_ok=True)
  raw=data.encode() if isinstance(data,str) else data;path.write_bytes(raw);manifest['files'][name]=hashlib.sha256(raw).hexdigest()
 landing=root/'notes/index.md';text=landing.read_text().split('\n## 看看花园的样子')[0]+'\n## 看看花园的样子\n\n[浏览公开功能演示](../demo/公开演示.md) · 全部为新写的合成示例，非用户笔记。\n';landing.write_text(text);manifest['files']['notes/index.md']=hashlib.sha256(landing.read_bytes()).hexdigest()
 manifest.update(synthetic_demo_notes=2,synthetic_demo_assets=1);(root/'publication.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');return check(root)
if __name__=='__main__':print(json.dumps(add(sys.argv[1] if len(sys.argv)>1 else 'content'),ensure_ascii=False))
