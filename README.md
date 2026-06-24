[![CI](https://github.com/evanrock520-ciencias/tissu-cli/actions/workflows/ci.yaml/badge.svg)](https://github.com/evanrock520-ciencias/tissu-cli/actions/workflows/ci.yaml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![CLI](https://img.shields.io/badge/CLI-Reference-blue)

# Tissu CLI

A command-line interface for [Tissu](https://github.com/evanrock520-ciencias/Tissu), letting you run cloth simulations directly from your terminal without writing Python scripts.

---

## Requirements

- Python >= 3.8
- [Tissu](https://github.com/evanrock520-ciencias/Tissu) >= 1.0.0

---

## Installation

```bash
pip install tissu-cli
```

Or from source:

```bash
git clone https://github.com/evanrock520-ciencias/tissu-cli.git
cd tissu-cli
pip install .
```

Enable shell completion (optional):

```bash
tissu-cli --install-completion
```

---

## Usage

```bash
tissu-cli [COMMAND] [OPTIONS]
```

### `init`

Initialize a new scene directory with a blank scene file.

```bash
tissu-cli init <dir> [OPTIONS]
```

| Option          | Default       | Description               |
|-----------------|---------------|---------------------------|
| `--substeps`    | `10`          | Solver substeps           |
| `--iterations`  | `2`           | Solver iterations         |
| `--gravity`     | `0,-9.81,0`   | Gravity vector (x,y,z)    |
| `--thickness`   | `0.05`        | Collision thickness       |
| `--wind`        | `0,0,0`       | Wind vector (x,y,z)       |
| `--air-density` | `0.1`         | Air density               |

### `add-fabric`

Add a fabric to a scene directory.

```bash
tissu-cli add-fabric <dir> <name> [OPTIONS]
```

| Option                | Default  | Description                            |
|-----------------------|----------|----------------------------------------|
| `--rows`, `-r`        | —        | Grid rows (required for grid)          |
| `--cols`, `-c`        | —        | Grid cols (required for grid)          |
| `--spacing`           | `0.05`   | Distance between particles             |
| `--path`, `-p`        | —        | Path to OBJ mesh (alternative to grid) |
| `--density`           | `0.1`    | Material density                       |
| `--structural`        | `1e-9`   | Structural compliance                  |
| `--shear`             | `1e-8`   | Shear compliance                       |
| `--bending`           | `0.1`    | Bending compliance                     |
| `--pin-mode`          | —        | Pin mode: `top_corners`, `by_height`   |
| `--pin-compliance`    | `1e-9`   | Pin compliance                         |
| `--pin-threshold`     | `0.01`   | Pin threshold                          |

### `add-collider`

Add a collider to a scene directory.

```bash
tissu-cli add-collider <dir> [OPTIONS]
```

| Option       | Default       | Description                         |
|--------------|---------------|-------------------------------------|
| `--plane`    | —             | Add a plane collider                |
| `--origin`   | `0,0,0`       | Plane origin (x,y,z)                |
| `--normal`   | `0,1,0`       | Plane normal (x,y,z)                |
| `--sphere`   | —             | Add a sphere collider               |
| `--center`   | `0,0,0`       | Sphere center (x,y,z)               |
| `--capsule`  | —             | Add a capsule collider              |
| `--start`    | `0,0,0`       | Capsule start (x,y,z)               |
| `--end`      | `0,1,0`       | Capsule end (x,y,z)                 |
| `--radius`   | `0.5`         | Sphere/capsule radius               |
| `--friction` | `0.5`         | Friction coefficient                |
| `--mesh`     | —             | Add a mesh collider                 |
| `--mesh-path`| —             | Path to OBJ mesh (required for mesh)|

One of `--plane`, `--sphere`, `--capsule`, or `--mesh` is required.

### `add-pin`

Add pins to a fabric in a scene directory.

```bash
tissu-cli add-pin <dir> <fabric> <mode> [OPTIONS]
```

| Option           | Default | Description                       |
|------------------|---------|-----------------------------------|
| `--compliance`   | `0.1`   | Pin constraint compliance         |
| `--threshold`    | `0.01`  | Pin constraint threshold          |

`mode` must be `top_corners` or `by_height`.

### `info`

Show information about a scene (`.json`) or state (`.tissu`) file.

```bash
tissu-cli info <dir>
```

### `bake`

Bake a cloth simulation and export it to Alembic (`.abc`).

```bash
tissu-cli bake <dir> [OPTIONS]
```

| Option          | Default       | Description          |
|-----------------|---------------|----------------------|
| `--out`, `-o`   | `output.abc`  | Output Alembic path  |
| `--start`       | `1`           | Start frame          |
| `--end`         | `120`         | End frame            |
| `--fps`         | `24.0`        | Frames per second    |
| `--state`, `-s` | —             | Load initial state   |

### `view`

View a cloth simulation in a 3D viewer.

```bash
tissu-cli view <dir> [--state, -s <path>]
```

### `snapshots`

Export OBJ mesh snapshots for each frame of a simulation.

```bash
tissu-cli snapshots <dir> <out_dir> <cloth> [OPTIONS]
```

| Option          | Default       | Description          |
|-----------------|---------------|----------------------|
| `--start`       | `1`           | Start frame          |
| `--end`         | `120`         | End frame            |
| `--state`, `-s` | —             | Load initial state   |

### `list-files`

List available files (scenes, materials, physics, states) in a directory.

```bash
tissu-cli list-files <dir> [OPTIONS]
```

| Option                | Description                        |
|-----------------------|------------------------------------|
| `-m`, `--materials`   | Show materials                     |
| `-p`, `--physics`     | Show physics                       |
| `-s`, `--scenes`      | Show scenes                        |
| `-e`, `--states`      | Show states                        |
| `-r`, `--recursive`   | Search recursively                 |

### `plot`

Visualize a simulation frame in a 3D matplotlib plot.

```bash
tissu-cli plot <dir> <frame> [OPTIONS]
```

| Option     | Default | Description          |
|------------|---------|----------------------|
| `--fabric` | —       | Fabric name to plot  |

### `plot-gif`

Generate an animated GIF preview of a simulation.

```bash
tissu-cli plot-gif <dir> <out_path> [OPTIONS]
```

| Option          | Default | Description            |
|-----------------|---------|------------------------|
| `--fabric`      | —       | Fabric name to render  |
| `--start`, `-s` | `1`     | Start frame            |
| `--end`, `-e`   | `120`   | End frame              |
| `--fps`         | `30.0`  | Frames per second      |

Output is written to `<dir>/exports/preview/<out_path>`.

### `plot-energy`

Simulate and plot energy over time.

```bash
tissu-cli plot-energy <dir> <frame>
```

### `physics`

Load a physics config file into a scene.

```bash
tissu-cli physics <dir> <physics_path>
```

### `save-state`

Run a simulation and save the solver state to a `.tissu` file.

```bash
tissu-cli save-state <dir> <out_path> <frame>
```

| Argument   | Description                    |
|------------|--------------------------------|
| `dir`      | Scene directory                |
| `out_path` | Output `.tissu` file path      |
| `frame`    | Frame number to simulate to    |

### `save-physics`

Extract and save the physics config from a scene.

```bash
tissu-cli save-physics <dir> <out_path> [OPTIONS]
```

| Option   | Default    | Description           |
|----------|------------|-----------------------|
| `--name` | `physics`  | Physics config name   |

---

## Example

Sample scenes and assets are included under `data/`:

```bash
tissu-cli info data/scenes/curtain
tissu-cli bake data/scenes/curtain -o curtain.abc
tissu-cli snapshots data/scenes/curtain ./frames curtain
```