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
    if result.returncode or not paths:
        raise LinkError(f'ghq has no checkout of {address}; clone it with `ghq get {address}`')
    if len(paths) > 1:
        raise LinkError(f'ghq lists more than one checkout of {address}: {", ".join(paths)}')
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
        link_path = garden / mount['path']
        if link_path.is_symlink() and link_path.resolve() == target.resolve():
            lines.append(f'{name}: {link_path} already links {target}')
            continue
        if link_path.is_symlink() or link_path.exists():
            raise LinkError(f'{link_path} already exists and is not a link to {target}; move it aside and run again')
        link_path.parent.mkdir(parents=True, exist_ok=True)
        link_path.symlink_to(target, target_is_directory=True)
        lines.append(f'{name}: linked {link_path} to {target}')
    return lines


if __name__ == '__main__':
    try:
        print('\n'.join(link()) or 'gitp-garden/asset-mounts.toml borrows no mounts')
    except (LinkError, MountError) as error:
        sys.exit(str(error))
