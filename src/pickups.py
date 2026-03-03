import random
from dataclasses import dataclass
from src import constants


# Här definierar jag alla olika "typer" av saker som kan ligga på kartan

@dataclass(frozen=True)
class Fruit:
    name: str
    value: int = constants.FRUIT_POINTS
    symbol: str = "?"

@dataclass(frozen=True)
class Trap:
    penalty: int = constants.TRAP_PENALTY
    symbol: str = constants.SYMBOL_TRAP

@dataclass(frozen=True)
class Key:
    symbol: str = constants.SYMBOL_KEY

@dataclass(frozen=True)
class Shovel:
    symbol: str = constants.SYMBOL_SHOVEL

@dataclass(frozen=True)
class Chest:
    symbol: str = constants.SYMBOL_CHEST

@dataclass(frozen=True)
class Exit:
    symbol: str = constants.SYMBOL_EXIT


FRUITS = [
    Fruit("apple", symbol="A"),
    Fruit("banana", symbol="B"),
    Fruit("cherry", symbol="H"),
    Fruit("pear", symbol="P"),
    Fruit("melon", symbol="M"),
]


def find_empty_spot(grid):
    """Försöker hitta en tom ruta (inte vägg, inte upptagen)."""
    for _ in range(2000):
        x = random.randint(1, grid.width - 2)
        y = random.randint(1, grid.height - 2)
        if grid.is_empty(x, y):
            return x, y
    return None


def place_many(grid, factory, count: int) -> int:
    """Placerar ut flera objekt på tomma rutor."""
    placed = 0
    for _ in range(count):
        spot = find_empty_spot(grid)
        if not spot:
            break
        x, y = spot
        grid.set(x, y, factory())
        placed += 1
    return placed


def place_fruits(grid, count: int) -> int:
    return place_many(grid, lambda: random.choice(FRUITS), count)


def spawn_one_fruit(grid) -> bool:
    """Skapar en ny frukt på en tom plats (bördig jord)."""
    spot = find_empty_spot(grid)
    if not spot:
        return False
    x, y = spot
    grid.set(x, y, random.choice(FRUITS))
    return True


def place_traps(grid, count: int) -> int:
    return place_many(grid, lambda: Trap(), count)


def place_shovels(grid, count: int = 1) -> int:
    return place_many(grid, lambda: Shovel(), count)


def place_keys(grid, count: int = 1) -> int:
    return place_many(grid, lambda: Key(), count)


def place_chests(grid, count: int = 1) -> int:
    return place_many(grid, lambda: Chest(), count)


def place_exit(grid) -> bool:
    """Placerar exit på en tom ruta."""
    spot = find_empty_spot(grid)
    if not spot:
        return False
    x, y = spot
    grid.set(x, y, Exit())
    return True
