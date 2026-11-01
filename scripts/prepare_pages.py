#!/usr/bin/env python3
"""Prepare a reviewed branch/root tree outside the checkout. No Git writes/network."""
import hashlib, json, pathlib, shutil, sys
from check_stage import check

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ('.gitignore', 'LICENSE.txt', 'README.md', 'UPSTREAM.json', 'globals.d.ts',
         'index.d.ts', 'package.json', 'package-lock.json', 'requirements.txt',
         'quartz.config.ts', 'quartz.layout.ts', 'tsconfig.json')
DIRECTORIES = ('.github', 'content', 'quartz', 'scripts', 'tests')
EXCLUDED = {'.git', 'node_modules', '.quartz-cache', '__pycache__', '.DS_Store'}

def prepare(destination):
    destination = pathlib.Path(destination).absolute()
    if destination.exists() or destination.resolve() != destination or destination == ROOT or ROOT in destination.parents:
        raise ValueError('candidate must be a new directory outside checkout')
    stage = check(ROOT / 'content')
    if stage['selected_notes'] or stage['selected_assets']:
        raise ValueError('this deployment authorizes zero real notes/assets')
    sources = []
    for name in FILES + DIRECTORIES:
        path = ROOT / name
        if path.is_symlink() or not path.exists():
            raise ValueError('missing/unsafe allowed source')
        sources.extend([path] if path.is_file() else path.rglob('*'))
    inventory = {}
    for path in sources:
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts) or path.suffix == '.pyc':
            continue
        if path.is_symlink():
            raise ValueError('source symlink')
        if path.is_file(): inventory[relative.as_posix()] = path
    output = ROOT / 'public'
    for path in output.rglob('*'):
        if path.is_symlink(): raise ValueError('output symlink')
        if path.is_file():
            name = path.relative_to(output).as_posix()
            if any(part.startswith('.') for part in pathlib.PurePosixPath(name).parts):
                raise ValueError('unexpected hidden output')
            if name in inventory: raise ValueError('source/output collision')
            inventory[name] = path
    for name in ('index.html', 'notes/index.html', '404.html', 'index.css', 'prescript.js', 'postscript.js', 'static/contentIndex.json'):
        if name not in inventory: raise ValueError('missing required output')
    destination.mkdir(parents=True)
    for name, path in inventory.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    (destination / '.nojekyll').write_bytes(b'')
    files = {p.relative_to(destination).as_posix(): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(destination.rglob('*')) if p.is_file()}
    return {'mode': 'branch-main-root-nojekyll', 'files': files, 'file_count': len(files),
            'bytes': sum(x['bytes'] for x in files.values()), 'stage': stage,
            'source_files': FILES, 'source_directories': DIRECTORIES,
            'exclusions': sorted(EXCLUDED | {'*.pyc', 'public/ (copied only as static root output)', 'all non-allowlisted paths'})}

if __name__ == '__main__':
    print(json.dumps(prepare(sys.argv[1]), ensure_ascii=False, indent=2))
