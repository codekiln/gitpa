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
from gitp_acolyte.ceremonial.spells.recording.files.rec_file_constants import (
    FILE_SUFFIXES_TO_SYNC,
    REC_DIR_SUBDIRS_TO_SEARCH,
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the file sync without making any changes.",
    )
    return parser.parse_args()


def filter_files_to_publish(src_dir: Path) -> list[Path]:
    """
    Iterates through files in src_dir and any subdirectories in
    REC_DIR_SUBDIRS_TO_SEARCH, and only returns files with extensions
    in FILE_SUFFIXES_TO_SYNC.
    """
    files_to_sync = []
    for subdir in REC_DIR_SUBDIRS_TO_SEARCH:
        for item in (src_dir / subdir).iterdir():
            if item.is_file() and item.suffix in FILE_SUFFIXES_TO_SYNC:
                files_to_sync.append(item)
    return files_to_sync


def sync_files(src_dir: Path, dest_dir: Path, dry_run: bool):
    """
    Sync files from the source directory to the destination directory,
    first filtering files with filter_files_to_publish. This function
    will only write files to the destination directory if the file does not
    yet exist in the destination directory or if the file in the destination
    directory is older than the file in the source directory.
    The directory structure is not preserved, so any files that are returned
    from filter_files_to_publish will be copied to the destination directory.
    """
    files_to_publish = filter_files_to_publish(src_dir)
    for file in files_to_publish:
        dest_file = dest_dir / file.name
        if not dest_file.exists():
            if dry_run:
                logger.info(f"Would copy '{file}' to '{get_relative_path(dest_file)}'")
            else:
                logger.debug(f"Copying '{file}' to '{get_relative_path(dest_file)}'")
                file.replace(dest_file)
        elif file.stat().st_mtime > dest_file.stat().st_mtime:
            if dry_run:
                logger.info(
                    f"Would overwrite '{get_relative_path(dest_file)}' with newer file '{file}'"
                )
            else:
                logger.warning(
                    f"Overwriting '{get_relative_path(dest_file)}' with newer file '{file}'"
                )
                file.replace(dest_file)
        else:
            logger.debug(
                f"Skipping sync; '{get_relative_path(dest_file)}' is newer than source file '{file}'"
            )


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

    sync_files(src_dir, dest_dir, args.dry_run)

    if args.dry_run:
        logger.info("Dry run complete. No files were synced.")
    else:
        logger.info("Files synced successfully.")


if __name__ == "__main__":
    main()
