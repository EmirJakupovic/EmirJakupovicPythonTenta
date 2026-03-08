# Samlar alla "magiska" värden på ett ställe (ger tydligare kod)

MOVE = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}

# Version 1
LAVA_COST_PER_STEP = 1

# Version 1/2
FRUIT_POINTS = 20
TRAP_PENALTY = 10
TREASURE_POINTS = 100
GROW_EVERY_TURNS = 25  # Bördig jord: ny frukt var 25:e drag

# Version 3
GRACE_STEPS_AFTER_PICKUP = 5

ENEMY_COUNT_MIN = 1
ENEMY_COUNT_MAX = 3
ENEMY_MOVE_CHANCE = 0.40
ENEMY_CATCH_PENALTY = 20

BOMB_TIMER_START = 3
BOMB_HIT_PENALTY = 30

# Symboler
SYMBOL_EMPTY = "."
SYMBOL_WALL = "#"
SYMBOL_PLAYER = "@"

SYMBOL_TRAP = "X"
SYMBOL_SHOVEL = "S"
SYMBOL_KEY = "K"
SYMBOL_CHEST = "C"
SYMBOL_EXIT = "E"

# Version 3 symboler
SYMBOL_ENEMY = "!"
SYMBOL_BOMB = "o"