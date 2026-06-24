from pathlib import Path
import json

from rich.console import Console
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from tissu import Simulation, _cloth_sdk_core as sdk

from tissu_cli.files import get_name
from tissu_cli.types import Type

console = Console()


def show_table(header: str, content: list, file_type: Type):
    table = Table(
        title=header,
        title_justify="left",
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Name", style="bold")
    table.add_column("Path")

    for file in content:
        name = get_name(file.resolve()) if file.suffix == ".json" else file.stem
        path = str(file.relative_to(file.anchor) if file.is_absolute() else file)
        table.add_row(name, path)

    console.print(table)


def row(key: str, value: str, key_width: int = 10, value_style: str = "white"):
    t = Text()
    t.append(key.ljust(key_width), style="cyan")
    t.append(" ── ", style="dim")
    t.append(value, style=value_style)
    console.print(t)


def section(title: str, count: int):
    t = Text()
    t.append(title, style="dim")
    t.append(f"  {count}", style="cyan bold")
    console.print()
    console.print(t)
    console.print(Rule(style="dim"))


def tag(label: str, style: str = "bold cyan on grey11") -> Text:
    t = Text()
    t.append(f" {label} ", style=style)
    return t


def scene_status(path: str):
    header = Text()
    header.append("Scene info", style="bold white")
    console.print()
    console.print(header)
    console.print(Rule(style="bright_black"))

    scene = Simulation.get_scene_status(path)
    fabrics = scene.fabrics
    colliders = scene.colliders

    row("name",    scene.name)
    row("version", str(scene.version))
    row("physics", scene.physics_preset.split("/")[-1].split(".")[0])

    section("fabrics", len(fabrics))
    for fabric in fabrics:
        t = Text()
        t.append(f"  {fabric.name}", style="cyan bold")
        t.append("  ")
        t.append_text(tag(fabric.type, "bold yellow on grey11"))
        console.print(t)

        if fabric.type == "grid":
            details = Text("  ")
            details.append(f"{fabric.cols}×{fabric.rows}", style="white")
            details.append("  ·  ", style="dim")
            details.append("spacing ", style="dim")
            details.append(f"{fabric.spacing:.2f}", style="yellow")
            details.append("  ·  ", style="dim")
            details.append("material ", style="dim")
            details.append(fabric.material.split("/")[-1].split(".")[0], style="cyan")
            console.print(details)
        elif fabric.type == "mesh":
            details = Text("  ")
            details.append("source ", style="dim")
            details.append(fabric.source, style="cyan")
            console.print(details)

        pins = Text("  ")
        pins.append("pins ", style="dim")
        pins.append("── ", style="dim")
        pins.append(fabric.pin_mode, style="cyan")
        console.print(pins)

    section("colliders", len(colliders))
    for collider in colliders:
        t = Text()
        name = collider.name if collider.name else collider.type
        t.append(f"  {name}", style="cyan bold")
        t.append("  ")
        t.append_text(tag(collider.type, "bold yellow on grey11"))
        console.print(t)

        summary = Text("  ")
        summary.append(collider.summary, style="dim white")
        console.print(summary)

    console.print()


def state_status(path: str):
    header = Text()
    header.append("state info", style="bold white")
    console.print()
    console.print(header)
    console.print(Rule(style="bright_black"))

    state = sdk.StateSerializer.get_state_info(path)

    row("version",   str(state.version))
    row("frame",     str(state.frame),         value_style="yellow")
    row("time",      f"{state.timestamp:.3f}s", value_style="yellow")
    row("particles", f"{state.particle_count:,}", value_style="yellow")

    console.print()


def material_status(path: str):
    with open(path) as f:
        data = json.load(f)

    header = Text()
    header.append("Material info", style="bold white")
    console.print()
    console.print(header)
    console.print(Rule(style="bright_black"))

    row("name",    data.get("name", "?"))
    row("density", str(data.get("density", "?")))

    console.print()
    t = Text()
    t.append("compliance", style="dim")
    console.print(t)
    console.print(Rule(style="dim"))

    comp = data.get("compliance", {})
    row("  structural", str(comp.get("structural", "?")), key_width=14)
    row("  shear",      str(comp.get("shear", "?")), key_width=14)
    row("  bending",    str(comp.get("bending", "?")), key_width=14)

    console.print()


def physics_status(path: str):
    with open(path) as f:
        data = json.load(f)

    header = Text()
    header.append("Physics info", style="bold white")
    console.print()
    console.print(header)
    console.print(Rule(style="bright_black"))

    row("name",       data.get("name", "?"))
    row("substeps",   str(data.get("substeps", "?")))
    row("iterations", str(data.get("iterations", "?")))
    row("gravity",    str(data.get("gravity", "?")))

    console.print()
    t = Text()
    t.append("collision", style="dim")
    console.print(t)
    console.print(Rule(style="dim"))

    col = data.get("collision", {})
    row("  thickness", str(col.get("thickness", "?")), key_width=14)

    console.print()
    t = Text()
    t.append("environment", style="dim")
    console.print(t)
    console.print(Rule(style="dim"))

    env = data.get("environment", {})
    row("  wind",        str(env.get("wind", "?")), key_width=14)
    row("  air_density", str(env.get("air_density", "?")), key_width=14)

    console.print()
