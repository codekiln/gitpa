"""Asset mounts of a garden, read with the mounts.py the proxy page sync task brings into gitp-garden."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gitp-garden' / 'mise-tasks' / 'asset' / 'lib'))
from mounts import MountError, load, public_links  # noqa: E402,F401
