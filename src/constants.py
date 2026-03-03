# Samlar alla "magiska" värden på ett ställe (ger tydligare kod)

MOVE = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}

LAVA_COST_PER_STEP = 1

FRUIT_POINTS = 20
TRAP_PENALTY = 10
TREASURE_POINTS = 100

GROW_EVERY_TURNS = 25  # Bördig jord: ny frukt var 25:e drag

SYMBOL_EMPTY = "."
SYMBOL_WALL = "#"
SYMBOL_PLAYER = "@"

SYMBOL_TRAP = "X"
SYMBOL_SHOVEL = "S"
SYMBOL_KEY = "K"
SYMBOL_CHEST = "C"
SYMBOL_EXIT = "E"
