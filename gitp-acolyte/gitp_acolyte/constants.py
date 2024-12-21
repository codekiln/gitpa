from pathlib import Path

RECORDINGS_ROOT_FOLDER = Path('~/Documents/ableton/GitP')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOGSEQ_FOLDER = REPO_ROOT / 'gitp-garden'
LOGSEQ_ASSETS_FOLDER = LOGSEQ_FOLDER / 'assets'
LOGSEQ_PAGES_FOLDER = LOGSEQ_FOLDER / 'pages'

DATE_FORMAT = '%Y-%m-%d'
SHORT_DATE_FORMAT = '%y.%m.%d'
EPISODE_YAML_FILENAME = 'episode.yml'
