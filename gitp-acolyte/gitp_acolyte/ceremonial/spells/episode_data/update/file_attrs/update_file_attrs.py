"""
update_file_attrs.py

Given a path to a path to the logseq directory for an episode, 
update the attributes in episode.yml that point to files in that directory.

Uses AI to infer the files.

Usage:
    update_file_attrs.py <episode_date> - update the file attributes for the given episode date.
    update_file_attrs.py --reference - update the file attributes for the reference episode.
"""

from gitp_acolyte.ceremonial.spells.episode_data.create import get_episode_dir
from gitp_acolyte.ceremonial.spells.episode_reference.constants import REFERENCE_EPISODE_DATE_STR, REFERENCE_EPISODE_DATE
from gitp_acolyte.constants import DATE_FORMAT, REFERENCE_EPISODE_DIR

def get_args():
    parser = argparse.ArgumentParser(description="Update the file attributes in episode.yml.")
    parser.add_argument("episode_date", type=str, help="The episode date in the format YYYY-MM-DD.")
    parser.add_argument("--reference", action="store_true", help="Update the file attributes for the reference episode.")
    return parser.parse_args()

def get_episode_dir(episode_date: None | datetime = None) -> Path:
    raise NotImplementedError("TODO - import function from create.py")

def main():
    args = get_args()
    episode_date = args.episode_date
    if args.reference:
        episode_date = REFERENCE_EPISODE_DATE
        episode_dir = REFERENCE_EPISODE_DIR
    else:
        episode_date = datetime.strptime(episode_date, DATE_FORMAT)
        episode_dir = get_episode_dir(episode_date)
    update_file_attrs(episode_dir)