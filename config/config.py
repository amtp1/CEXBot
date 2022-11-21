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
        self.token = os.getenv('BOT_TOKEN')
        self.main_group_id = os.getenv('MAIN_GROUP_ID')
        self.sub_group_id = os.getenv('SUB_GROUP_ID')
        self.sub_group_url = os.getenv('SUB_GROUP_URL')
