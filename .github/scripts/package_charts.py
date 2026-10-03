#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile


def run(*args):
    return subprocess.check_output(args, text=True)


def contents(path):
    with tarfile.open(path) as archive:
        return {member.name: (member.mode, archive.extractfile(member).read())
                for member in archive.getmembers() if member.isfile()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository-url', default='https://charts.projecthelena.com')
    args = parser.parse_args()
    dist = Path('dist')
    if dist.exists() and any(dist.iterdir()):
        raise RuntimeError('dist must be empty before packaging')
    dist.mkdir(exist_ok=True)
    # Cloudflare Pages replaces the deployment, so keep every published package.
    with tempfile.TemporaryDirectory() as temp:
        config = str(Path(temp) / 'repositories.yaml')
        cache = str(Path(temp) / 'cache')
        flags = ('--repository-config', config, '--repository-cache', cache)
        run('helm', 'repo', 'add', 'published', args.repository_url, *flags)
        packages = json.loads(run('helm', 'search', 'repo', 'published/', '--versions', '--devel', '-o', 'json', *flags))
        if not packages:
            raise RuntimeError('Published repository is empty; refusing to discard chart history')
        for package in packages:
            run('helm', 'pull', package['name'], '--version', package['version'], '--destination', str(dist), *flags)
        for chart in sorted(Path('charts').iterdir()):
            if not (chart / 'Chart.yaml').is_file():
                continue
            run('helm', 'package', str(chart), '--destination', temp)
        for package in Path(temp).glob('*.tgz'):
            target = dist / package.name
            if target.exists():
                if contents(target) != contents(package):
                    raise RuntimeError(f'{package.name} already exists with different contents; bump the chart version')
            else:
                package.replace(target)
    run('helm', 'repo', 'index', str(dist))


if __name__ == '__main__':
    main()
