import typer
from rich.console import Console
from rich.text import Text
from rich.rule import Rule
from enum import Enum
from pathlib import Path
import json
from prompt_toolkit import prompt           # For Tissu Shell
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


@app.command()
def bake(
    scene_path: str,
    out_path: str = typer.Option("output.abc", "--out", "-o"),
    start: int = typer.Option(1, "--start"),
    end: int = typer.Option(120, "--end"),
    fps: float = typer.Option(24.0, "--fps"),
    state_path: str = typer.Option(None, "--state", "-s")
):
    sim = Simulation.load_scene(scene_path)
    
    if state_path != None:
        sim.load_state(state_path)
    
    sim.bake_alembic(
        filepath=out_path,
        start_frame=start,
        end_frame=end,
        fps=fps
    )

@app.command()
def view(scene_path: str, state_path: str = typer.Option(None, "--state", "-s")):
    sim = Simulation.load_scene(scene_path)
    
    if state_path != None:
        sim.load_state(state_path)
    
    sim.view()


@app.command()
def snapshots(
    scene_path: str, 
    out_dir: str, 
    cloth: str,
    start: int = typer.Option(1, "--start"),
    end: int = typer.Option(120, "--end"),
    state_path: str = typer.Option(None, "--state", "-s")
    ):
    sim = Simulation.load_scene(scene_path)
    
    if state_path != None:
        sim.load_state(state_path)
    
    @sim.on_range(start, end)
    def snapshot(sim: Simulation):
        sim.save_snapshot(filename=out_dir + "/" + cloth + str(sim.frame) + ".obj", fabric_name=cloth)
        
    sim.simulate(end - start)


@app.command()
def init(
    dir_path: str,
    substeps: int = typer.Option(10, "--substeps"),
    iterations: int = typer.Option(2, "--iterations"),
    gravity: str = typer.Option("0,-9.81,0", "--gravity"),
    thickness: float = typer.Option(0.05, "--thickness"),
    wind: str = typer.Option("0,0,0", "--wind"),
    air_density: float = typer.Option(0.1, "--air-density"),
):
    def parse_vec(s: str) -> list[float]:
        return [float(x) for x in s.split(",")]

    jsonHeader = {
        "version": 2.0,
        "type": "scene",
        "name": dir_path,
        "physics": {
            "substeps": substeps,
            "iterations": iterations,
            "gravity": parse_vec(gravity),
            "collision": {
                "thickness": thickness
            },
            "environment": {
                "wind": parse_vec(wind),
                "air_density": air_density
            }
        },
        "fabrics": [],
        "colliders": []
    }

    create_dir(dir_path)
    file_path = f"{dir_path}/{dir_path}.json"
    if not Path(file_path).exists():
        Path(file_path).touch()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(jsonHeader, file, indent=4, ensure_ascii=False)

    console.print(f"[cyan]Scene[/cyan] [bold]{dir_path}[/bold] initialized at [dim]{file_path}[/dim]")

@app.command()
def add_fabric(
    dir_path: str,
    name: str,
    rows: int = typer.Option(None, "--rows", "-r"),
    cols: int = typer.Option(None, "--cols", "-c"),
    spacing: float = typer.Option(0.05, "--spacing"),
    mesh_path: str = typer.Option(None, "--path", "-p"),
    density: float = typer.Option(0.1, "--density"),
    compliance_structural: float = typer.Option(1e-9, "--structural"),
    compliance_shear: float = typer.Option(1e-8, "--shear"),
    compliance_bending: float = typer.Option(0.1, "--bending"),
    pin_mode: str = typer.Option(None, "--pin-mode"),
    pin_compliance: float = typer.Option(1e-9, "--pin-compliance"),
    pin_threshold: float = typer.Option(0.01, "--pin-threshold"),
):
    file_path = f"{dir_path}/{dir_path}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        scene = json.load(f)

    if rows is not None and cols is not None:
        fabric = {
            "name": name,
            "type": "grid",
            "rows": rows,
            "cols": cols,
            "spacing": spacing,
        }
    elif mesh_path is not None:
        fabric = {
            "name": name,
            "type": "mesh",
            "path": mesh_path,
        }
    else:
        console.print("[red]Error:[/red] Provide --rows and --cols, or --path.")
        raise typer.Exit(1)

    fabric["material"] = {
        "density": density,
        "compliance": {
            "structural": compliance_structural,
            "shear": compliance_shear,
            "bending": compliance_bending,
        }
    }

    if pin_mode is not None:
        if pin_mode not in ("top_corners", "by_height"):
            console.print("[red]Error:[/red] --pin-mode must be 'top_corners' or 'by_height'.")
            raise typer.Exit(1)
        fabric["pins"] = {
            "mode": pin_mode,
            "compliance": pin_compliance,
            "threshold": pin_threshold,
        }

    if not isinstance(scene.get("fabrics"), list):
        scene["fabrics"] = []
    scene["fabrics"].append(fabric)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)
    console.print(f"[cyan]Fabric[/cyan] [bold]{name}[/bold] added to [dim]{file_path}[/dim]")

@app.command()
def add_collider(
    dir_path: str,
    plane: bool = typer.Option(False, "--plane"),
    origin: str = typer.Option("0,0,0", "--origin"),
    normal: str = typer.Option("0,1,0", "--normal"),
    sphere: bool = typer.Option(False, "--sphere"),
    center: str = typer.Option("0,0,0", "--center"),
    capsule: bool = typer.Option(False, "--capsule"),
    start: str = typer.Option("0,0,0", "--start"),
    end: str = typer.Option("0,1,0", "--end"),
    radius: float = typer.Option(0.5, "--radius"),
    friction: float = typer.Option(0.5, "--friction"),
    mesh: bool = typer.Option(False, "--mesh"),
    mesh_path: str = typer.Option(None, "--mesh-path")
):
    file_path = f"{dir_path}/{dir_path}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        scene = json.load(f)

    def parse_vec(s: str) -> list[float]:
        return [float(x) for x in s.split(",")]

    if plane:
        collider = {
            "type": "plane",
            "origin": parse_vec(origin),
            "normal": parse_vec(normal),
        }
    elif sphere:
        collider = {
            "type": "sphere",
            "center": parse_vec(center),
            "radius": radius,
        }
    elif capsule:
        collider = {
            "type": "capsule",
            "start": parse_vec(start),
            "end": parse_vec(end),
            "radius": radius,
        }
    elif mesh:
        collider = {
            "type": "mesh",
            "path": mesh_path
        }
    else:
        console.print("[red]Error:[/red] Provide --plane, --sphere, or --capsule.")
        raise typer.Exit(1)

    collider["friction"] = friction

    if not isinstance(scene.get("colliders"), list):
        scene["colliders"] = []
    scene["colliders"].append(collider)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)

    console.print(f"[cyan]Collider[/cyan] [bold]{collider['type']}[/bold] added to [dim]{file_path}[/dim]")


@app.command()
def plot(scene_path: str, frame: int, fabric: str = typer.Option(None, "--fabric")):
    sim = Simulation.load_scene(scene_path)
    sim.simulate(frame)
    sim.plot(fabric)


@app.command()
def plot_gif(
    scene_path: str, 
    out_path: str,
    fabric: str = typer.Option(None, "--fabric"), 
    start: int = typer.Option(1, "--start", "-s"), 
    end: int = typer.Option(120, "--end", "-e"), 
    fps: float = typer.Option(30.0, "--fps"), 
    ):
    out_path = scene_path.split("/")[0] + "/exports/preview/" + out_path
    sim = Simulation.load_scene(scene_path)
    sim.plot_gif(fabric, start, end, fps, out_path)

@app.command()
def save_state(
    scene_path: str,
    out_path: str,
    frame: int
):
    sim = Simulation.load_scene(scene_path)
    sim.simulate(frame)
    sim.save_state(out_path)

def create_dir(name: str):
    if not Path(name).exists():
        Path(name).mkdir()
    
    if not Path(f"{name}/exports").exists():
        Path(f"{name}/exports").mkdir()
        
    if not Path(f"{name}/exports/preview").exists():
        Path(f"{name}/exports/preview").mkdir()
        
    if not Path(f"{name}/exports/animations").exists():
        Path(f"{name}/exports/animations").mkdir()
        
    if not Path(f"{name}/states").exists():
        Path(f"{name}/states").mkdir()
        
    if not Path(f"{name}/assets").exists():
        Path(f"{name}/assets").mkdir()

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
