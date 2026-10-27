#!/usr/bin/env python3
"""Inventory public-note attachment candidates; never fetch or create attachments.

Uses the site's Kramdown dependency to parse Markdown (not a link regex). Explicit
fences are masked first, including GFM backtick fences. HTML attributes are read
outside pre/code only (script/style bodies are raw text). This is a source inventory, not proof that
Liquid/Jekyll renders every candidate. JSON output includes path-level evidence;
--data-output writes only confirmed missing mappings used by the existing include.
Run under bundle exec, or with the site's gems available through GEM_PATH.
"""
import argparse
import fnmatch
import json
import os
import posixpath
import re
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Keep identical to check_generated.check's attachment suffix allowlist.
SUFFIXES = {'.js', '.css', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp',
            '.ico', '.woff', '.woff2', '.pdf'}
RUBY_PARSE = r'''
require 'json'
require 'yaml'
require 'kramdown'
input = JSON.parse(STDIN.read)
config = File.file?(input['config']) ? YAML.load_file(input['config']) : {}
begin
  require 'kramdown-parser-gfm'
  parser = 'GFM'
rescue LoadError
  parser = 'kramdown'
end
options = (config || {}).fetch('kramdown', {}).transform_keys(&:to_sym)
options[:input] ||= parser
puts JSON.generate({
  'exclude' => (config || {}).fetch('exclude', []),
  'include' => (config || {}).fetch('include', []),
  'parser' => options[:input],
  'jekyll_default_parser_available' => parser == 'GFM',
  'html' => input['pages'].map { |text| Kramdown::Document.new(text, options).to_html }
})
'''


def without_fences(text):
    """Remove front matter and fenced examples, retaining line boundaries."""
    text = re.sub(r'\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)', '', text, count=1, flags=re.S)
    result, fence = [], None
    for line in text.splitlines(keepends=True):
        plain = re.sub(r'^(?: {0,3}> ?)*', '', line)
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', plain.rstrip('\r\n'))
        if fence:
            result.append('\n' if line.endswith('\n') else '')
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
        elif match and not (match[1][0] == '`' and '`' in match[2]):
            fence = match[1]
            result.append('\n' if line.endswith('\n') else '')
        else:
            result.append(line)
    return ''.join(result)


class Attributes(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.blocked = []
        self.targets = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag in {'pre', 'code'}:
            self.blocked.append(tag)
        if not self.blocked:
            for name, value in attrs:
                if name in {'href', 'src'} and value:
                    self.targets.append((tag, name, value))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.blocked:
            self.blocked = self.blocked[:self.blocked.index(tag)]


def normalized(path):
    return posixpath.normpath('/' + path.lstrip('/'))


def resource_location(parent, target):
    # Unlike browser URL normalization, check_generated's filesystem lookup can
    # traverse above the build root. Retain leading ../ as evidence, never probe
    # outside the repository or alias an escaped path to a public root file.
    relative = target.lstrip('/') if target.startswith('/') else posixpath.join(parent.lstrip('/'), target)
    path = posixpath.normpath(relative)
    return path if path == '..' or path.startswith('../') else '/' + path


def public_static_files(root, exclude, include):
    """Index exact public source paths, respecting Jekyll special/excluded paths."""
    paths = set()
    for directory, dirs, files in os.walk(root):
        parent = Path(directory).relative_to(root)
        def allowed(path):
            value = path.as_posix()
            if any(fnmatch.fnmatch(value, x.rstrip('/')) or value.startswith(x.rstrip('/') + '/')
                   for x in exclude):
                return False
            return not any(part.startswith(('.', '_', '#')) for part in path.parts) or value in include
        dirs[:] = [name for name in dirs if allowed(parent / name)]
        for name in files:
            path = parent / name
            if allowed(path) and (root / path).is_file():
                paths.add('/' + path.as_posix())
    return paths


def scan(root, manifest=None):
    root = Path(root).resolve()
    manifest = manifest or json.loads((root / 'scripts/publication-manifest.json').read_text())
    entries = manifest['public']
    notes_root = (root / '_notes').resolve()
    if not notes_root.is_relative_to(root):
        raise ValueError('notes root escapes repository')
    pages, paths = [], []
    for item in entries:
        filename = item['file']
        if Path(filename).is_absolute():
            raise ValueError('absolute note path: ' + filename)
        page = '_notes/' + filename.removeprefix('_notes/')
        path = (root / page).resolve()
        if not path.is_relative_to(root) or not path.is_relative_to(notes_root):
            raise ValueError('note path escapes repository or notes root: ' + filename)
        pages.append(page)
        paths.append(path)
    texts = [without_fences(path.read_text()) for path in paths]
    parsed = subprocess.run(['ruby', '-e', RUBY_PARSE], input=json.dumps({
        'config': str(root / '_config.yml'), 'pages': texts}),
        text=True, capture_output=True, check=True)
    parsed = json.loads(parsed.stdout)
    public = public_static_files(root, parsed['exclude'], parsed['include'])
    note_urls = {normalized(unquote(urlsplit(item['url']).path)) for item in entries}
    rows = {}
    for page, entry, rendered in zip(pages, entries, parsed['html']):
        page_url = unquote(urlsplit(entry['url']).path)
        # Jekyll's extensionless collection URL is emitted as URL.html. A trailing
        # slash instead emits URL/index.html. Match check_generated's parent dir.
        generated_page = page_url + ('index.html' if page_url.endswith('/') else '.html')
        for tag, attribute, url in Attributes(rendered).targets:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or url.startswith('//') or not parts.path:
                continue
            target = parts.path  # Preserve URL encoding; queries/fragments stay in url.
            decoded = unquote(target)
            if Path(decoded).suffix.lower() not in SUFFIXES or '{{' in decoded or '{%' in decoded:
                continue
            source_path = resource_location(posixpath.dirname(page), decoded)
            generated_path = resource_location(posixpath.dirname(generated_page), decoded)
            if generated_path in note_urls:
                continue
            # Only the generated page's URL controls browser/checker lookup.
            # A source-relative match is diagnostic evidence, never proof.
            found = [generated_path] if generated_path in public else []
            supported = (tag, attribute) in {('img', 'src'), ('a', 'href')}
            key = (page, url, tag, attribute)
            rows[key] = {'page': page, 'page_url': entry['url'], 'url': url,
                         'target': target, 'tag': tag, 'attribute': attribute,
                         'degradable': supported,
                         'kind': ('image' if tag == 'img' else 'document') if supported else None,
                         'source_path': source_path, 'generated_path': generated_path,
                         'public_files_found': found, 'missing': not found}
    candidates = sorted(rows.values(), key=lambda row: (row['page'], row['url'], row['tag'], row['attribute']))
    missing = [row for row in candidates if row['missing']]
    unsupported = [row for row in missing if not row['degradable']]
    def counts(items):
        return {'candidate_records': len(items),
                'unique_targets': len({r['generated_path'] for r in items}),
                'unique_url_paths': len({r['target'] for r in items}),
                'page_url_pairs': len({(r['page'], r['url']) for r in items}),
                'pages': len({r['page'] for r in items})}
    grouped = defaultdict(set)
    for row in missing:
        if not row['degradable']:
            continue
        grouped[row['page'], row['target'], row['kind']].add(row['url'])
    mapping = [{'page': page, 'target': target, 'kind': kind, 'urls': sorted(urls)}
               for (page, target, kind), urls in sorted(grouped.items())]
    return {'scope': 'manifest public notes; parsed Markdown and raw HTML attributes; not a rendered-site assertion',
            'manifest_public_pages': len(entries),
            'parser': parsed['parser'],
            'jekyll_default_parser_available': parsed['jekyll_default_parser_available'],
            'rendered_site_verified': False,
            'counts': {'candidates': counts(candidates), 'confirmed_missing': counts(missing),
                       'unsupported_unresolved': counts(unsupported)},
            'candidates': candidates, 'mapping': mapping,
            'unsupported_unresolved': unsupported}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, required=True, help='Full evidence JSON (keep outside product repo)')
    parser.add_argument('--data-output', type=Path, help='Confirmed mapping, JSON-compatible YAML')
    args = parser.parse_args()
    result = scan(args.root)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if args.data_output:
        args.data_output.write_text(json.dumps(result['mapping'], ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['counts'], ensure_ascii=False))


if __name__ == '__main__':
    main()
