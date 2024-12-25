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

def get_args():
    parser = define_common_args()
    return parser.parse_args()


def main():
    args = get_args()
    episode_date = get_episode_date(args)
    episode_dir, _ = ensure_episode_dir_and_yaml_exists(episode_date, args)
    update_file_attrs(episode_dir)