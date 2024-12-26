from datetime import date
from typing import List
from pydantic import BaseModel, Field

class PodcastEpisodePublicationData(BaseModel):
    episode_title: str = Field(...)
    episode_date: date = Field(...)
    audio_file: str = Field(...)
    description: str = Field(...)
    assets_base_url: str = Field(...)
    patches: List[str] = Field(default_factory=list)
    midi_files: List[str] = Field(default_factory=list)
