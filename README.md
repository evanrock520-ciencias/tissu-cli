# Tissu CLI

A command-line interface for [Tissu](https://github.com/evanrock520-ciencias/Tissu), letting you run cloth simulations directly from your terminal without writing Python scripts.

---

## Requirements

- Python ($\ge$ 3.8)
- [Tissu](https://github.com/evanrock520-ciencias/Tissu) ($\ge$ 1.0.0)

---

## Installation

First, install Tissu from source and all it's dependencies.

Then, install Tissu CLI:

```bash
git clone https://github.com/evanrock520-ciencias/Tissu-CLI.git
cd tissu-cli
pip install .
```

## Usage

```bash
tissu-cli [COMMAND] [OPTIONS]
```

## Commands

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