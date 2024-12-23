from datetime import datetime
from gitp_acolyte.constants import DATE_FORMAT

REFERENCE_EPISODE_DATE_STR = "2024-12-04"

REFERENCE_EPISODE_DATE = datetime.strptime(REFERENCE_EPISODE_DATE_STR, DATE_FORMAT)