import yaml
from jinja2 import Environment, FileSystemLoader
import os
import logging
import coloredlogs
import argparse
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DATE_FORMAT = '%Y-%m-%d'

def get_argparse_args():
    parser = argparse.ArgumentParser(description="Generate episode page.")
    parser.add_argument(
        '--reference',
        action='store_true',
        help='Use reference_episode.yml and generate reference_output.md'
    )
    parser.add_argument(
        'date',
        type=lambda s: datetime.strptime(s, DATE_FORMAT),
        nargs='?',
        help=f'Date in {DATE_FORMAT} format. Required if --reference is not supplied.'
    )
    return parser.parse_args()

def main():
    args = get_argparse_args()

    if args.reference:
        # Determine the path to reference_episode.yml
        script_dir = os.path.dirname(os.path.abspath(__file__))
        reference_yml_path = os.path.join(script_dir, 'reference_episode.yml')
        output_file = os.path.join(script_dir, 'reference_output.md')
    else:
        if not args.date:
            raise ValueError("Date is required if --reference is not supplied.")
        raise NotImplementedError("Non-reference mode is not implemented yet.")

    # Load reference_episode.yml
    with open(reference_yml_path, 'r') as f:
        data = yaml.safe_load(f)
        logger.debug("Loaded reference_episode.yml")

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
