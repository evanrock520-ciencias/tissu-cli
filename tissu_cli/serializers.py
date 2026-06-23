from tissu import Simulation, _cloth_sdk_core as sdk


def scene_to_dict(path: str) -> dict:
    scene = Simulation.get_scene_status(path)
    fabrics = []
    for f in scene.fabrics:
        fabric = {"name": f.name, "type": f.type}
        if f.type == "grid":
            fabric["rows"] = f.rows
            fabric["cols"] = f.cols
            fabric["spacing"] = f.spacing
        elif f.type == "mesh":
            fabric["source"] = f.source
        fabric["material"] = f.material.split("/")[-1].split(".")[0]
        fabric["pin_mode"] = f.pin_mode
        fabrics.append(fabric)

    colliders = []
    for c in scene.colliders:
        colliders.append({"type": c.type, "summary": c.summary})

    return {
        "type": "scene",
        "name": scene.name,
        "version": scene.version,
        "physics_preset": scene.physics_preset.split("/")[-1].split(".")[0],
        "fabrics": fabrics,
        "colliders": colliders,
    }


def state_to_dict(path: str) -> dict:
    state = sdk.StateSerializer.get_state_info(path)
    return {
        "type": "state",
        "version": state.version,
        "frame": state.frame,
        "timestamp": state.timestamp,
        "particle_count": state.particle_count,
    }
