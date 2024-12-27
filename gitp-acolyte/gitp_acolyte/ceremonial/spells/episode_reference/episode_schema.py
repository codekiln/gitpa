from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class PodcastEpisodePublicationData(BaseModel):
    """
    Data for a single published podcast episode.
    """

    episode_title: str = Field(
        #  fix BadRequestError 400 because `'default'` is not permitted in structured output
        # default="Ceremony",
        description="The title of the podcast episode; should default to 'Ceremony' if no further information is available."
    )
    episode_date: str = Field(..., description="The publication date of the episode in YYYY-MM-DD format.")
    audio_file: str = Field(..., description="The file name of the episode's audio.")
    description: str = Field(..., description="A text description of the episode content. Leave blank if not enough info to make a description is available.")
    patch_files: List[str] = Field(default_factory=list, description="Optional list of Microfreak synthesizer patch file names associated with this episode.")
    midi_files: List[str] = Field(default_factory=list, description="Optional list of MIDI file names associated with this episode.")
