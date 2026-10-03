#!/usr/bin/env python3
import functools
import http.server
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest


SCRIPT = Path(__file__).with_name('package_charts.py').resolve()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'published'
        self.repo.mkdir()
        self.work = self.root / 'work'
        self.chart = self.work / 'charts' / 'example'
        (self.chart / 'templates').mkdir(parents=True)
        (self.chart / 'templates' / 'configmap.yaml').write_text(
            'apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: example\n')
        for version in ['0.1.0', '0.1.1-rc.1']:
            self.write_chart(version)
            subprocess.run(['helm', 'package', str(self.chart), '-d', str(self.repo)],
                           check=True, capture_output=True)
        subprocess.run(['helm', 'repo', 'index', str(self.repo)], check=True)
        self.originals = {p.name: p.read_bytes() for p in self.repo.glob('*.tgz')}
        handler = functools.partial(QuietHandler, directory=str(self.repo))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def write_chart(self, version, description='Example chart'):
        (self.chart / 'Chart.yaml').write_text(
            f'apiVersion: v2\nname: example\nversion: {version}\ndescription: {description}\n')

    def publish(self):
        return subprocess.run([sys.executable, str(SCRIPT), '--repository-url', self.url],
                              cwd=self.work, capture_output=True, text=True)

    def test_new_release_preserves_stable_and_prerelease_archives(self):
        self.write_chart('0.2.0')
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name, content in self.originals.items():
            self.assertEqual((self.work / 'dist' / name).read_bytes(), content)
        index = (self.work / 'dist' / 'index.yaml').read_text()
        for version in ['0.1.0', '0.1.1-rc.1', '0.2.0']:
            self.assertIn(f'version: {version}', index)

    def test_unchanged_chart_keeps_original_archive(self):
        self.write_chart('0.1.0')
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name, content in self.originals.items():
            self.assertEqual((self.work / 'dist' / name).read_bytes(), content)

    def test_changed_published_version_is_rejected(self):
        self.write_chart('0.1.0', 'Changed chart')
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('bump the chart version', result.stderr)
        self.assertFalse((self.work / 'dist' / 'index.yaml').exists())

    def test_missing_index_stops_publication(self):
        (self.repo / 'index.yaml').unlink()
        self.write_chart('0.2.0')
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.work / 'dist' / 'index.yaml').exists())

    def test_stale_output_is_rejected(self):
        (self.work / 'dist').mkdir()
        (self.work / 'dist' / 'old.tgz').write_bytes(b'stale')
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('dist must be empty', result.stderr)


if __name__ == '__main__':
    unittest.main()
