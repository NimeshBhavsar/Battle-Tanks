# Tank Battle

A local-network, turn-based tank artillery game built with Pygame. Two tanks trade shots
across destructible terrain; an authoritative server owns physics and game state while
clients render and send input. See [ProjectArchitecture.md](ProjectArchitecture.md) for
the full design and development milestones.

## Status

- Phase 1 (Core): window creation, static terrain, two tanks on the map, and a turn indicator.
- Phase 2 (Tank Controls): move, rotate the barrel, adjust power. Moving spends the turn;
  aiming (rotate/power) doesn't.

## Running

```sh
uv run tankbattle
```

Controls (apply to whichever player's turn it is):

- `Left`/`A`, `Right`/`D` — move (spends the turn on release)
- `Up`/`W`, `Down`/`S` — rotate the barrel
- `E`/`Q` — increase/decrease firing power
- `Space` — pass the turn without moving

Close the window or press the window's close button to quit.
