"""Google resource checks distinguish rendered examples from resource references."""
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_generated import check


class GoogleResources(unittest.TestCase):
    def errors(self, html, files=None):
        scratch = Path(__file__).resolve().parents[2] / 'scratch'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            (root / 'index.html').write_text(html)
            (root / 'SearchData.json').write_text('{}')
            for name, content in (files or {}).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            return check(root, {'public': [], 'private': []})['errors']

    def assert_google(self, html, files=None):
        self.assertIn('template/Google: index.html', self.errors(html, files))

    def test_highlighted_css_example(self):
        self.assertEqual(self.errors('<pre><code><span class="k">@import</span> '
            '<span class="sx">url(\'https://fonts.googleapis.com/css2?family=Inter&amp;display=swap\')</span>'
            '</code></pre>'), [])

    def test_escaped_html_example(self):
        self.assertEqual(self.errors('<pre><code>&lt;link rel="stylesheet" '
            'href="https://fonts.googleapis.com/css"&gt;</code></pre>'), [])

    def test_visible_inline_code(self):
        self.assertEqual(self.errors('<p><code>url(https://fonts.gstatic.com/font.woff2)</code></p>'), [])

    def test_real_link(self):
        self.assert_google('<link rel="stylesheet" href="https://fonts.googleapis.com/css">')

    def test_real_image(self):
        self.assert_google('<img src="//fonts.gstatic.com/image.png">')

    def test_real_script(self):
        self.assert_google('<script src="https://fonts.googleapis.com/script.js"></script>')

    def test_real_dom_inside_code(self):
        self.assert_google('<pre><code><img src="https://fonts.gstatic.com/image.png"></code></pre>')

    def test_style_attribute(self):
        self.assert_google('<div style="background:url(https://fonts.gstatic.com/image.png)"></div>')

    def test_style_element_import(self):
        self.assert_google('<style>@import "https://fonts.googleapis.com/css";</style>')

    def test_style_element_url(self):
        self.assert_google('<style>@font-face{src:url(//fonts.gstatic.com/font.woff2)}</style>')

    def test_linked_local_css(self):
        self.assert_google('<link rel="stylesheet" href="/assets/main.css">',
            {'assets/main.css': '@import url("https://fonts.googleapis.com/css");'})

    def test_nested_local_css_import(self):
        self.assert_google('<link rel="stylesheet" href="/assets/main.css">',
            {'assets/main.css': '@import "nested/font.css";',
             'assets/nested/font.css': '@font-face{src:url(https://fonts.gstatic.com/font.woff2)}'})

    def test_inline_style_local_import(self):
        self.assert_google('<style>@import "/assets/font.css";</style>',
            {'assets/font.css': '@import "https://fonts.googleapis.com/css";'})

    def test_local_css_cycle(self):
        self.assertEqual(self.errors('<link rel="stylesheet" href="/a.css">',
            {'a.css': '@import "b.css";', 'b.css': '@import "a.css";'}), [])

    def test_additional_html_resource_attributes(self):
        for tag, attr in [('img', 'srcset'), ('source', 'srcset'), ('link', 'imagesrcset'),
                          ('video', 'poster'), ('object', 'data'), ('body', 'background'),
                          ('table', 'background'), ('td', 'background'), ('th', 'background'),
                          ('html', 'manifest'), ('applet', 'code'), ('applet', 'codebase'),
                          ('object', 'archive'), ('object', 'classid'), ('head', 'profile'),
                          ('a', 'ping'), ('iframe', 'longdesc'), ('img', 'lowsrc'), ('img', 'dynsrc')]:
            with self.subTest(tag=tag, attr=attr):
                self.assert_google(f'<pre><code><{tag} {attr}="https://fonts.gstatic.com/asset.webp"></{tag}></code></pre>')
                self.assertEqual(self.errors(f'<pre><code>&lt;{tag} {attr}="https://fonts.gstatic.com/asset.webp"&gt;</code></pre>'), [])

    def test_image_set_strings(self):
        for function in ['image-set', '-webkit-image-set']:
            css = f'body{{background:{function}("local.webp" 1x, "https://fonts.gstatic.com/asset.webp" 2x)}}'
            with self.subTest(function=function):
                self.assert_google(f'<style>{css}</style>')
                self.assert_google(f"<div style='{css}'></div>")
                self.assert_google('<link rel="stylesheet" href="/assets/main.css">',
                    {'assets/main.css': '@import "nested.css";', 'assets/nested.css': css})
                self.assertEqual(self.errors(f'<style>/* {css} */</style>'), [])
                self.assertEqual(self.errors(f'<pre><code>{css}</code></pre>'), [])

    def test_css_strings_are_not_requests(self):
        self.assertEqual(self.errors('<style>p::after{content: "image-set(https://fonts.gstatic.com/asset.webp)"}</style>'), [])

    def test_src_href_missing_resource_contract(self):
        self.assertEqual(self.errors('<img src="/missing.png"><a href="/missing.pdf">x</a>'),
            ['missing resource: index.html -> /missing.pdf', 'missing resource: index.html -> /missing.png'])

    def test_css_escape_does_not_read_outside_root(self):
        scratch = Path(__file__).resolve().parents[2] / 'scratch'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            base = Path(directory)
            root = base / 'build'
            root.mkdir()
            outside = base / 'outside.css'
            outside.write_text('@import "https://fonts.googleapis.com/css";')
            (root / 'escape.css').symlink_to(outside)
            (root / 'SearchData.json').write_text('{}')
            original = Path.read_text
            def guarded_read(path, *args, **kwargs):
                self.assertTrue(path.resolve().is_relative_to(root), str(path))
                return original(path, *args, **kwargs)
            for target in ['../outside.css', 'escape.css', r'\2e \2e /outside.css', r'\65 scape.css']:
                (root / 'index.html').write_text(f'<style>@import "{target}";</style>')
                with self.subTest(target=target), patch.object(Path, 'read_text', guarded_read):
                    self.assertEqual(check(root, {'public': [], 'private': []})['errors'], [])

    def test_template_assertion_preserved(self):
        self.assertIn('template/Google: index.html', self.errors('<pre>Your Name</pre>'))

    def test_import_comment_separator(self):
        self.assert_google('<style>@import/**/"https://fonts.googleapis.com/css";</style>')
        self.assert_google('<style>@import/**/url("nested.css");</style>',
            {'nested.css': '@import/**/"https://fonts.googleapis.com/css";'})

    def test_css_escape_semantic_values(self):
        for escaped in [r'\2e ', r'\02e ', r'\002e ', r'\0002e ', r'\00002e', r'\00002e ', '\\2e\t', '\\2e\r\n']:
            with self.subTest(escaped=escaped):
                self.assert_google(f'<style>a{{background:url("https://fonts{escaped}gstatic.com/a.png")}}</style>')
        for css in [
            'url("https://fonts.\\\ngstatic.com/a.png")',
            'url("https://fonts.\\\r\ngstatic.com/a.png")',
            'url("https://fonts.\\\rgstatic.com/a.png")',
            'url("https://fonts.\\\fgstatic.com/a.png")',
            r'url(https://fonts\2e gstatic.com/a.png)',
            r'@import "https://fonts\2e googleapis.com/css"',
            r'image-set("https://fonts\2e gstatic.com/a.png" 1x)',
        ]:
            with self.subTest(css=css):
                self.assert_google(f'<style>a{{background:{css}}}</style>')
        for escaped in [r'\0 ', r'\D800 ', r'\110000 ', r'\2e0 ']:
            with self.subTest(invalid_or_longer=escaped):
                self.assertEqual(self.errors(f'<style>a{{background:url("https://fonts{escaped}gstatic.com/a.png")}}</style>'), [])
        self.assert_google(r'<style>@import "ne\73 ted.css";</style>',
            {'nested.css': '@import "https://fonts.googleapis.com/css";'})

    def test_unterminated_css_comment(self):
        self.assertEqual(self.errors('<style>/* url(https://fonts.gstatic.com/a.png)</style>'), [])
        self.assertEqual(self.errors('<style>/* @import "https://fonts.googleapis.com/css";</style>'), [])
        self.assertEqual(self.errors('<style>@import/*https://fonts.googleapis.com/css</style>'), [])

    def test_html_attribute_element_semantics(self):
        self.assertEqual(self.errors('<div data="fonts.googleapis.com"></div>'), [])
        self.assert_google('<object data="fonts.googleapis.com"></object>')
        for attr in ['srcset', 'poster', 'background', 'manifest', 'code', 'ping']:
            with self.subTest(attr=attr):
                self.assertEqual(self.errors(f'<div {attr}="https://fonts.gstatic.com/a.png"></div>'), [])

    def test_css_escaped_quotes_keep_string_boundary(self):
        for css in [r'p{content:"example\" url(https://fonts.gstatic.com/a.png)"}',
                    r"p{content:'example\' @import \"https://fonts.googleapis.com/css\"'}",
                    r'p{content:"https://fonts\2e gstatic.com/a.png"}',
                    r'/* url("https://fonts\2e gstatic.com/a.png") */']:
            with self.subTest(css=css):
                self.assertEqual(self.errors(f'<style>{css}</style>'), [])

    def test_escaped_css_function_identifiers(self):
        for function in [r'\75 rl', r'u\72l', r'\000075\000072\00006c', r'\55 RL']:
            with self.subTest(function=function):
                self.assert_google(f'<style>a{{background:{function}("https://fonts.gstatic.com/a.png")}}</style>')
        self.assert_google(r'<style>a{background:im\61 ge-set("https://fonts.gstatic.com/a.png" 1x)}</style>')


if __name__ == '__main__':
    unittest.main()
