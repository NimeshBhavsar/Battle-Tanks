"""Low-level constants shared across the game: screen size, colors, timing."""

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
FPS = 60

WINDOW_TITLE = "Tank Battle"

# Colors (R, G, B)
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (101, 67, 33)
GROUND_OUTLINE_COLOR = (60, 40, 20)
PLAYER1_COLOR = (200, 60, 60)
PLAYER2_COLOR = (60, 90, 200)
BARREL_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HUD_TEXT_COLOR = WHITE

# Tank dimensions, in pixels
TANK_WIDTH = 40
TANK_HEIGHT = 20
BARREL_LENGTH = 28
BARREL_THICKNESS = 4
TANK_HITBOX_PADDING = 10  # extra px on every side of the drawn body that still counts as a hit

# Tank controls (Phase 2)
TANK_MOVE_SPEED = 3.0  # px/frame
TANK_FUEL_COST_PER_FRAME = 0.5
TANK_ROTATE_SPEED = 2.0  # degrees/frame
TANK_MIN_ANGLE = 0.0
TANK_MAX_ANGLE = 180.0
TANK_POWER_STEP = 1.0  # percent/frame
TANK_POWER_MIN = 0.0
TANK_POWER_MAX = 100.0

# Projectile physics (Phase 3)
LAUNCH_POWER_SCALE = 0.25  # tank.power percent -> px/frame launch speed
AMMO_WEIGHT_GRAVITY_SCALE = 0.05  # ammo.weight -> gravity contribution
PROJECTILE_RADIUS_MIN = 3
PROJECTILE_RADIUS_PER_WEIGHT = 1.2  # heavier ammo draws (and hits) as a bigger ball
PROJECTILE_COLOR = (20, 20, 20)
EXPLOSION_COLOR = (255, 140, 0)
EXPLOSION_CORE_COLOR = (255, 245, 180)
EXPLOSION_RADIUS = 18
EXPLOSION_FRAMES = 15

# Aim trajectory preview
TRAJECTORY_DOT_COLOR = (255, 230, 0)
TRAJECTORY_DOT_RADIUS = 2
TRAJECTORY_MAX_POINTS = 25
TRAJECTORY_STEPS_PER_POINT = 3
TRAJECTORY_VISIBLE_FRACTION = 0.6  # only preview the first 60% of the arc, to keep aiming a skill

# Fuel pickups
FUEL_PICKUP_MAX = 3  # most cans on the map at once
FUEL_PICKUP_START = 2  # cans present at match start
FUEL_PICKUP_REFILL = 40  # fuel restored per can
FUEL_PICKUP_MIN_TANK_DISTANCE = 80  # don't spawn a can right on top of a tank
FUEL_PICKUP_EDGE_MARGIN = 40
FUEL_PICKUP_WIDTH = 14
FUEL_PICKUP_HEIGHT = 18
FUEL_PICKUP_COLOR = (210, 40, 40)
FUEL_PICKUP_CAP_COLOR = (240, 200, 40)

# Visual effects (client-side only)
SHAKE_PER_BLAST_RADIUS = 0.15  # shake strength in px per px of blast radius
SHAKE_FRAMES = 14
HIT_FLASH_FRAMES = 12
DEFAULT_EXPLOSION_RADIUS = 30  # used if the server doesn't say how big an explosion was
MAX_PARTICLES = 400
SMOKE_TRAIL_COLOR = (200, 200, 200)
EXPLOSION_SMOKE_COLOR = (90, 90, 90)
DEBRIS_COLORS = (GROUND_COLOR, GROUND_OUTLINE_COLOR, (140, 100, 55))

# Floating damage numbers
DAMAGE_POPUP_COLOR = (230, 30, 30)
DAMAGE_POPUP_FRAMES = 75  # how long the "-15 HP" text stays up
DAMAGE_POPUP_RISE = 30  # px it drifts upward over its lifetime

# HUD scoreboard bars
BAR_WIDTH = 140
BAR_HEIGHT = 10
BAR_GAP = 4
BAR_BG_COLOR = (40, 40, 40)
HP_BAR_COLOR = (60, 200, 60)
FUEL_BAR_COLOR = (90, 150, 230)

# Menu / name editing
MAX_NAME_LENGTH = 16
MENU_BG_COLOR = (0, 0, 0)
MENU_HIGHLIGHT_COLOR = (255, 230, 0)
