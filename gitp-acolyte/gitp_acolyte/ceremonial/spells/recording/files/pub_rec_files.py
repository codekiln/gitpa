import argparse
import logging
import sys
from pathlib import Path

import coloredlogs
from gitp_acolyte.ceremonial.spells.episode_data.args import (
    define_common_args,
    get_episode_date,
)
from gitp_acolyte.ceremonial.spells.episode_data.create import (
    episode_publishing_dir_exists,
    recording_dir_exists,
)
from gitp_acolyte.constants import get_relative_path

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG",
    logger=logger,
    fmt="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
)


HELP_DOCSTRING = """
Sync files from the episode recording directory to the episode publishing directory.
"""


def define_args():
    """
    Defines argparse arguments.
    """
    parser = argparse.ArgumentParser(description=HELP_DOCSTRING)
    parser = define_common_args()
    return parser.parse_args()


def sync_files(src_dir: Path, dest_dir: Path):
    """
    Sync files from the source directory to the destination directory.
    """
    for item in src_dir.iterdir():
        if item.is_file():
            # shutil.copy(item, dest_dir / item.name)
            logger.info(f"Would have copied {item.name}")


def main():
    args = define_args()
    episode_date = get_episode_date(args)
    logger.debug(f"Episode date: {episode_date}")

    if not recording_dir_exists(episode_date, args):
        logger.error("Recording directory does not exist.")
        return

    src_dir, src_dir_exists = recording_dir_exists(episode_date, args)
    if not src_dir_exists:
        sys.exit(1)
    dest_dir, dest_dir_exists = episode_publishing_dir_exists(episode_date, args)
    if not dest_dir_exists:
        sys.exit(1)

    logger.debug(f"Source directory: '{src_dir}'")
    logger.debug(f"Destination directory: '{get_relative_path(dest_dir)}'")

    sync_files(src_dir, dest_dir)
    logger.info("Files synced successfully.")


if __name__ == "__main__":
    main()
