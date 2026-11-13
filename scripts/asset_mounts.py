"""Import load, public_links and MountError from gitp-garden/mise-tasks/asset/lib/mounts.py.

`mise run logseq:entity:proxy:page:sync` copies mounts.py from codekiln/logseq-encode-garden into gitp-garden."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gitp-garden' / 'mise-tasks' / 'asset' / 'lib'))
from mounts import MountError, load, public_links  # noqa: E402,F401
