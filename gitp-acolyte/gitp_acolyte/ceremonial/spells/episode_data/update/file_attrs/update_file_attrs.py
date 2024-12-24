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

def get_args():
    parser = define_common_args()
    return parser.parse_args()

def get_episode_dir(episode_date: None | datetime = None) -> Path:
    raise NotImplementedError("TODO - import function from create.py")

def main():
    args = get_args()
    episode_date = get_episode_date(args)
    if args.reference:
        episode_dir = REFERENCE_EPISODE_DIR
    else:
        episode_dir = get_episode_dir(episode_date)
    update_file_attrs(episode_dir)