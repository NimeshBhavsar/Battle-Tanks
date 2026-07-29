# Tank Battle

A local-network, turn-based tank artillery game built with Pygame. Two tanks trade shots
across destructible terrain; an authoritative server owns physics and game state while
clients render and send input. See [ProjectArchitecture.md](ProjectArchitecture.md) for
the full design and development milestones.

## Status

- Phase 1 (Core): window creation, static terrain, two tanks on the map, and a turn indicator.
- Phase 2 (Tank Controls): move, rotate the barrel, adjust power. Moving spends the turn;
  aiming (rotate/power) doesn't.
- Phase 3 (Projectile Physics): fire shells with weight-dependent trajectories; firing
  spends the turn. Heavier shells arc shorter and drop faster.

## Running

```sh
uv run tankbattle
```

Controls (apply to whichever player's turn it is):

- `Left`/`A`, `Right`/`D` — move (spends the turn on release)
- `Up`/`W`, `Down`/`S` — rotate the barrel
- `E`/`Q` — increase/decrease firing power
- `1`/`2`/`3` — select Light/Medium/Heavy shell
- `Space` — fire (spends the turn)

Close the window or press the window's close button to quit.
