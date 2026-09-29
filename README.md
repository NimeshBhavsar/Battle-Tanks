# Tank Battle

A real-time, turn-based, network-multiplayer artillery game (in the spirit of *Scorched
Earth* / *Worms*) written in Python with [Pygame](https://www.pygame.org/). Two players
connect over TCP sockets, aim across procedurally generated, destructible terrain, and
trade shells until one tank is left standing.

The project is built as an authoritative-server / thin-client system: `server.py` owns
the entire simulation (physics, collisions, damage, turn order) and runs headless;
`client.py` only renders whatever the server broadcasts and sends the local player's
input. This mirrors how real multiplayer games are structured, and is the reason the
project is split across dedicated `engine/`, `models/`, `ui/`, and networking modules
rather than one script.

See [ProjectArchitecture.md](ProjectArchitecture.md) for the original design document
and the phase-by-phase build plan this project followed.

## Features

- Turn-based movement, aiming (angle/power), and firing, with a live trajectory preview
- Projectile physics where shell weight (Light/Medium/Heavy) changes arc, drop speed,
  and even the shell's on-screen (and hit-detection) size
- Distance-based explosion damage and terrain deformation (craters), each carved into a
  per-column height map
- A real client/server network architecture (length-prefixed JSON over TCP), not just a
  shared-process hot-seat mode
- Fuel cans that spawn at random spots on the map - drive over one to refill your tank
- Labelled HP/fuel bars, animated explosions, synthesized sound effects (no external audio
  assets needed), and a menu for renaming yourself and restarting a finished match

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- An audio-capable environment is optional - sound effects fail silently if no audio
  device is available

## Installation

```sh
git clone https://github.com/NimeshBhavsar/Battle-Tanks.git
cd "Intro to Python"
uv pip install -e .
```

This installs the `tankbattle` package (declared via `pyproject.toml`'s
`[build-system]`, using `uv_build`) in editable mode, along with its one runtime
dependency, `pygame`.

## Running

The game needs three processes: one server and two clients (each client opens its own
window). Run each in a separate terminal:

```sh
uv run -m tankbattle server
uv run -m tankbattle client   # player 1
uv run -m tankbattle client   # player 2
```

(A console-script shortcut is also installed, so `uv run tankbattle server` /
`uv run tankbattle client` work identically.)

By default the server listens on `127.0.0.1:5555`. Both subcommands accept `--host` and
`--port` if you want to play across a LAN instead of on one machine:

```sh
uv run -m tankbattle server --host 0.0.0.0 --port 5555
uv run -m tankbattle client --host <server-ip> --port 5555
```

## Using the package from Python

The main building blocks are exported from the top-level package:

```python
from tankbattle import Tank, Terrain, HeavyShell, GameServer, GameClient

terrain = Terrain(seed=1)
tank = Tank(player_id=1, x=200, y=terrain.height_at(200), color=(200, 60, 60))
tank.current_ammo = HeavyShell()
shell = tank.fire()
```

## Controls

Apply on your turn:

| Key(s) | Action |
| --- | --- |
| `Left`/`A`, `Right`/`D` | Move (spends the turn on release) |
| `Up`/`W`, `Down`/`S` | Rotate the barrel |
| `E` / `Q` | Increase / decrease firing power |
| `1` / `2` / `3` | Select Light / Medium / Heavy shell |
| `Space` | Fire (spends the turn) |
| `Esc` | Open/close the menu |

In the menu: `N` edits your name, `R` restarts once a match has ended, `Esc` closes it.

## Project structure

```text
src/tankbattle/
    __main__.py         entry point for `python -m tankbattle`
    main.py              CLI (argparse) - dispatches to server or client
    server.py            authoritative GameServer: owns all game state, runs headless
    client.py             GameClient: renders server state, sends local input
    network.py            length-prefixed JSON message framing over TCP
    settings.py            session config (starting stats, default host/port)

    models/                game objects
        tank.py, projectile.py, terrain.py, ammunition.py, player.py

    engine/                 rules, with no rendering/networking knowledge
        physics.py, collision.py, damage.py, turn_manager.py, terrain_engine.py

    ui/                     pygame rendering only
        game_screen.py, hud.py, menu.py, sound.py

    utils/
        constants.py, helpers.py

assets/                    art/audio folders (currently empty placeholders -
                            sound effects are synthesized in code instead)
```

## Course concepts

Where each topic actually shows up in this codebase:

- **Primitives, control flow, containers** - everywhere, but concentrated in
  [server.py](src/tankbattle/server.py) (`_tick`/`_apply_input`: if/elif chains, early
  returns), [terrain.py](src/tankbattle/models/terrain.py) (`destroy_circle`'s
  per-column loop over a `list` height map). Containers: `dict` for
  [server.py](src/tankbattle/server.py)'s `pending_inputs`/`client_sockets`,
  [client.py](src/tankbattle/client.py)'s `tanks_by_id`,
  [ammunition.py](src/tankbattle/models/ammunition.py)'s `AMMO_BY_NAME`; `tuple` for
  positions/velocities throughout; a list comprehension at
  `_advance_projectile` in [server.py](src/tankbattle/server.py)
  (`opponents = [p.tank for p in self.players if ...]`).

- **Functions** - small, pure, single-purpose functions are the backbone of `engine/`:
  [physics.py](src/tankbattle/engine/physics.py) (`launch_velocity`, `step`),
  [damage.py](src/tankbattle/engine/damage.py) (`calculate_damage`),
  [helpers.py](src/tankbattle/utils/helpers.py) (`clamp`, `distance`,
  `distance_to_segment`).

- **Classes** - one per file under `models/`, plus `TurnManager`, `GameServer`,
  `GameClient`. [tank.py](src/tankbattle/models/tank.py) is the clearest example of
  state + behavior encapsulated together; `@property` is used for computed attributes
  in [tank.py](src/tankbattle/models/tank.py) (`alive`) and
  [projectile.py](src/tankbattle/models/projectile.py) (`radius`, derived from
  ammo weight).

- **Inheritance & polymorphism** -
  [ammunition.py](src/tankbattle/models/ammunition.py): `Ammo` is the base class,
  `LightShell`/`MediumShell`/`HeavyShell` inherit from it and only override the
  constructor's values. The polymorphism is in how they're *used*: `Tank.fire()`
  ([tank.py](src/tankbattle/models/tank.py)) and `Projectile`
  ([projectile.py](src/tankbattle/models/projectile.py)) never check
  which subclass they hold - they just read `.weight`/`.damage`/`.blast_radius`/`.name`
  on whatever `Ammo` instance they were given.

- **Packaging** - [pyproject.toml](pyproject.toml) (`[build-system]`, `uv_build`,
  console-script entry point), the `src/` layout, and
  [`__main__.py`](src/tankbattle/__main__.py) for `python -m tankbattle`.

- **Version control** - the commit history shows incremental, meaningful progress
  (`v5.0` terrain deformation through `v8` ammo-scaled ball size / menu / restart).

- **Not used**: numpy, pandas, and matplotlib are not used - a real-time game
  doesn't naturally need array math, tabular data, or static plots, so there was no
  organic place for them.

## Development notes

Code style is checked with [ruff](https://astral.sh/ruff) (configured in
`pyproject.toml`):

```sh
uvx ruff check src
uvx ruff format --check src
```

The server and client can each be exercised without a display: `server.py` never calls
into pygame's rendering/audio subsystems, and both were developed against headless
(`SDL_VIDEODRIVER=dummy`) smoke tests plus real two-window playtests before each
feature was considered done.

## Status

All phases from [ProjectArchitecture.md](ProjectArchitecture.md)'s milestone list are
implemented: window/terrain/turn setup, tank controls, projectile physics, combat,
terrain deformation, client/server networking, and polish (animation, sound, HUD,
restart flow).
