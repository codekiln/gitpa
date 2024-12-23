from pathlib import Path

RECORDINGS_ROOT_FOLDER = Path('~/Documents/ableton/GitP')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# gitp-acolyte paths
ACOLYTE_DIR = REPO_ROOT / 'gitp-acolyte'
CEREMONIAL_DIR = ACOLYTE_DIR / 'ceremonial'
SPELLS_DIR = CEREMONIAL_DIR / 'spells'
REFERENCE_DIR = SPELLS_DIR / 'episode_reference'
REFERENCE_EPISODE_DIR = REFERENCE_DIR / 'ref_ep_dir'

LOGSEQ_FOLDER = REPO_ROOT / 'gitp-garden'
LOGSEQ_ASSETS_FOLDER = LOGSEQ_FOLDER / 'assets'
LOGSEQ_PAGES_FOLDER = LOGSEQ_FOLDER / 'pages'

DATE_FORMAT = '%Y-%m-%d'
SHORT_DATE_FORMAT = '%y.%m.%d'
EPISODE_YAML_FILENAME = 'episode.yml'