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

### `info`

Show information about a scene (`.json`) or state (`.tissu`) file.

```bash
tissu-cli info <path>
```

### `bake`

Bake a cloth simulation and export it to Alembic (`.abc`).

```bash
tissu-cli bake <scene_path> [OPTIONS]
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
tissu-cli view <scene_path> [--state, -s <path>]
```

### `snapshots`

Export OBJ mesh snapshots for each frame of a simulation.

```bash
tissu-cli snapshots <scene_path> <out_dir> <cloth> [OPTIONS]
```

| Option          | Default       | Description          |
|-----------------|---------------|----------------------|
| `--start`       | `1`           | Start frame          |
| `--end`         | `120`         | End frame            |
| `--state`, `-s` | —             | Load initial state   |

---

## Example

Sample scenes and assets are included under `data/`:

```bash
tissu-cli info data/scenes/curtain.json
tissu-cli bake data/scenes/curtain.json -o curtain.abc
tissu-cli snapshots data/scenes/curtain.json ./frames curtain
```