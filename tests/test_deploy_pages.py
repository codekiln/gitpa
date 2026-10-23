import contextlib
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from deploy_pages import Pages, prepare, verify


class FakePages:
    revision = 'source-new'
    run = 'run-new'

    def __init__(self, builds=(), markers=()):
        self.builds = iter(builds)
        self.markers = iter(markers)
        self.requests = []
        self.head = self.revision

    def identity(self):
        return {'revision': self.revision, 'run': self.run}

    def api(self, path, method='GET'):
        self.requests.append((path, method))
        if path == 'git/ref/heads/main':
            return {'object': {'sha': self.head}}
        if path == 'git/ref/heads/gh-pages':
            return {'object': {'sha': 'output-new'}}
        if path == 'pages':
            return {'html_url': 'https://example.test/gitpa/'}
        if method == 'POST':
            return {'status': 'queued'}
        result = next(self.builds)
        if isinstance(result, Exception):
            raise result
        return result

    def marker(self, site):
        return next(self.markers)


def build(status, commit='output-new'):
    return {'status': status, 'commit': commit}


class DeploymentTests(unittest.TestCase):
    def run_verify(self, pages, timeout=120):
        now = [0]
        def sleep(seconds):
            now[0] += seconds
        with contextlib.redirect_stdout(io.StringIO()):
            return verify(pages, timeout, clock=lambda: now[0], sleep=sleep)

    def test_waits_for_matching_build_and_public_run(self):
        p = FakePages([build('errored', 'output-old'), build('building'), build('built'), build('built')],
                      [{'revision': 'source-new', 'run': 'old'}] +
                      [{'revision': 'source-new', 'run': 'run-new'}])
        self.run_verify(p)
        self.assertEqual(p.requests.count(('pages/builds', 'POST')), 1)
        self.assertEqual(len(list(p.markers)), 0)

    def test_replacement_build_recovers_from_matching_error(self):
        p = FakePages([build('errored'), build('queued'), build('building'), build('built')],
                      [{'revision': 'source-new', 'run': 'run-new'}])
        self.run_verify(p)
        self.assertEqual(p.requests.count(('pages/builds', 'POST')), 1)
        self.assertEqual(len(list(p.markers)), 0)

    def test_persistent_matching_build_error_fails_after_replacement_grace(self):
        p = FakePages([build('errored')] * 12)
        with self.assertRaisesRegex(RuntimeError, 'Pages build failed'):
            self.run_verify(p)
        self.assertGreater(p.requests.count(('pages/builds/latest', 'GET')), 1)
        self.assertEqual(p.requests.count(('pages/builds', 'POST')), 1)

    def test_outdated_public_marker_times_out(self):
        p = FakePages([build('built')] * 3, [{'revision': 'old'}] * 3)
        with self.assertRaisesRegex(RuntimeError, 'did not serve'):
            self.run_verify(p, timeout=30)

    def test_transient_http_failure_recovers_but_permission_error_fails(self):
        retry = HTTPError('https://api.github.com', 503, 'unavailable', {}, None)
        p = FakePages([retry, build('built')], [{'revision': 'source-new', 'run': 'run-new'}])
        self.run_verify(p)
        denied = HTTPError('https://api.github.com', 403, 'denied', {}, None)
        with self.assertRaises(HTTPError):
            self.run_verify(FakePages([denied]))

    def test_stale_source_leaves_artifact_untouched(self):
        p = FakePages()
        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / 'publication.json'
            p.head = 'newer-main'
            self.assertFalse(prepare(p, folder))
            self.assertFalse(marker.exists())
            p.head = p.revision
            self.assertTrue(prepare(p, folder))
            self.assertIn('run-new', marker.read_text())

    def test_public_request_does_not_receive_repository_token(self):
        with patch.dict('os.environ', {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_SHA': 'source',
                                      'GITHUB_RUN_ID': 'run', 'GH_TOKEN': 'private-token'}):
            p = Pages()
        response = contextlib.nullcontext(io.StringIO('{}'))
        with patch('deploy_pages.urlopen', return_value=response) as open_url:
            p.marker('https://example.test/gitpa/')
        request = open_url.call_args.args[0]
        self.assertIsNone(request.get_header('Authorization'))
        self.assertTrue(request.full_url.endswith('/publication.json?run=run'))


if __name__ == '__main__':
    unittest.main()
