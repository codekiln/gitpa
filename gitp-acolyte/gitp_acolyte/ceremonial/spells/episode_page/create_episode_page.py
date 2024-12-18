import yaml
from jinja2 import Environment, FileSystemLoader
import os
import logging
import coloredlogs

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # Determine the path to reference_episode.yml
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reference_yml_path = os.path.join(script_dir, 'reference_episode.yml')

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
    output_file = os.path.join(script_dir, 'episode_output.md')
    with open(output_file, 'w') as f:
        f.write(output)
        logger.info(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
