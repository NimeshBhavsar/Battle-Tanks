"""Game/session configuration, as opposed to the low-level constants in utils.constants."""

# Starting stats for each tank
TANK_START_HEALTH = 100
TANK_START_FUEL = 100

# Where the server saves each finished match's JSON stats and PNG chart (relative to where it was started)
STATS_DIR = "match_stats"

# Networking (used starting in Phase 6)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5555
