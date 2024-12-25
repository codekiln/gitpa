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
from gitp_acolyte.constants import DATE_FORMAT, REFERENCE_EPISODE_DIR, get_relative_path
from gitp_acolyte.ceremonial.spells.episode_data.create import ensure_episode_dir_and_yaml_exists
import logging
import coloredlogs
from dotenv import load_dotenv
from openai import OpenAI
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_args():
    parser = define_common_args()
    return parser.parse_args()


def get_system_prompt() -> str:
    """
    Load the system prompt from update_file_attrs_prompt.md
    """
    script_dir = Path(__file__).parent
    prompt_path = script_dir / "update_file_attrs_prompt.md"
    logger.debug(f"Loading system prompt from {get_relative_path(prompt_path)}")
    with prompt_path.open() as f:
        return f.read()


def call_openai(user_query: str) -> dict:
    load_dotenv()
    client = OpenAI()

    system_prompt = get_system_prompt()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_query,
            }
        ],
        model="gpt-4o-mini",
    )
    return chat_completion


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


def update_file_attrs(episode_dir, args):
    logger.info("Calling OpenAI ...")
    dir_info = get_episode_dir_ai_info(episode_dir)
    logger.debug(f"Directory info: {dir_info}")
    query = "What is the meaning of life?"
    openai_response = call_openai(query)
    logger.debug(f"{openai_response=}")
    raise NotImplementedError("This function is not implemented yet.")


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