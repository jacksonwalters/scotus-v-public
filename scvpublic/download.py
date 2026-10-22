"""Download explicit, checksum-pinned raw inputs; never guess a latest release."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request
from urllib.parse import urlparse


def fetch(entry, root):
    url, expected = entry['url'], entry['sha256']
    if urlparse(url).scheme != 'https':
        raise ValueError('Source URLs must use HTTPS')
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise ValueError('Supply a lowercase SHA-256 digest for each source')
    target = (root / entry['path']).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Download path escapes destination')
    from .build import digest
    if target.exists():
        if digest(target) == expected:
            return
        raise ValueError(f'Existing file checksum differs: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
            staging = Path(output.name)
            h = hashlib.sha256()
            with urllib.request.urlopen(url, timeout=120) as response:
                if urlparse(response.url).scheme != 'https':
                    raise ValueError('Refusing non-HTTPS redirect')
                for block in iter(lambda: response.read(1024*1024), b''):
                    output.write(block)
                    h.update(block)
            if h.hexdigest() != expected:
                raise ValueError(f'Checksum mismatch: {url}')
        staging.replace(target)
    finally:
        if staging:
            staging.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--destination', type=Path, default=Path('data/raw'))
    args = parser.parse_args()
    for entry in json.loads(args.manifest.read_text())['files']:
        fetch(entry, args.destination)
        print(entry['path'])


if __name__ == '__main__':
    main()
