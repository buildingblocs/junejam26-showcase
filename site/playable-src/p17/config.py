WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765
BROADCAST_HZ = 20

PLAYER_RADIUS = 18
PLAYER_SPEED = 4
MIN_X = PLAYER_RADIUS
MAX_X = WINDOW_WIDTH - PLAYER_RADIUS
MIN_Y = 90 + PLAYER_RADIUS
MAX_Y = WINDOW_HEIGHT - PLAYER_RADIUS

INTERACTION_RANGE = 120
TERMINAL_WIDTH = 140
TERMINAL_HEIGHT = 72
TERMINAL_COLLISION_PADDING = 8
GAME_DURATION_SECONDS = 200
ROLE_REVEAL_GRACE_SECONDS = 6.0
MIN_PLAYERS = 3
DIFFICULTIES = ("easy", "medium", "hard")
TASK_COOLDOWN_SECONDS = 30
SYSTEM_START_HEALTH = 50
SYSTEM_HEALTH_DELTA = 10
SPECIALTY_BONUS = 5
ATTACK_POINT_REWARD = 1
ABILITY_COOLDOWN_SECONDS = 8
BLACKOUT_DURATION_SECONDS = 10
MALWARE_DAMAGE = 15

SPAWN_POINTS = (
    {"x": 455, "y": 560},
    {"x": 500, "y": 525},
    {"x": 545, "y": 560},
    {"x": 455, "y": 610},
    {"x": 545, "y": 610},
    {"x": 500, "y": 640},
)

TERMINALS = {
    "terminal_python": {
        "label": "Data Center",
        "x": 180,
        "y": 235,
        "color": (70, 150, 255),
    },
    "terminal_crypto": {
        "label": "Network Core",
        "x": 500,
        "y": 235,
        "color": (190, 100, 255),
    },
    "terminal_network": {
        "label": "Power Grid",
        "x": 820,
        "y": 235,
        "color": (70, 220, 150),
    },
}

NORMAL_TERMINALS = (
    "terminal_python",
    "terminal_crypto",
    "terminal_network",
)

INFRASTRUCTURE_SYSTEMS = {
    "terminal_python": "Data Center",
    "terminal_crypto": "Network Core",
    "terminal_network": "Power Grid",
}

ROLE_COLORS = {
    "Python Engineer": (70, 150, 255),
    "Cryptographer": (190, 100, 255),
    "Network Analyst": (70, 220, 150),
}
