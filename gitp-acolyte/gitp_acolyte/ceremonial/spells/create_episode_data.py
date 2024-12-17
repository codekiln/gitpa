from pathlib import Path
import argparse
from datetime import datetime

RECORDINGS_ROOT_FOLDER = Path('~/Documents/ableton/GitP')

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
LOGSEQ_FOLDER = REPO_ROOT / 'gitp-garden'
LOGSEQ_ASSETS_FOLDER = LOGSEQ_FOLDER / 'assets'

DATE_FORMAT = '%Y-%m-%d'
SHORT_DATE_FORMAT = '%y.%m.%d'

def validate_directories():
    directories = [RECORDINGS_ROOT_FOLDER.expanduser(), LOGSEQ_FOLDER, LOGSEQ_ASSETS_FOLDER]
    
    for directory in directories:
        if directory.exists() and directory.is_dir():
            # print(f"Directory {directory} exists and is accessible.")
            pass
        else:
            print(f"Directory {directory} does not exist or is not accessible.")

def define_argparse_that_takes_a_date():
    """
    Defines an argparse that takes a date as an argument.
    The default date should be today.
    """
    parser = argparse.ArgumentParser(description="Process a date.")
    parser.add_argument(
        'date',
        type=lambda s: datetime.strptime(s, DATE_FORMAT),
        default=datetime.today().strftime(DATE_FORMAT),
        nargs='?',
        help=f'Date in {DATE_FORMAT} format. Default is today.'
    )
    args = parser.parse_args()
    return args

def construct_episode_recording_dir_name(episode_date):
    """
    Constructs the episode recording directory name.
    Should handle the date format so the directories are like "GitP.24.12.04 Project"
    """
    episode_recording_dir_name = f"GitP.{episode_date.strftime(SHORT_DATE_FORMAT)} Project"
    return episode_recording_dir_name

def construct_path_to_episode_recording_dir(episode_date):
    """
    Constructs the path to the episode recording directory.
    """
    episode_recording_dir_name = construct_episode_recording_dir_name(episode_date)
    episode_recording_dir = RECORDINGS_ROOT_FOLDER / episode_recording_dir_name
    return episode_recording_dir

def episode_recording_dir_exists(episode_date):
    """
    Checks if the episode recording directory exists.
    """
    path_to_episode_recording_dir = construct_path_to_episode_recording_dir(episode_date)
    return path_to_episode_recording_dir.exists()



if __name__ == "__main__":
    validate_directories()
    args = define_argparse_that_takes_a_date()
    episode_date = args.date
    print(f"Episode date: {episode_date}")
    path_to_episode_recording_dir = construct_path_to_episode_recording_dir(episode_date)
    print(f"Path to episode recording directory: {path_to_episode_recording_dir}")
    episode_recording_dir_exists = episode_recording_dir_exists(episode_date)
    print(f"Episode recording directory exists: {episode_recording_dir_exists}")