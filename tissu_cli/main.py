import typer
from rich.console import Console
from rich.text import Text
from rich.rule import Rule
from enum import Enum
from tissu import _cloth_sdk_core as sdk
from tissu import Simulation

app = typer.Typer()
console = Console()


class FilesSuported(Enum):
    JSON = ".json",
    TISSU = ".tissu",


@app.command()
def info(path: str):
    format = get_file_format(path)
    match format:
        case FilesSuported.JSON:
            scene_status(path)
        case FilesSuported.TISSU:
            state_status(path)


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
        t.append(f"  {collider.type}", style="cyan bold")
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


def get_file_format(path: str) -> FilesSuported:
    if path.endswith(".json"):
        return FilesSuported.JSON
    elif path.endswith(".tissu"):
        return FilesSuported.TISSU
    raise ValueError(f"File format not supported: {path.split('.')[-1]}")


if __name__ == "__main__":
    app()