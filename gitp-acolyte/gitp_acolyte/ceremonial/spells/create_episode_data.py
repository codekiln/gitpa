from pathlib import Path

RECORDINGS_ROOT_FOLDER = Path('~/Documents/ableton/GitP')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
LOGSEQ_FOLDER = REPO_ROOT / 'gitp-garden'
LOGSEQ_ASSETS_FOLDER = LOGSEQ_FOLDER / 'assets'

def main():
    directories = [RECORDINGS_ROOT_FOLDER.expanduser(), LOGSEQ_FOLDER, LOGSEQ_ASSETS_FOLDER]
    
    for directory in directories:
        if directory.exists() and directory.is_dir():
            print(f"Directory {directory} exists and is accessible.")
        else:
            print(f"Directory {directory} does not exist or is not accessible.")

if __name__ == "__main__":
    main()