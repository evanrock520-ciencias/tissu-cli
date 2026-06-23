from dataclasses import dataclass
from enum import Enum


@dataclass
class CLIState:
    json_output: bool = False
    quiet: bool = False


class FilesSuported(Enum):
    JSON = ".json"
    TISSU = ".tissu"


class Type(Enum):
    SCENE = "scenes"
    PHYSICS = "physics"
    MATERIAL = "materials"
    STATE = "states"
