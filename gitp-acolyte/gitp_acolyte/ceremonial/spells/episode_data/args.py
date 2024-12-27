import argparse
from datetime import datetime
from gitp_acolyte.constants import DATE_FORMAT
from gitp_acolyte.ceremonial.spells.episode_reference.constants import REFERENCE_EPISODE_DATE

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
        help=f'Date in {DATE_FORMAT} format. Default is today.'
    )
    parser.add_argument(
        '--reference',
        action='store_true',
        help='Use the reference episode date.'
    )
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
