#!/usr/bin/env python3
"""Request the branch-based Pages build and verify its public revision."""
import argparse
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class Pages:
    def __init__(self):
        self.repository = os.environ['GITHUB_REPOSITORY']
        self.revision = os.environ['GITHUB_SHA']
        self.run = os.environ['GITHUB_RUN_ID']
        self.token = os.environ['GH_TOKEN']

    def api(self, path, method='GET'):
        request = Request(f'https://api.github.com/repos/{self.repository}/{path}',
                          method=method, headers={
                              'Authorization': f'Bearer {self.token}',
                              'Accept': 'application/vnd.github+json',
                              'X-GitHub-Api-Version': '2022-11-28'})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    def marker(self, site):
        # Public requests never carry the repository token.
        request = Request(f'{site.rstrip("/")}/publication.json?run={self.run}',
                          headers={'Cache-Control': 'no-cache'})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    def identity(self):
        return {'revision': self.revision, 'run': self.run}


def prepare(pages, output):
    current = pages.api('git/ref/heads/main')['object']['sha'] == pages.revision
    if current:
        (Path(output) / 'publication.json').write_text(json.dumps(pages.identity()) + '\n')
    return current


def verify(pages, timeout=900, clock=time.monotonic, sleep=time.sleep):
    expected = pages.api('git/ref/heads/gh-pages')['object']['sha']
    site = pages.api('pages')['html_url']
    pages.api('pages/builds', 'POST')
    deadline = clock() + timeout
    last = None
    failed_since = None
    while clock() < deadline:
        try:
            build = pages.api('pages/builds/latest')
            status = build.get('status')
            if build.get('commit') == expected:
                if status in ('errored', 'failed', 'error'):
                    # The latest endpoint can still show a cancelled build while its
                    # replacement is queued or building in the recent-build list.
                    recent = [item for item in pages.api('pages/builds?per_page=10')
                              if item.get('commit') == expected]
                    replacement = next((item for item in recent
                                        if item.get('status') == 'built'), None)
                    if replacement is None:
                        replacement = next((item for item in recent
                                            if item.get('status') in ('queued', 'building')), None)
                    if replacement is not None:
                        build = replacement
                        status = build['status']
                if status in ('errored', 'failed', 'error'):
                    # A cancelled build can be replaced by another request for this commit.
                    if failed_since is None:
                        failed_since = clock()
                    if clock() - failed_since >= 60:
                        raise RuntimeError(f'Pages build failed for {expected}: {build.get("error")}')
                else:
                    failed_since = None
                if status == 'built' and pages.marker(site) == pages.identity():
                    print(f'Pages serves source revision {pages.revision}: {site}')
                    return
            else:
                failed_since = None
            state = (build.get('commit'), status)
            if state != last:
                print(f'Waiting for Pages revision {expected}; latest build: {state}', flush=True)
                last = state
        except HTTPError as error:
            if error.code not in (404, 429) and error.code < 500:
                raise
        except (URLError, TimeoutError, json.JSONDecodeError):
            pass
        sleep(10)
    raise RuntimeError(f'Pages did not serve source revision {pages.revision} within {timeout}s')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify'])
    parser.add_argument('--output', default='www')
    args = parser.parse_args()
    if os.environ.get('GITHUB_REF') != 'refs/heads/main' or os.environ.get('GITHUB_EVENT_NAME') not in ('push', 'workflow_dispatch'):
        parser.error('production deployment requires a push or manual run on main')
    pages = Pages()
    if args.command == 'prepare':
        current = prepare(pages, args.output)
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            stream.write(f'current={str(current).lower()}\n')
        if not current:
            print('A newer main revision exists; skipping this deployment.')
    else:
        verify(pages)


if __name__ == '__main__':
    main()
