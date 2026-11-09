"""Editable CV regression using an isolated repository, never changing the real CV."""
import hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]

class CVSource(unittest.TestCase):
    def setUp(self):
        base = pathlib.Path(os.environ['TEST_SCRATCH']).resolve()
        if base == ROOT or ROOT in base.parents:
            raise RuntimeError('fixtures must be outside checkout')
        self.case = pathlib.Path(tempfile.mkdtemp(prefix='cv-source-', dir=base))
        self.repo = self.case / 'repo'
        shutil.copytree(ROOT / 'scripts', self.repo / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        self.cv = self.repo / 'cv.md'
        self.cv.write_bytes((ROOT / 'cv.md').read_bytes())
        self.vault = self.case / 'empty-fixture'; self.vault.mkdir()
        self.stage = self.repo / 'content'

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(self.repo / 'scripts' / name), *map(str, args)],
                              cwd=self.case, capture_output=True, text=True)

    def test_edit_drives_export_and_persists(self):
        edited = self.cv.read_text() + '\nCV_EDIT_FIXTURE_2026\n'
        self.cv.write_text(edited)
        for _ in range(2):
            result = self.run_script('selective_export.py', self.vault, '--output', self.stage)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((self.stage / 'index.md').read_text(), edited)
            self.assertEqual(self.cv.read_text(), edited)

    def test_missing_unsafe_sources_revoke_stage(self):
        original = self.cv.read_bytes()
        for kind in ('missing', 'symlink', 'directory', 'invalid-utf8'):
            with self.subTest(kind=kind):
                self.cv.write_bytes(original)
                self.assertEqual(self.run_script('selective_export.py', self.vault, '--output', self.stage).returncode, 0)
                self.cv.unlink()
                if kind == 'symlink':
                    target = self.case / 'target.md'; target.write_bytes(original); self.cv.symlink_to(target)
                elif kind == 'directory': self.cv.mkdir()
                elif kind == 'invalid-utf8': self.cv.write_bytes(b'\xff')
                result = self.run_script('selective_export.py', self.vault, '--output', self.stage)
                self.assertEqual(result.returncode, 2)
                self.assertIn('E_CV:', result.stdout)
                self.assertFalse(self.stage.exists())
                if self.cv.is_dir(): self.cv.rmdir()
                elif self.cv.exists() or self.cv.is_symlink(): self.cv.unlink()

    def test_source_hash_mode_and_generated_root_integrity(self):
        for tamper in ('source', 'mode', 'hash', 'root-with-updated-hash'):
            with self.subTest(tamper=tamper):
                self.assertEqual(self.run_script('selective_export.py', self.vault, '--output', self.stage).returncode, 0)
                self.assertEqual(self.run_script('check_stage.py', self.stage).returncode, 0)
                manifest = self.stage / 'publication.json'
                data = json.loads(manifest.read_text())
                self.assertEqual(data['cv_source']['sha256'], hashlib.sha256(self.cv.read_bytes()).hexdigest())
                if tamper == 'source': self.cv.write_text(self.cv.read_text() + '\nChanged source\n')
                elif tamper == 'mode': data['cv_source']['mode'] = 'other'
                elif tamper == 'hash': data['cv_source']['sha256'] = '0' * 64
                else:
                    (self.stage / 'index.md').write_text('Changed generated root')
                    data['files']['index.md'] = hashlib.sha256((self.stage / 'index.md').read_bytes()).hexdigest()
                manifest.write_text(json.dumps(data))
                self.assertEqual(self.run_script('check_stage.py', self.stage).returncode, 2)

    def test_real_render_and_candidate_inclusion(self):
        # Supplemental integration: use the installed toolchain, with isolated source/output.
        import importlib.util
        spec = importlib.util.spec_from_file_location('fixture_prepare', ROOT / 'scripts/prepare_pages.py')
        sys.path.insert(0, str(ROOT / 'scripts'))
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        for name in module.FILES:
            if name != 'cv.md': shutil.copy2(ROOT / name, self.repo / name)
        for name in module.DIRECTORIES:
            if name not in ('scripts', 'content'):
                shutil.copytree(ROOT / name, self.repo / name, ignore=shutil.ignore_patterns('__pycache__'))
        (self.repo / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
        self.cv.write_text(self.cv.read_text() + '\nCV_RENDER_FIXTURE_2026\n')
        self.assertEqual(self.run_script('selective_export.py', self.vault, '--output', self.stage).returncode, 0)
        result = self.run_script('site-build.py', self.stage, self.repo / 'public')
        (self.case / 'build.log').write_text(result.stdout + result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CV_RENDER_FIXTURE_2026', (self.repo / 'public/index.html').read_text())
        for checker in ('check_resources.py', 'check_http_routes.py'):
            result = self.run_script(checker, self.repo / 'public')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        candidate = self.case / 'candidate'
        result = self.run_script('prepare_pages.py', candidate)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((candidate / 'cv.md').read_bytes(), self.cv.read_bytes())
        self.assertEqual((candidate / 'content/index.md').read_bytes(), self.cv.read_bytes())
        receipt = json.loads(result.stdout)
        self.assertIn('cv.md', receipt['source_files'])
        self.assertEqual(receipt['stage']['selected_notes'], 0)
        self.assertEqual(receipt['stage']['selected_assets'], 0)
        # Existing deployment guard must continue rejecting selected notes.
        (self.vault / 'selected.md').write_text('---\npublish: true\n---\nSynthetic selection\n')
        self.assertEqual(self.run_script('selective_export.py', self.vault, '--output', self.stage).returncode, 0)
        rejected = self.case / 'rejected-candidate'
        self.assertNotEqual(self.run_script('prepare_pages.py', rejected).returncode, 0)
        self.assertFalse(rejected.exists())

if __name__ == '__main__': unittest.main(verbosity=2)
