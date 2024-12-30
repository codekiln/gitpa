from pathlib import Path

RECORDINGS_ROOT_FOLDER = Path("~/Documents/ableton/GitP")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# gitp-acolyte paths
ACOLYTE_DIR = REPO_ROOT / "gitp-acolyte"
ACOLYTE_PACKAGE_DIR = ACOLYTE_DIR / "gitp_acolyte"
CEREMONIAL_DIR = ACOLYTE_PACKAGE_DIR / "ceremonial"
SPELLS_DIR = CEREMONIAL_DIR / "spells"
REFERENCE_DIR = SPELLS_DIR / "episode_reference"
REFERENCE_EPISODE_DIR = REFERENCE_DIR / "ref_ep_dir"

LOGSEQ_FOLDER = REPO_ROOT / "gitp-garden"
LOGSEQ_ASSETS_FOLDER = LOGSEQ_FOLDER / "assets"
LOGSEQ_PAGES_FOLDER = LOGSEQ_FOLDER / "pages"

GITHUB_USER_CONTENT_ASSETS_BASE_URL = (
    "https://raw.githubusercontent.com/codekiln/gitpa/main/assets/Ceremony/"
)

DATE_FORMAT = "%Y-%m-%d"
SHORT_DATE_FORMAT = "%y.%m.%d"
EPISODE_YAML_FILENAME = "episode.yml"


def get_relative_path(path: Path) -> Path:
    """
    Get the path relative to the repository root.
    """
    return path.relative_to(REPO_ROOT)
