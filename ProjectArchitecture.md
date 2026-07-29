# Overall Architecture

```
                   +----------------------+
                   |      server.py       |
                   |----------------------|
                   | Game Controller      |
                   | Turn Management      |
                   | Physics Authority    |
                   | Collision Detection  |
                   +----------+-----------+
                              |
                Local Network (Sockets)
            ------------------------------
             |                            |
             |                            |
      +------+-------+             +------+-------+
      | client.py    |             | client.py    |
      |--------------|             |--------------|
      | Render Game  |             | Render Game  |
      | Read Inputs  |             | Read Inputs  |
      +------+-------+             +------+-------+
             |                            |
             +------------+---------------+
                          |
                   Shared Game State
```

The server is the **single source of truth**.

Clients **never calculate physics**.

Clients only

* draw
* send player input
* receive updated game state

---

# Project Structure

```
TankBattle/

assets/
    tanks/
    terrain/
    explosions/
    sounds/
    fonts/

server.py

client.py

network.py

settings.py

main.py

models/

    tank.py
    projectile.py
    terrain.py
    ammunition.py
    player.py

engine/

    physics.py
    collision.py
    damage.py
    turn_manager.py
    terrain_engine.py

ui/

    game_screen.py
    hud.py
    menu.py

utils/

    constants.py
    helpers.py
```

---

# Main Game Objects

## Tank

```
Tank

health
position
angle
fuel
current_ammo
velocity

Methods

move()
rotate_barrel()
fire()
take_damage()
```

---

## Projectile

```
Projectile

position
velocity
weight
damage
blast_radius

Methods

update()
explode()
```

---

## Terrain

```
Terrain

height_map

Methods

draw()

destroy_circle()

collision()

height_at()
```

Terrain deformation is one of the coolest parts.

Instead of pixels, store terrain as a height map.

Example

```
Before

###############

After explosion

######____#####
```

---

## Ammunition

Create a base class.

```
Ammo

name

weight

damage

blast_radius

sprite
```

Then derive

```
LightShell

MediumShell

HeavyShell
```

Example values

| Ammo   | Weight | Damage | Radius |
| ------ | ------ | ------ | ------ |
| Light  | 1      | 20     | 20     |
| Medium | 3      | 40     | 35     |
| Heavy  | 6      | 70     | 50     |

Weight affects projectile motion.

---

# Turn Manager

Very simple.

```
Player 1

↓

Move

or

Shoot

↓

End Turn

↓

Player 2

↓

Move

or

Shoot
```

Pseudo

```
current_player

wait for action

if moved

    next turn

if fired

    simulate projectile

    explosion

    damage

    terrain

    next turn
```

---

# Physics Engine

This should be isolated.

Input

```
Position

Angle

Power

Weight
```

Output

```
Projectile Position
```

Formula

```
vx = power * cos(angle)

vy = power * sin(angle)

gravity = 9.8 * weight_factor
```

Every frame

```
x += vx

y += vy

vy += gravity
```

This module should know nothing about tanks.

---

# Collision Engine

Checks

```
Projectile

↓

Terrain?

↓

Tank?

↓

Out of map?
```

Returns

```
Explosion Point
```

---

# Damage Engine

Input

```
Explosion

Tank Position
```

Calculate

```
distance

↓

Damage

↓

Tank Health
```

Example

```
Damage

100%

80%

60%

40%

10%

0%
```

The closer to the centre of the explosion, the higher the damage.

---

# Terrain Engine

Receives

```
Explosion

Radius
```

Produces

```
Crater
```

Example

```
###########

Explosion

###########

After

#####___###
```

---

# Networking

Only the server performs calculations.

Clients send

```
Move Left

Move Right

Fire

Angle

Power

Ammo
```

Server broadcasts

```
Tank1 Position

Tank2 Position

Projectile Position

Terrain

Health

Turn

Winner
```

---

# State Machine

```
Waiting for Player

↓

Player Choosing

↓

Player Moves

↓

End Turn

OR

Player Fires

↓

Projectile Flying

↓

Explosion

↓

Damage

↓

Terrain Update

↓

Next Turn
```

---

# Rendering Order

```
Sky

↓

Terrain

↓

Tank 1

↓

Tank 2

↓

Projectile

↓

Explosion

↓

HUD
```

---

# HUD

Display

```
Health

Ammo

Current Turn

Power

Angle
```

Example

```
Player 1

Health 85

Ammo

Light

Medium

Heavy

Power 72%

Angle 53°

--------------------

Player 2

Health 63
```

---

# Game Loop

```
Receive Network

↓

Update Objects

↓

Physics

↓

Collision

↓

Terrain

↓

Damage

↓

Draw Screen

↓

Repeat
```

---

# Suggested Development Milestones

Rather than trying to build everything at once, implement features in this order:

### Phase 1: Core

* Window creation with Pygame
* Static terrain
* Two tanks placed on the map
* Turn indicator

### Phase 2: Tank Controls

* Move left/right during a turn
* Rotate cannon
* Adjust firing power
* Restrict to one action (move or shoot) per turn

### Phase 3: Projectile Physics

* Fire shells using projectile motion
* Different trajectories based on shell weight
* Visualise the shell's flight

### Phase 4: Combat

* Detect collisions with tanks
* Apply distance-based damage
* Reduce health and detect game over

### Phase 5: Terrain Deformation

* Carve craters where shells explode
* Ensure tanks interact correctly with modified terrain
* Prevent movement through destroyed ground

### Phase 6: Networking

* Build the authoritative server
* Synchronise game state between two clients
* Handle turn switching over the network

### Phase 7: Polish

* Explosion animations
* Sound effects
* Health bars and HUD improvements
* Victory screen and restart option
* Optional wind, fuel limits, or power-ups

## Design Principles

To keep the code maintainable:

* **Server is authoritative:** only the server computes physics, collisions, health, and terrain changes.
* **Clients are "dumb":** they render the received game state and send player inputs.
* **Each module has one responsibility:** physics doesn't know about networking, rendering doesn't know about damage calculations, and terrain logic doesn't know about UI.
* **Represent game state as serialisable data:** positions, health, terrain, and turn information should be easy to send over sockets as JSON or another simple format.

Following this architecture will make the project easier to implement incrementally, debug, and extend with features like wind, AI opponents, or additional ammunition types later.
