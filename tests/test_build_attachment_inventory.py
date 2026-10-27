import json
import os
import sys
import tempfile
import unittest
import subprocess
import ast
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_attachment_inventory import scan, SUFFIXES


class AttachmentInventory(unittest.TestCase):
    def test_manifest_paths_are_checked_before_reading(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
            base = Path(directory)
            root = base / 'repo'
            (root / '_notes').mkdir(parents=True)
            outside = base / 'outside.md'
            outside.write_text('fixture only')
            (root / 'elsewhere.md').write_text('fixture only')
            (root / '_notes/link.md').symlink_to(outside)
            (root / '_notes/internal-link.md').symlink_to(root / 'elsewhere.md')
            read_text = Path.read_text
            for filename in (str(outside), '../../outside.md', '../elsewhere.md',
                             'link.md', 'internal-link.md'):
                with self.subTest(filename=filename):
                    reads = []
                    def tracked_read(path, *args, **kwargs):
                        reads.append(path.resolve())
                        return read_text(path, *args, **kwargs)
                    with patch.object(Path, 'read_text', tracked_read):
                        with self.assertRaises(ValueError):
                            scan(root, {'public': [{'file': filename, 'url': '/notes/a'}]})
                    self.assertEqual(reads, [], 'reject unsafe notes before reading any target')
            (root / '_notes/中文 笔记.md').write_text('![图](missing.png)')
            for filename in ('中文 笔记.md', '_notes/中文 笔记.md'):
                result = scan(root, {'public': [{'file': filename, 'url': '/notes/a'}]})
                self.assertEqual(result['mapping'][0]['page'], '_notes/中文 笔记.md')

    def test_notes_root_symlink_must_remain_inside_repo(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
            base = Path(directory)
            (base / 'repo').mkdir()
            (base / 'outside').mkdir()
            (base / 'outside/a.md').write_text('fixture only')
            (base / 'repo/_notes').symlink_to(base / 'outside', target_is_directory=True)
            with patch.object(Path, 'read_text', side_effect=AssertionError('unsafe read')):
                with self.assertRaises(ValueError):
                    scan(base / 'repo', {'public': [{'file': 'a.md', 'url': '/notes/a'}]})

    def test_tag_support_and_real_include_checker_behavior(self):
        from check_generated import check
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
            root = Path(directory)
            (root / '_notes').mkdir()
            (root / 'assets').mkdir()
            (root / 'assets/ok.svg').write_text('<svg/>')
            (root / 'assets/images').mkdir()
            (root / 'assets/images/attachment-unavailable.svg').write_text('<svg/>')
            html = '''<img src="same.pdf?x=1&amp;y=2#page=3" alt="original">
<a href="same.pdf?x=1&amp;y=2#page=3">PDF</a>
<script src="same.pdf?x=1&amp;y=2#page=3"></script>
<link href="missing.css?x=1&amp;y=2#frag" rel="stylesheet">
<source src="missing.png">
<img src="/assets/ok.svg"><a href="/assets/ok.svg">OK</a>
<pre><code><img src="code.png"></code></pre>'''
            (root / '_notes/a.md').write_text(html)
            result = scan(root, {'public': [{'file': 'a.md', 'url': '/notes/a'}]})
            self.assertEqual(len(result['candidates']), 7)
            self.assertEqual(result['counts']['confirmed_missing']['candidate_records'], 5)
            unsupported = result['unsupported_unresolved']
            self.assertEqual({(r['tag'], r['attribute']) for r in unsupported},
                             {('script', 'src'), ('link', 'href'), ('source', 'src')})
            self.assertTrue(all(r['kind'] is None and not r['degradable'] for r in unsupported))
            self.assertEqual(result['counts']['unsupported_unresolved']['candidate_records'], 3)
            self.assertEqual({(r['target'], r['kind']) for r in result['mapping']},
                             {('same.pdf', 'image'), ('same.pdf', 'document')})
            self.assertEqual({r['urls'][0] for r in result['mapping']}, {'same.pdf?x=1&y=2#page=3'})
            ruby = """require 'json'; require 'liquid'; require 'cgi'
module Filters; def escape(x); CGI.escapeHTML(x.to_s); end; end
Liquid::Template.register_filter(Filters)
i=JSON.parse(STDIN.read)
puts Liquid::Template.parse(File.read(i['include'])).render!({'content'=>i['html'], 'page'=>{'path'=>'_notes/a.md'}, 'site'=>{'baseurl'=>'', 'data'=>{'unavailable_attachments'=>i['mapping']}}})
"""
            rendered = subprocess.run(['ruby', '-e', ruby], input=json.dumps({
                'include': str(ROOT / '_includes/UnavailableAttachments.html'),
                'html': html, 'mapping': result['mapping']}), text=True, capture_output=True, check=True).stdout
            self.assertEqual(rendered.count('data-missing-resource='), 2)
            self.assertIn('src="/assets/images/attachment-unavailable.svg" data-missing-resource="same.pdf?x=1&amp;y=2#page=3"', rendered)
            self.assertIn('aria-disabled="true" data-missing-resource="same.pdf?x=1&amp;y=2#page=3"', rendered)
            self.assertIn('alt="original"', rendered)
            for original in ('<script src="same.pdf?x=1&amp;y=2#page=3"></script>',
                             '<link href="missing.css?x=1&amp;y=2#frag" rel="stylesheet">',
                             '<source src="missing.png">', '<img src="/assets/ok.svg">',
                             '<pre><code><img src="code.png"></code></pre>'):
                self.assertIn(original, rendered)
            (root / 'index.html').write_text(rendered)
            (root / 'SearchData.json').write_text('{}')
            errors = check(root, {'public': [], 'private': []})['errors']
            for row in unsupported:
                self.assertIn('missing resource: index.html -> ' + row['url'], errors)
            self.assertEqual(set(errors), {'missing resource: index.html -> ' + r['url']
                                          for r in unsupported} |
                             {'missing resource: index.html -> code.png'})

    def test_suffixes_match_generated_checker(self):
        tree = ast.parse((ROOT / 'scripts/check_generated.py').read_text())
        suffix_sets = [ast.literal_eval(node) for node in ast.walk(tree)
                       if isinstance(node, ast.Set) and any(isinstance(x, ast.Constant) and x.value == '.pdf' for x in node.elts)]
        self.assertEqual(suffix_sets, [SUFFIXES])

    def test_markdown_html_code_and_exact_path_resolution(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
            root = Path(directory)
            (root / '_notes/topic').mkdir(parents=True)
            (root / 'assets').mkdir()
            (root / 'notes/mapped/assets').mkdir(parents=True)
            (root / '_notes/private').mkdir()
            (root / 'tests').mkdir()
            (root / '_config.yml').write_text('exclude: [tests/]\n')
            # Real fixture files at exact public source/generated locations.
            (root / 'assets/ok.svg').write_text('<svg/>')
            (root / 'notes/mapped/assets/routed.png').write_bytes(b'fixture')
            (root / '_notes/private/hidden.png').write_bytes(b'fixture')
            (root / 'tests/excluded.png').write_bytes(b'fixture')
            (root / '_notes/topic/a.md').write_text('''---
summary: "[metadata](metadata.pdf)"
---
[PDF](files/02.Vector.pdf#page=2&selection=1,0,3,4)
![PDF image](files/02.Vector.pdf#page=2&selection=1,0,3,4)
[other](files/03.List.pdf?download=1&amp;x=2#page=3)
[space](<files/a%20(b).pdf#page=4>)
[reference][ref]

[ref]: files/reference.pdf#page=8 "title"
<img src="files/raw.png?a=1&amp;b=2#frag">
<script src="files/app.js">const example = '<img src="script-example.png">';</script>
<link rel="stylesheet" href="files/theme.css">
![traversal](../../../../assets/ok.svg)
<a href='files/raw.pdf?x=1&amp;y=2#page=7'>HTML</a>
![real](../../assets/ok.svg)
![routed](assets/routed.png)
![basename collision](elsewhere/ok.svg)
![hidden](/_notes/private/hidden.png)
![excluded](/tests/excluded.png)
`[code](inline.pdf)` ``![code](inline2.png)``
```markdown
[x](fence.pdf)
<img src="fence.png">
```
~~~html
<img src="tilde.png">
~~~
> ```
> [quote code](quote.pdf)
> ```

    [indented](indented.pdf)

<pre><a href="pre.pdf">code</a></pre>
<code><img src="code.png"></code>
<!-- <img src="comment.png"> -->
[external](https://example.org/a.pdf)
[external](//example.org/b.pdf)
[data](data:image/png;base64,AA)
[mail](mailto:a@example.org)
[anchor](#x.pdf)
[note](other.md) [[note.pdf]]
[internal route](/notes/internal.pdf)
[source](a.c)
''')
            (root / '_notes/internal.md').write_text('note')
            manifest = {'public': [
                {'file': 'topic/a.md', 'url': '/notes/mapped/a'},
                {'file': 'internal.md', 'url': '/notes/internal.pdf'}], 'private': []}
            result = scan(root, manifest)
            urls = {r['url'] for r in result['candidates']}
            self.assertEqual(urls, {
                'files/02.Vector.pdf#page=2&selection=1,0,3,4',
                'files/03.List.pdf?download=1&x=2#page=3',
                'files/a%20(b).pdf#page=4', 'files/reference.pdf#page=8',
                'files/raw.png?a=1&b=2#frag', 'files/raw.pdf?x=1&y=2#page=7',
                '../../assets/ok.svg', 'assets/routed.png', 'elsewhere/ok.svg',
                '/_notes/private/hidden.png', '/tests/excluded.png',
                'files/app.js', 'files/theme.css', '../../../../assets/ok.svg'})
            found = {r['url'] for r in result['candidates'] if not r['missing']}
            self.assertEqual(found, {'../../assets/ok.svg', 'assets/routed.png'})
            missing = {r['url'] for r in result['candidates'] if r['missing']}
            self.assertIn('elsewhere/ok.svg', missing)
            self.assertIn('/_notes/private/hidden.png', missing)
            self.assertIn('../../../../assets/ok.svg', missing)
            vector = [r for r in result['mapping'] if r['target'].endswith('02.Vector.pdf')]
            self.assertEqual({r['kind'] for r in vector}, {'image', 'document'})
            raw = next(r for r in result['candidates'] if r['target'] == 'files/raw.pdf')
            self.assertEqual(raw['generated_path'], '/notes/mapped/files/raw.pdf')
            self.assertEqual(raw['source_path'], '/_notes/topic/files/raw.pdf')

    def test_source_location_cannot_prove_generated_resource_exists(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as directory:
            root = Path(directory)
            (root / '_notes/topic').mkdir(parents=True)
            (root / 'assets').mkdir()
            (root / 'assets/ok.svg').write_text('<svg/>')
            (root / '_notes/topic/a.md').write_text('![image](../../assets/ok.svg?x=1&amp;y=2#frag)')
            manifest = {'public': [{'file': 'topic/a.md', 'url': '/notes/deep/mapped/a'}], 'private': []}
            result = scan(root, manifest)
            row = result['candidates'][0]
            self.assertEqual(row['generated_path'], '/notes/assets/ok.svg')
            self.assertTrue(row['missing'], 'source-relative existence is not generated URL existence')
            self.assertEqual(row['url'], '../../assets/ok.svg?x=1&y=2#frag')

    def test_existing_repository_resource_is_not_degraded(self):
        result = scan(ROOT)
        self.assertEqual(result['unsupported_unresolved'], [])
        self.assertEqual(result['mapping'], json.loads((ROOT / '_data/unavailable_attachments.yml').read_text()))
        self.assertTrue(all(r['tag'] == ('img' if r['kind'] == 'image' else 'a')
                            for r in result['candidates'] if r['missing']))
        public_favicon = ROOT / 'assets/img/favicon.svg'
        self.assertTrue(public_favicon.is_file())
        # Also exercise an actual public repo resource through a note's URL.
        from build_attachment_inventory import public_static_files
        self.assertIn('/assets/img/favicon.svg', public_static_files(ROOT, ['scripts/', 'tests/'], []))
        self.assertFalse(any(r['target'] == '/assets/img/favicon.svg' for r in result['mapping']))


if __name__ == '__main__':
    unittest.main()
