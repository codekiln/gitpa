from pathlib import Path
import yaml
import logging
import coloredlogs
from gitp_acolyte.constants import (
    DATE_FORMAT,
    EPISODE_YAML_FILENAME,
    LOGSEQ_ASSETS_FOLDER,
    LOGSEQ_FOLDER,
    RECORDINGS_ROOT_FOLDER,
    REFERENCE_EPISODE_DIR,
    REPO_ROOT,
    SHORT_DATE_FORMAT,
)
from gitp_acolyte.ceremonial.spells.episode_reference.constants import REFERENCE_EPISODE_DATE
from gitp_acolyte.ceremonial.spells.episode_data.args import define_common_args, get_episode_date

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def validate_directories():
    directories = [RECORDINGS_ROOT_FOLDER.expanduser(), LOGSEQ_FOLDER, LOGSEQ_ASSETS_FOLDER]
    
    for directory in directories:
        if directory.exists() and directory.is_dir():
            # logger.debug(f"Directory {directory} exists and is accessible.")
            pass
        else:
            logger.warning(f"Directory {directory} does not exist or is not accessible.")

def define_args():
    """
    Defines argparse arguments.
    """
    parser = define_common_args()
    return parser.parse_args()

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

def construct_path_to_episode_publishing_dir(episode_date, args):
    """
    Constructs the path to the episode publishing directory.
    """
    if args.reference:
        ref_ep_dir = REFERENCE_EPISODE_DIR
        expected_ref_ep_dir = REPO_ROOT / "gitp-acolyte/gitp_acolyte/ceremonial/spells/episode_reference/ref_ep_dir"
        assert ref_ep_dir == expected_ref_ep_dir, f"Reference episode directory is not as expected: \nactual:   '{ref_ep_dir}' \nexpected: '{expected_ref_ep_dir}'"
        return REFERENCE_EPISODE_DIR
    year = episode_date.strftime('%Y')
    month = episode_date.strftime('%m')
    day = episode_date.strftime('%d')
    episode_publishing_dir = LOGSEQ_ASSETS_FOLDER / "Ceremony" / year / month / day
    return episode_publishing_dir

def ensure_episode_publishing_dir(episode_date, args):
    """
    Ensures the episode publishing directory exists.
    Returns True if the directory was created, False if it already existed.
    """
    path_to_episode_publishing_dir = construct_path_to_episode_publishing_dir(episode_date, args)
    if not path_to_episode_publishing_dir.exists():
        path_to_episode_publishing_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Episode publishing directory created: {path_to_episode_publishing_dir}")
        return True
    logger.debug(f"Episode publishing directory already exists: {path_to_episode_publishing_dir}")
    return False

def path_to_episode_publishing_yml(episode_date, args):
    """
    Constructs the path to the episode.yml file in the episode publishing directory.
    """
    path_to_episode_publishing_dir = construct_path_to_episode_publishing_dir(episode_date, args)
    return path_to_episode_publishing_dir / EPISODE_YAML_FILENAME

def ensure_episode_yaml(episode_date, args):
    """
    Ensures that episode.yml exists in the episode publishing directory
    """
    episode_yaml_path = path_to_episode_publishing_yml(episode_date, args)
    
    if episode_yaml_path.exists() and args.recreate:
        episode_yaml_path.unlink()
        logger.info(f"--recreate: Removed existing episode.yml file: {episode_yaml_path}")

    if not episode_yaml_path.exists():
        episode_data = {
            'episode_date': episode_date.strftime(DATE_FORMAT)
        }
        with episode_yaml_path.open('w') as file:
            yaml.dump(episode_data, file)
        return True
    else:
        with episode_yaml_path.open('r') as file:
            episode_data = yaml.safe_load(file)
        
        if 'episode_date' not in episode_data or episode_data['episode_date'] != episode_date.strftime(DATE_FORMAT):
            episode_data['episode_date'] = episode_date.strftime(DATE_FORMAT)
            with episode_yaml_path.open('w') as file:
                yaml.dump(episode_data, file)
            return True
    return False

def recording_dir_exists(episode_date, args):
    path_to_episode_recording_dir = construct_path_to_episode_recording_dir(episode_date)
    logger.debug(f"Path to episode recording directory: {path_to_episode_recording_dir}")
    if not path_to_episode_recording_dir.exists():
        if args.reference:
            logger.info(
                "Will not create reference episode recording directory. "
                f"It would have been at {path_to_episode_recording_dir}. "
            )
        else:
            logger.error(f"Episode recording directory does not exist: {path_to_episode_recording_dir}")
            logger.error("Please create the episode recording directory.")
        return False
    return True

def episode_publishing_dir_exists(episode_date, args) -> tuple[Path, bool]:
    path_to_episode_publishing_dir = construct_path_to_episode_publishing_dir(episode_date, args)
    logger.debug(f"Path to episode publishing directory: {path_to_episode_publishing_dir}")
    if not path_to_episode_publishing_dir.exists():
        if args.reference:
            logger.info(
                "Reference episode directory does not exist. "
            )
        else:
            logger.debug(f"Episode publishing directory does not exist: {path_to_episode_publishing_dir}")
        return path_to_episode_publishing_dir, False
    return path_to_episode_publishing_dir, True

def ensure_episode_dir_and_yaml_exists(episode_date, args) -> tuple[Path, Path]:
    """
    Ensures the episode publishing directory and episode.yml file exist.
    Returns a tuple of:
    - the path to the episode publishing directory
    - the path to the episode.yml file
    """
    ep_pub_dir, ep_pub_dir_exists = episode_publishing_dir_exists(episode_date, args)
    
    if not ep_pub_dir_exists:
        episode_publishing_dir_created = ensure_episode_publishing_dir(episode_date, args)
    
    episode_yaml_created = ensure_episode_yaml(episode_date, args)
    logger.debug(f"Episode YAML created or updated: {episode_yaml_created}")
    return ep_pub_dir, path_to_episode_publishing_yml(episode_date, args)

def main():
    validate_directories()
    args = define_args()
    episode_date = get_episode_date(args)
    logger.debug(f"Episode date: {episode_date}")

    # check the episode recording dir
    # we're not doing any info with this for now
    # eventually, maybe call a script to create the recording dir
    recording_dir_exists(episode_date, args)

    ensure_episode_dir_and_yaml_exists(episode_date, args)

if __name__ == "__main__":
    main()
