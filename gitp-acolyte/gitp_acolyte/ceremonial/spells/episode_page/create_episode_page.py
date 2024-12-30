import argparse
import logging
import os
from datetime import datetime

import coloredlogs
import yaml
from jinja2 import Environment, FileSystemLoader

from gitp_acolyte.ceremonial.spells.episode_data.args import (
    define_common_args,
    get_episode_date,
)
from gitp_acolyte.ceremonial.spells.episode_data.create import (
    path_to_episode_publishing_yml,
)
from gitp_acolyte.ceremonial.spells.episode_reference.constants import (
    DEFAULT_REFERENCE_EPISODE_YML_PATH,
    DRAFT_REFERENCE_EPISODE_OUTPUT_PATH,
    REFERENCE_EPISODE_DATE,
)
from gitp_acolyte.constants import (
    EPISODE_YAML_FILENAME,
    LOGSEQ_PAGES_FOLDER,
    get_relative_path,
)

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG",
    logger=logger,
    fmt="%(asctime)s - %(module)s - %(levelname)s - %(message)s",
)


def get_argparse_args():
    parser = argparse.ArgumentParser(description="Generate episode page.")
    define_common_args(parser)  # Use common argparse arguments
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite if the episode page already exists.",
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


def load_episode_yaml_and_ensure_context(episode_yaml_path):
    """
    Loads the episode YAML data from the given path.
    """
    with open(episode_yaml_path, "r") as f:
        data = yaml.safe_load(f)
        # Derive date_created from episode_date to avoid duplication
        if "episode_date" in data:
            episode_dt = datetime.strptime(data["episode_date"], "%Y-%m-%d")
            data["date_created"] = episode_dt.strftime("%Y-%m-%d %a")
        else:
            logger.error("episode_date not found in YAML.")
            exit(1)

        logger.debug(
            f"Loaded episode YAML for date {episode_dt} from {episode_yaml_path}"
        )
        logger.debug(f"Episode Data: {data}")
    return data


def main():
    args = get_argparse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.reference:
        output_file = DRAFT_REFERENCE_EPISODE_OUTPUT_PATH
        episode_date = REFERENCE_EPISODE_DATE
        episode_yaml_path = args.reference_dir / EPISODE_YAML_FILENAME
        if args.use_ref_ep_yml:
            episode_yaml_path = DEFAULT_REFERENCE_EPISODE_YML_PATH
    else:
        episode_date = get_episode_date(args)
        output_file = get_episode_page_path(episode_date)

        if output_file.exists() and not args.force:
            logger.warning(
                f"Episode page {output_file} already exists. Use --force to overwrite."
            )
            exit(1)

        episode_yaml_path = path_to_episode_publishing_yml(episode_date)
        if not episode_yaml_path.exists():
            logger.warning(f"Episode YAML {episode_yaml_path} does not exist.")
            exit(1)

    # Load episode YAML
    data = load_episode_yaml_and_ensure_context(episode_yaml_path)

    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader(script_dir))
    template = env.get_template("episode.jinja")
    logger.debug("Jinja environment set up and template loaded")

    # Render template with data
    output = template.render(**data)
    logger.debug("Template rendered with data")

    # Write to file
    with open(output_file, "w") as f:
        f.write(output)
        logger.info(f"Output written to {get_relative_path(output_file)}")


if __name__ == "__main__":
    main()
