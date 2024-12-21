import yaml
from jinja2 import Environment, FileSystemLoader
import os
import logging
import coloredlogs
import argparse
from datetime import datetime
from pathlib import Path
from gitp_acolyte.constants import (
    REPO_ROOT,
    LOGSEQ_FOLDER,
    LOGSEQ_ASSETS_FOLDER,
    LOGSEQ_PAGES_FOLDER,
    DATE_FORMAT,
    SHORT_DATE_FORMAT,
    EPISODE_YAML_FILENAME
)
from gitp_acolyte.ceremonial.spells.create_episode_data import (
    path_to_episode_publishing_yml,
    ensure_episode_yaml
)

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(module)s - %(levelname)s - %(message)s')

def get_argparse_args():
    parser = argparse.ArgumentParser(description="Generate episode page.")
    parser.add_argument(
        '--reference',
        action='store_true',
        help='Use reference_episode.yml and generate reference_output.md'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite if the episode page already exists.'
    )
    parser.add_argument(
        'date',
        type=lambda s: datetime.strptime(s, DATE_FORMAT),
        nargs='?',
        help=f'Date in {DATE_FORMAT} format. Required if --reference is not supplied.'
    )
    return parser.parse_args()

def get_episode_page_filename(episode_date):
    """
    Constructs the episode page filename.
    """
    return f"Ceremony___{episode_date.strftime('%Y')}___{episode_date.strftime('%m')}___{episode_date.strftime('%d')}.md"

def get_episode_page_path(episode_date):
    """
    Constructs the full path to the episode page.
    """
    filename = get_episode_page_filename(episode_date)
    return LOGSEQ_PAGES_FOLDER / filename

def load_episode_yaml(episode_yaml_path):
    """
    Loads the episode YAML data from the given path.
    """
    with open(episode_yaml_path, 'r') as f:
        data = yaml.safe_load(f)
        # Derive date_created from episode_date to avoid duplication
        if 'episode_date' in data:
            episode_dt = datetime.strptime(data['episode_date'], '%Y-%m-%d')
            data['date_created'] = episode_dt.strftime('%Y-%m-%d %a')
        else:
            logger.error("episode_date not found in YAML.")
            exit(1)

        logger.debug(f"Loaded episode YAML for date {episode_dt} from {episode_yaml_path}")
        logger.debug(f"Episode Data: {data}")
    return data

def main():
    args = get_argparse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.reference:
        # Determine the path to reference_episode.yml
        episode_yaml_path = os.path.join(script_dir, 'reference_episode.yml')
        output_file = os.path.join(script_dir, 'reference_output.md')
        episode_date = None
    else:
        if not args.date:
            raise ValueError("Date is required if --reference is not supplied.")
        
        episode_date = args.date
        output_file = get_episode_page_path(episode_date)
        
        if output_file.exists() and not args.force:
            logger.warning(f"Episode page {output_file} already exists. Use --force to overwrite.")
            exit(1)
        
        episode_yaml_path = path_to_episode_publishing_yml(episode_date)
        if not episode_yaml_path.exists():
            logger.warning(f"Episode YAML {episode_yaml_path} does not exist.")
            exit(1)

    # Load episode YAML
    data = load_episode_yaml(episode_yaml_path)

    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template('episode.jinja')
    logger.debug("Jinja environment set up and template loaded")

    # Render template with data
    output = template.render(**data)
    logger.debug("Template rendered with data")

    # Write to file
    with open(output_file, 'w') as f:
        f.write(output)
        logger.info(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
