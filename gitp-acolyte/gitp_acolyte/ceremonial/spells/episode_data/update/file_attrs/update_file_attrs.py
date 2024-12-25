"""
update_file_attrs.py

Given a path to a path to the logseq directory for an episode, 
update the attributes in episode.yml that point to files in that directory.

Uses AI to infer the files.

Usage:
    update_file_attrs.py <episode_date> - update the file attributes for the given episode date.
    update_file_attrs.py --reference - update the file attributes for the reference episode.
"""

import argparse
from datetime import datetime
from gitp_acolyte.ceremonial.spells.episode_data.args import define_common_args, get_episode_date
from gitp_acolyte.constants import DATE_FORMAT, REFERENCE_EPISODE_DIR
from gitp_acolyte.ceremonial.spells.episode_data.create import ensure_episode_dir_and_yaml_exists
import logging
import coloredlogs

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_args():
    parser = define_common_args()
    return parser.parse_args()


def update_file_attrs(episode_dir, args):
    raise NotImplementedError("This function is not implemented yet.")



def main():
    args = get_args()
    episode_date = get_episode_date(args)
    logger.debug(f"Episode date: {episode_date}")
    episode_dir, _ = ensure_episode_dir_and_yaml_exists(episode_date, args)
    logger.debug(f"Episode directory: {episode_dir}")
    update_file_attrs(episode_dir, args)
    logger.info("File attributes updated successfully.")

if __name__ == "__main__":
    main()