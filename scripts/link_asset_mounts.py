"""Link each mount that gitp-garden borrows to the same folder in the source garden's ghq checkout.

When a proxied page links ../assets/.remote/<mount>/<file>, Logseq on the Mac opens that file from the source garden's checkout."""
from pathlib import Path
import subprocess
import sys

from asset_mounts import MountError, load

GARDEN = Path(__file__).resolve().parents[1] / 'gitp-garden'


class LinkError(RuntimeError):
    pass


def ghq_path(address):
    result = subprocess.run(['ghq', 'list', '--full-path', '--exact', address], capture_output=True, text=True)
    paths = result.stdout.split()
    if result.returncode or len(paths) != 1:
        raise LinkError(f'ghq finds no single checkout of {address}; clone it with `ghq get {address}`')
    return Path(paths[0])


def link(garden=GARDEN, locate=ghq_path):
    """Return one line per borrowed mount saying what was linked."""
    lines = []
    for name, mount in load(garden).items():
        if 'source' not in mount:
            continue
        target = locate(mount['source']) / mount['path']
        if not target.is_dir():
            raise LinkError(f'{target} is missing; run `mise run asset:fetch` in {mount["source"]} first')
        here = garden / mount['path']
        if here.is_symlink() and here.resolve() == target.resolve():
            lines.append(f'{name}: {here} already links {target}')
            continue
        if here.is_symlink() or here.exists():
            raise LinkError(f'{here} already exists and is not a link to {target}; move it aside and run again')
        here.parent.mkdir(parents=True, exist_ok=True)
        here.symlink_to(target, target_is_directory=True)
        lines.append(f'{name}: linked {here} to {target}')
    return lines


if __name__ == '__main__':
    try:
        print('\n'.join(link()) or 'gitp-garden/asset-mounts.toml borrows no mounts')
    except (LinkError, MountError) as error:
        sys.exit(str(error))
