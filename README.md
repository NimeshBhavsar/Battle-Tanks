# Tank Battle

A local-network, turn-based tank artillery game built with Pygame. Two tanks trade shots
across destructible terrain; an authoritative server owns physics and game state while
clients render and send input. See [ProjectArchitecture.md](ProjectArchitecture.md) for
the full design and development milestones.

## Status

Phase 1 (Core): window creation, static terrain, two tanks on the map, and a turn
indicator.

## Running

```sh
uv run tankbattle
```

Press `Space` to pass the turn. Close the window or press the window's close button to quit.
