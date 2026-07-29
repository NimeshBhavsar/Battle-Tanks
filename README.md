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
- Phase 4 (Combat): shells detonate on hitting a tank, the ground, or the map edge;
  damage falls off with distance from the blast center; the game ends when only one
  tank (or none) is left standing.
- Phase 5 (Terrain Deformation): explosions carve craters into the terrain; tanks
  settle onto the reshaped ground after every blast.
- Phase 6 (Networking): the game is now a real client/server split. `server.py` owns
  the simulation and runs headless; `client.py` connects over TCP, renders whatever
  the server broadcasts, and sends local input. This replaced the old single-process
  hot-seat mode.
- Phase 7 (Polish): animated explosions, synthesized fire/impact sound effects, HP and
  fuel bars in the scoreboard, and a restart flow after a win/draw. Tank hitboxes are
  now shaped like the actual tank + barrel rather than a flat inflated rectangle, and
  each match now generates fresh random terrain instead of the same fixed layout.

While aiming, a dotted yellow line previews the shell's arc for the current angle,
power, and ammo, updating live as you adjust either — though it only traces the first
60% of the arc, so landing a shot still takes some judgment. Shell size (and hit size)
scales with ammo weight — Heavy rounds draw and hit as a noticeably bigger ball than
Light ones.

Press `Esc` any time to open the menu, where you can rename yourself and — once a
match has ended — restart with fresh terrain.

## Running

Start the server first, then connect two clients (in separate terminals — each opens
its own window):

```sh
uv run tankbattle server
uv run tankbattle client   # player 1
uv run tankbattle client   # player 2
```

By default the server listens on `127.0.0.1:5555`; both subcommands accept `--host`
and `--port` to point at a different address (e.g. to play over a LAN).

Controls (apply on your turn):

- `Left`/`A`, `Right`/`D` — move (spends the turn on release)
- `Up`/`W`, `Down`/`S` — rotate the barrel
- `E`/`Q` — increase/decrease firing power
- `1`/`2`/`3` — select Light/Medium/Heavy shell
- `Space` — fire (spends the turn)
- `Esc` — open/close the menu

In the menu:

- `N` — edit your name (type, `Backspace` to correct, `Enter` to confirm, `Esc` to cancel)
- `R` — once a match has ended, restart with fresh terrain and full health
- `Esc` — close the menu

Close a window or press Ctrl+C on the server to quit.
