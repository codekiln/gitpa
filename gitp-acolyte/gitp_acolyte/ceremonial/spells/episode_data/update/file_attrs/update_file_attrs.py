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
import json
from gitp_acolyte.ceremonial.spells.episode_data.args import define_common_args, get_episode_date
from gitp_acolyte.ceremonial.spells.episode_reference.episode_schema import PodcastEpisodePublicationData
from gitp_acolyte.constants import DATE_FORMAT, EPISODE_YAML_FILENAME, REFERENCE_EPISODE_DIR, get_relative_path
from gitp_acolyte.ceremonial.spells.episode_data.create import ensure_episode_dir_and_yaml_exists
import logging
import coloredlogs
from dotenv import load_dotenv
from openai import OpenAI
import os
from pathlib import Path
import yaml
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_args():
    parser = define_common_args()
    return parser.parse_args()


def get_system_prompt() -> str:
    """
    Load the system prompt from update_file_attrs_system_prompt.md
    """
    script_dir = Path(__file__).parent
    prompt_path = script_dir / "update_file_attrs_system_prompt.md"
    logger.debug(f"Loading system prompt from {get_relative_path(prompt_path)}")
    with prompt_path.open() as f:
        return f.read()

def get_user_prompt(podcast_directory_info: str) -> str:
    """
    Load the user prompt from update_file_attrs_user_prompt.md
    """
    script_dir = Path(__file__).parent
    prompt_path = script_dir / "update_file_attrs_user_prompt.md"
    logger.debug(f"Loading user prompt from {get_relative_path(prompt_path)}")
    with prompt_path.open() as f:
        prompt = f.read()
    return prompt.format(podcast_directory_info=podcast_directory_info)


def call_openai(podcast_directory_info: str) -> ParsedChatCompletion[PodcastEpisodePublicationData]:
    load_dotenv()
    client = OpenAI()

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(podcast_directory_info)

    logger.debug("Calling OpenAI ...")
    podcast_episode_publication_data: PodcastEpisodePublicationData = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="gpt-4o-mini",
        response_format=PodcastEpisodePublicationData
    )
    return podcast_episode_publication_data


def get_episode_dir_ai_info(pathlib_dir_obj: Path) -> dict:
    """
    Get directory information similar to `ls -la`.
    Returns a dictionary with directory name, and for each file, a file name, 
    the size of the file, the created and last modified date in a standard ISO time format.
    """
    dir_info = {
        "directory_name": pathlib_dir_obj.name,
        "files": []
    }
    for file in pathlib_dir_obj.iterdir():
        if file.is_file():
            file_info = {
                "file_name": file.name,
                "size": file.stat().st_size,
                "created": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                "last_modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            }
            dir_info["files"].append(file_info)
    return dir_info

def serialize_episode_dir_ai_info(dir_info: dict) -> str:
    """
    Serialize the directory information to a string.
    """
    serialized_episode_directory_info = json.dumps(dir_info, indent=4)
    logger.debug(f"{serialized_episode_directory_info=}")
    return serialized_episode_directory_info


def update_file_attrs(episode_dir, args):
    dir_info = get_episode_dir_ai_info(episode_dir)
    serialized_dir_info = serialize_episode_dir_ai_info(dir_info)
    podcast_episode_publication_data: ParsedChatCompletion[PodcastEpisodePublicationData] = call_openai(serialized_dir_info)
    write_episode_yaml(podcast_episode_publication_data, episode_dir, args)    


def write_episode_yaml(podcast_episode_publication_data: ParsedChatCompletion[PodcastEpisodePublicationData], episode_dir: Path, args):
    """
    Write the episode data to the episode.yml file.
    If args.reference is True, write to the reference episode directory.
    """
    if args.reference:
        yaml_path = REFERENCE_EPISODE_DIR / EPISODE_YAML_FILENAME
    else:
        yaml_path = episode_dir / EPISODE_YAML_FILENAME

    with yaml_path.open('w') as f:
        pydantic_serialized_to_yaml_string = serialize_pydantic_to_yaml(podcast_episode_publication_data)
        f.write(pydantic_serialized_to_yaml_string)

    logger.debug(f"Written episode data to {get_relative_path(yaml_path)}")


def serialize_pydantic_to_yaml(podcast_episode_publication_data: ParsedChatCompletion[PodcastEpisodePublicationData]) -> str:
    """
    Serialize the PodcastEpisodePublicationData to a YAML string.
    """
    data_dict = podcast_episode_publication_data.model_dump()
    data_dict_str = json.dumps(data_dict, indent=4)
    logger.debug(f"podcast_episode_publication_data: {data_dict_str}")

    parsed_response_json = podcast_episode_publication_data.choices[0].message.content
    episode_dict = json.loads(parsed_response_json)
    yaml_string = yaml.dump(episode_dict, sort_keys=True, default_flow_style=False)
    return yaml_string


def main():
    args = get_args()
    episode_date = get_episode_date(args)
    logger.debug(f"Episode date: {episode_date}")
    episode_dir, _ = ensure_episode_dir_and_yaml_exists(episode_date, args)
    logger.debug(f"Episode directory: {get_relative_path(episode_dir)}")
    update_file_attrs(episode_dir, args)
    logger.info("File attributes updated successfully.")

if __name__ == "__main__":
    main()