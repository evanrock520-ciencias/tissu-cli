import json
from pathlib import Path

from tissu_cli.types import FilesSuported, Type


def get_available_files(dir_path: str, recursive: bool = False) -> dict:
    dir = Path(dir_path)
    if recursive:
        files = [f for f in dir.rglob("*") if f.is_file() and (f.suffix in (".json", ".tissu"))]
    else:
        files = [f for f in dir.iterdir() if f.is_file() and f.suffix in (".json", ".tissu")]

    available = {Type.SCENE: [], Type.PHYSICS: [], Type.MATERIAL: [], Type.STATE: []}

    for file in files:
        tissu_type = classify_file(file)
        if tissu_type:
            available[tissu_type].append(file)

    return available


def classify_file(file_path: Path) -> Type | None:
    format = get_file_format(file_path.name)
    if format == FilesSuported.TISSU:
        return Type.STATE
    elif format == FilesSuported.JSON:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            match data["type"]:
                case "scene":
                    return Type.SCENE
                case "material":
                    return Type.MATERIAL
                case "physics":
                    return Type.PHYSICS

    return None


def get_name(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data["name"]


def get_file_format(path: str) -> FilesSuported:
    if path.endswith(".json"):
        return FilesSuported.JSON
    elif path.endswith(".tissu"):
        return FilesSuported.TISSU
    raise ValueError(f"File format not supported: {path.split('.')[-1]}")
