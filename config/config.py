import os
from dataclasses import dataclass

from dotenv import load_dotenv, find_dotenv


@dataclass
class Config:
    token: str
    group_id: str

    def __init__(self):
        load_dotenv(find_dotenv())
        self._set()

    def _set(self):
        self.token = os.getenv("BOT_TOKEN")
        self.group_id = os.getenv("GROUP_ID")
