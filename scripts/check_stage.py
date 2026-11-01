#!/usr/bin/env python3
"""Validate only the export's approved file inventory, without private-vault access."""
import hashlib,json,pathlib,sys

def check(root):
 root=pathlib.Path(root).absolute()
 # Reject symlink traversal before normalizing benign lexical ../ segments.
 if any(p.is_symlink() for p in (root,*root.parents)):raise ValueError('unsafe staging root')
 root=root.resolve(strict=True)
 if any(p.is_symlink() for p in root.rglob('*')):raise ValueError('unsafe staging root')
 manifest=json.loads((root/'publication.json').read_text())
 if manifest.get('schema')!='shulva-selective-v1' or manifest.get('default_private') is not True:raise ValueError('unrecognized publication manifest')
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
 if actual!=set(manifest['files'])|{'publication.json'}:raise ValueError('unexpected staged files')
 for name,digest in manifest['files'].items():
  p=root/name
  if p.is_symlink() or p.resolve()!=p.absolute() or '..' in pathlib.PurePosixPath(name).parts or name.startswith('/') or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('staging integrity failure')
 return {'checked_files':len(actual),'selected_notes':manifest['selected_notes'],'selected_assets':manifest['selected_assets']}
if __name__=='__main__':
 try:print(json.dumps(check(sys.argv[1] if len(sys.argv)>1 else 'content')))
 except Exception:print('E_STAGE: staging inventory/integrity failure');raise SystemExit(2)
