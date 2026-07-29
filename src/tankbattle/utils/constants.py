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
LAUNCH_POWER_SCALE = 0.15  # tank.power percent -> px/frame launch speed
AMMO_WEIGHT_GRAVITY_SCALE = 0.05  # ammo.weight -> gravity contribution
PROJECTILE_RADIUS = 4
PROJECTILE_COLOR = (20, 20, 20)
EXPLOSION_COLOR = (255, 140, 0)
EXPLOSION_RADIUS = 18
EXPLOSION_FRAMES = 15

# Aim trajectory preview
TRAJECTORY_DOT_COLOR = (255, 230, 0)
TRAJECTORY_DOT_RADIUS = 2
TRAJECTORY_MAX_POINTS = 25
TRAJECTORY_STEPS_PER_POINT = 3
