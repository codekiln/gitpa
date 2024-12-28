import argparse
from datetime import datetime
from pathlib import Path
from gitp_acolyte.constants import DATE_FORMAT, REFERENCE_EPISODE_DIR, get_relative_path
from gitp_acolyte.ceremonial.spells.episode_reference.constants import DEFAULT_REFERENCE_EPISODE_YML_PATH, REFERENCE_EPISODE_DATE


def define_common_reference_file_args(parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """
    Defines common argparse arguments for operating on reference versions of the files.
    """
    parser.add_argument(
        '--reference',
        action='store_true',
        help='Use the reference episode. Used for testing the script.'
    )

    ref_ep_dir_relpath = str(get_relative_path(REFERENCE_EPISODE_DIR))
    ref_ep_dir_help = f'Path to the reference episode directory. Default is {ref_ep_dir_relpath}.'
    parser.add_argument(
        '--reference-dir',
        type=Path,
        default=REFERENCE_EPISODE_DIR,
        help=ref_ep_dir_help
    )

    ref_ep_yml_relpath = str(get_relative_path(DEFAULT_REFERENCE_EPISODE_YML_PATH))
    ref_ep_yml_help = f'Use the reference episode YAML file. Default is "{ref_ep_yml_relpath}".'
    parser.add_argument(
        '--use-ref-ep-yml',
        action='store_true',
        help=ref_ep_yml_help,
        default=False
    )
    
    return parser


def define_common_args(parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """
    Defines common argparse arguments.
    The default date should be today.
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Process a date.")
    
    parser.add_argument(
        'date',
        type=lambda s: datetime.strptime(s, DATE_FORMAT),
        default=datetime.today().strftime(DATE_FORMAT),
        nargs='?',
        help=f'Date in {{DATE_FORMAT}} format. Default is today.'
    )
    define_common_reference_file_args(parser)

    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Recreate the episode.yml file if it already exists.'
    )
    return parser

def get_episode_date(args):
    """
    Returns the episode date based on the provided arguments.
    """
    if args.reference:
        return REFERENCE_EPISODE_DATE
    return args.date
