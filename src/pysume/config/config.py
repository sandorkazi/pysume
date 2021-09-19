import yaml  # type: ignore
from pathlib import PurePath
from typing import Dict, Optional


class Config(dict[str, str]):

    def __init__(self, config_path: PurePath, defaults: Optional[Dict[str, str]] = None):
        if defaults is None:
            defaults = {}
        with open(config_path) as fin:
            defaults.update(yaml.safe_load(fin))
            super().__init__(**defaults)
