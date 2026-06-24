import json
from pathlib import Path

import typer
from rich.console import Console
from tissu import Material, Simulation, _cloth_sdk_core as sdk

from tissu_cli.display import console, material_status, physics_status, scene_status, show_table, state_status
from tissu_cli.files import get_available_files, get_file_format, get_name
from tissu_cli.serializers import scene_to_dict, state_to_dict
from tissu_cli.types import CLIState, FilesSuported, Type

app = typer.Typer()
err_console = Console(stderr=True)


@app.callback()
def main(
    ctx: typer.Context,
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
):
    ctx.obj = CLIState(json_output=json, quiet=quiet)


@app.command()
def info(ctx: typer.Context, dir_path: str):
    file_path = f"{dir_path}/{dir_path}.json"
    try:
        format = get_file_format(file_path)
        st = ctx.obj

        if st.json_output:
            match format:
                case FilesSuported.JSON:
                    console.print(json.dumps(scene_to_dict(file_path), indent=2))
                case FilesSuported.TISSU:
                    console.print(json.dumps(state_to_dict(file_path), indent=2))
        else:
            match format:
                case FilesSuported.JSON:
                    scene_status(file_path)
                case FilesSuported.TISSU:
                    state_status(file_path)
    except FileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] File not found: {e.filename or file_path}")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        err_console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)
    except (ValueError, RuntimeError) as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def bake(
    dir_path: str,
    out_path: str = typer.Option("output.abc", "--out", "-o"),
    start: int = typer.Option(1, "--start"),
    end: int = typer.Option(120, "--end"),
    fps: float = typer.Option(24.0, "--fps"),
    state_path: str = typer.Option(None, "--state", "-s")
):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")

    if state_path != None:
        sim.load_state(state_path)

    sim.bake_alembic(
        filepath=out_path,
        start_frame=start,
        end_frame=end,
        fps=fps
    )


@app.command()
def view(dir_path: str, state_path: str = typer.Option(None, "--state", "-s")):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")

    if state_path != None:
        sim.load_state(state_path)

    sim.view()


@app.command()
def snapshots(
    dir_path: str,
    out_dir: str,
    cloth: str,
    start: int = typer.Option(1, "--start"),
    end: int = typer.Option(120, "--end"),
    state_path: str = typer.Option(None, "--state", "-s")
    ):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")

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

    existing = next((i for i, f in enumerate(scene["fabrics"]) if f.get("name") == name), None)
    if existing is not None:
        scene["fabrics"][existing] = fabric
        console.print(f"[cyan]Fabric[/cyan] [bold]{name}[/bold] updated in [dim]{file_path}[/dim]")
    else:
        scene["fabrics"].append(fabric)
        console.print(f"[cyan]Fabric[/cyan] [bold]{name}[/bold] added to [dim]{file_path}[/dim]")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)


@app.command()
def remove_fabric(
    dir_path: str,
    fabric: str
):
    file_path =  f"{dir_path}/{dir_path}.json"
    with open(file_path, 'r', encoding="utf-8") as f:
        scene = json.load(f)

    fabrics = scene.get("fabrics")
    if not fabrics:
        console.print("[red]Error:[/red] No fabrics found in scene.")
        raise typer.Exit(1)
    
    target = next((i for i, f in enumerate(fabrics) if f.get("name") == fabric), None)
    if target is None:
        console.print(f"[yellow]Fabric [bold]{fabric}[/bold] is not part of the scene.[/yellow]")
        raise typer.Exit(0)

    del fabrics[target]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)
    console.print(f"[bold]{fabric}[/bold] removed")


@app.command()
def remove_collider(
    dir_path: str,
    collider: str 
):
    file_path =  f"{dir_path}/{dir_path}.json"
    with open(file_path, 'r', encoding="utf-8") as f:
        scene = json.load(f)

    colliders = scene.get("colliders")
    if not colliders:
        console.print("[red]Error:[/red] No colliders found in scene.")
        raise typer.Exit(1)
    
    target = next((i for i, c in enumerate(colliders) if c.get("name") == collider), None)
    if target is None:
        console.print(f"[yellow]Collider [bold]{collider}[/bold] is not part of the scene.[/yellow]")
        raise typer.Exit(0)

    del colliders[target]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)
    console.print(f"[bold]{collider}[/bold] removed")



@app.command()
def pin(
    dir_path: str,
    fabric: str,
    mode: str,
    compliance: float = typer.Option(1e-9, "--compliance"),
    threshold: float = typer.Option(0.01, "--threshold")
):
    file_path = f"{dir_path}/{dir_path}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        scene = json.load(f)

    fabrics = scene.get("fabrics")
    if not fabrics:
        console.print("[red]Error:[/red] No fabrics found in scene.")
        raise typer.Exit(1)

    target = next((f for f in fabrics if f.get("name") == fabric), None)
    if target is None:
        console.print(f"[red]Error:[/red] Fabric [bold]{fabric}[/bold] not found.")
        raise typer.Exit(1)

    target["pins"] = {
        "mode": mode,
        "compliance": compliance,
        "threshold": threshold
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)
    console.print(f"[cyan]Pins[/cyan] added to fabric [bold]{fabric}[/bold] in [dim]{file_path}[/dim]")


@app.command()
def unpin(
    dir_path: str,
    fabric: str
):
    file_path = f"{dir_path}/{dir_path}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        scene = json.load(f)

    fabrics = scene.get("fabrics")
    if not fabrics:
        console.print("[red]Error:[/red] No fabrics found in scene.")
        raise typer.Exit(1)

    target = next((f for f in fabrics if f.get("name") == fabric), None)
    if target is None:
        console.print(f"[red]Error:[/red] Fabric [bold]{fabric}[/bold] not found.")
        raise typer.Exit(1)
    
    if "pins" not in target:
        console.print(f"[yellow]Fabric [bold]{fabric}[/bold] has no pins to remove.[/yellow]")
        raise typer.Exit(0)

    del target["pins"]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)
    console.print(f"[bold]{fabric}[/bold] unpinned")



@app.command()
def add_collider(
    dir_path: str,
    name: str = typer.Option("", "--name", "-n"),
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
        console.print("[red]Error:[/red] Provide --plane, --sphere, --capsule, or --mesh")
        raise typer.Exit(1)

    collider["friction"] = friction
    collider["name"] = name

    if not isinstance(scene.get("colliders"), list):
        scene["colliders"] = []
    scene["colliders"].append(collider)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, indent=4, ensure_ascii=False)

    console.print(f"[cyan]Collider[/cyan] [bold]{collider['type']}[/bold] added to [dim]{file_path}[/dim]")


@app.command()
def plot(dir_path: str, frame: int, fabric: str = typer.Option(None, "--fabric")):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")
    sim.simulate(frame)
    sim.plot(fabric)


@app.command()
def plot_gif(
    dir_path: str,
    out_path: str,
    fabric: str = typer.Option(None, "--fabric"),
    start: int = typer.Option(1, "--start", "-s"),
    end: int = typer.Option(120, "--end", "-e"),
    fps: float = typer.Option(30.0, "--fps"),
    ):
    out_path = f"{dir_path}/exports/preview/{out_path}"
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")
    sim.plot_gif(fabric, start, end, fps, out_path)


@app.command()
def plot_energy(
    dir_path: str,
    frame: int
):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")
    sim.start_recording()
    sim.simulate(frame)
    sim.stop_recording()
    sim.plot_energy()


@app.command()
def list_files(
    ctx: typer.Context,
    dir_path: str,
    materials: bool = typer.Option(False, "-m", "--materials", help="Show materials"),
    physics: bool = typer.Option(False, "-p", "--physics", help="Show physics"),
    scenes: bool = typer.Option(False, "-s", "--scenes", help="Show scenes"),
    states: bool = typer.Option(False, "-e", "--states", help="Show states"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Search recursively"),
):
    try:
        selected = [t for t, v in [
            (Type.SCENE, scenes), (Type.PHYSICS, physics),
            (Type.MATERIAL, materials), (Type.STATE, states)
        ] if v] or [*Type]

        files = get_available_files(dir_path, recursive)
        st = ctx.obj

        if st.json_output:
            result = {}
            for t in selected:
                entries = []
                for f in files[t]:
                    name = get_name(f.resolve()) if f.suffix == ".json" else f.stem
                    path = str(f.relative_to(f.anchor) if f.is_absolute() else f)
                    entries.append({"name": name, "path": path})
                result[t.value] = entries
            console.print(json.dumps(result, indent=2))
        else:
            for t in selected:
                if files[t]:
                    show_table(t.value.replace(t.value[0], t.value[0].upper(), 1), files[t], t)
    except FileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] Directory not found: {e.filename or dir_path}")
        raise typer.Exit(1)
    except Exception as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def physics(
    dir_path: str,
    physics_path: str
):
    file_path = f"{dir_path}/{dir_path}.json"
    sim = Simulation.load_scene(file_path)
    sim.load_physics(physics_path)
    sim.save_scene(file_path)


@app.command()
def save_state(
    dir_path: str,
    out_path: str,
    frame: int
):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")
    sim.simulate(frame)
    sim.save_state(out_path)


@app.command()
def save_physics(
    dir_path: str,
    out_path: str,
    name: str = typer.Option("physics", "--name")
):
    sim = Simulation.load_scene(f"{dir_path}/{dir_path}.json")
    sim.save_physics(out_path, name)


@app.command()
def create_material(
    material_path: str,
    name: str,
    density: float = typer.Option(0.1, "--density"),
    structural: float = typer.Option(1e-9, "--structural"),
    shear: float = typer.Option(1e-8, "--shear"),
    bending: float = typer.Option(0.01, "--bending")
):
    Path(material_path).parent.mkdir(parents=True, exist_ok=True)
    material = Material(density, structural, shear, bending)
    sdk.ConfigLoader.save_material(material_path, material._native, name)
    console.print(f"[cyan]Material[/cyan] [bold]{name}[/bold] saved to [dim]{material_path}[/dim]")


@app.command()
def extract_material(
    dir_path: str,
    fabric: str,
    out_path: str
):
    file_path = f"{dir_path}/{dir_path}.json"
    sim = Simulation.load_scene(file_path)
    sim.save_material(out_path, fabric)

@app.command()
def apply_material(
    dir_path: str,
    fabric: str,
    path: str = typer.Option(None, "-p", "--path"),
    density: float = typer.Option(None, "-d", "--density"),
    structural: float = typer.Option(None, "--structural"),
    shear: float = typer.Option(None, "--shear"),
    bending: float = typer.Option(None, "--bending"),
):
    file_path = f"{dir_path}/{dir_path}.json"
    sim = Simulation.load_scene(file_path)

    if path is not None:
        sim.load_material(path, fabric)

    overrides = {k: v for k, v in [
        ("density", density),
        ("structural", structural),
        ("shear", shear),
        ("bending", bending),
    ] if v is not None}

    if overrides:
        fab = sim.get_fabric(fabric)
        fab.update_material(**overrides)

    if path is None and not overrides:
        err_console.print("[red]Error:[/red] Provide --path or at least one property flag (--density, --structural, --shear, --bending).")
        raise typer.Exit(1)

    sim.save_scene(file_path)


@app.command()
def inspect_material(ctx: typer.Context, material_path: str):
    try:
        file_path = Path(material_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Material file not found: {material_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "material":
            raise ValueError(f"File is not a material: {material_path}")

        st = ctx.obj
        if st.json_output:
            console.print(json.dumps(data, indent=2))
        else:
            material_status(str(file_path))
    except FileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] File not found: {e.filename or material_path}")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        err_console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)
    except (ValueError, RuntimeError) as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def inspect_physics(ctx: typer.Context, physics_path: str):
    try:
        file_path = Path(physics_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Physics file not found: {physics_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "physics":
            raise ValueError(f"File is not a physics preset: {physics_path}")

        st = ctx.obj
        if st.json_output:
            console.print(json.dumps(data, indent=2))
        else:
            physics_status(str(file_path))
    except FileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] File not found: {e.filename or physics_path}")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        err_console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)
    except (ValueError, RuntimeError) as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def create_dir(name: str):
    if not Path(name).exists():
        Path(name).mkdir()

    if not Path(f"{name}/exports").exists():
        Path(f"{name}/exports").mkdir()

    if not Path(f"{name}/exports/preview").exists():
        Path(f"{name}/exports/preview").mkdir()

    if not Path(f"{name}/exports/animations").exists():
        Path(f"{name}/exports/animations").mkdir()

    if not Path(f"{name}/exports/materials").exists():
        Path(f"{name}/exports/materials").mkdir()

    if not Path(f"{name}/states").exists():
        Path(f"{name}/states").mkdir()

    if not Path(f"{name}/assets").exists():
        Path(f"{name}/assets").mkdir()

if __name__ == "__main__":
    app()
