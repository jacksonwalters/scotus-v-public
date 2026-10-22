"""Package an explicit allowlist; never ship raw data or local credentials."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
import shutil
from contextlib import closing
from scvpublic.store import connect, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact', type=Path)
    parser.add_argument('--output', type=Path, default=Path('artifacts/scvpublic-release.tar.gz'))
    args = parser.parse_args()
    with closing(connect(args.artifact)) as db:
        assert metadata(db)['schema_version'] == 1
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    paths = [Path('requirements.txt'), Path('LICENSE')]
    paths += [p for folder in ('scvpublic', 'deploy') for p in Path(folder).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    paths += [Path('scripts/check_serving.py')]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        hashes = {}
        for source, relative in [(p, p) for p in paths] + [(args.artifact, Path('artifacts/search.sqlite'))]:
            dest = root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            dest.chmod(0o644)
            with dest.open('rb') as stream:
                hashes[str(relative)] = hashlib.file_digest(stream, 'sha256').hexdigest()
        (root / 'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name, digest in sorted(hashes.items())))
        with tarfile.open(args.output, 'w:gz') as archive:
            for item in sorted(root.rglob('*')):
                if item.is_file():
                    archive.add(item, arcname=str(item.relative_to(root)), recursive=False)
    print(json.dumps({'release': str(args.output), 'bytes': args.output.stat().st_size, 'files': len(hashes)}))


if __name__ == '__main__':
    main()
