from src.grid import Grid
from src.player import Player
from src import pickups
from src import constants


def find_start_near_center(grid: Grid) -> tuple[int, int]:
    """Start nära mitten. Om mitten inte är tom, leta närmaste tomma ruta."""
    cx, cy = grid.width // 2, grid.height // 2
    if grid.is_empty(cx, cy):
        return cx, cy

    for r in range(1, max(grid.width, grid.height)):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x = cx + dx
                y = cy + dy
                if grid.is_empty(x, y):
                    return x, y

    return 1, 1


def main():
    grid = Grid(
        width=20,
        height=12,
        empty=constants.SYMBOL_EMPTY,
        wall=constants.SYMBOL_WALL,
    )

    sx, sy = find_start_near_center(grid)
    player = Player(sx, sy, symbol=constants.SYMBOL_PLAYER)
    grid.set_player(player)

    # Spel-state (poäng, drag, inventory)
    score = 0
    turns = 0

    # Inventory som räknare: tydligt för förbrukningsbara saker (nyckel/spade)
    inventory = {"key": 0, "shovel": 0}
    collected_names = []  # här sparar vi frukter/skatt för att visa med i

    # Slumpa ut objekt (Version 2)
    fruit_count = pickups.place_fruits(grid, count=8)
    pickups.place_traps(grid, count=4)
    shovel_count = pickups.place_shovels(grid, count=1)
    key_count = pickups.place_keys(grid, count=1)
    chest_count = pickups.place_chests(grid, count=1)
    pickups.place_exit(grid)

    # "Objectives left" = allt ursprungligt som måste samlas/öppnas innan exit ska vinna
    objectives_left = fruit_count + shovel_count + key_count + chest_count

    def show_inventory():
        """Skriver ut inventory och vad som samlats."""
        print(f"Keys: {inventory['key']} | Shovels: {inventory['shovel']}")
        if collected_names:
            print("Collected:", ", ".join(collected_names))
        else:
            print("Collected: (none)")

    def fertile_soil_growth():
        """Bördig jord: var 25:e drag växer en ny frukt."""
        if turns % constants.GROW_EVERY_TURNS == 0:
            if pickups.spawn_one_fruit(grid):
                print("A new fruit grew somewhere! (fertile soil)")
            else:
                print("No space to grow a new fruit.")

    def handle_wall_hit(wx: int, wy: int) -> str:
        """Spade: nästa vägg du går in i tas bort, och spaden förbrukas."""
        if inventory["shovel"] > 0:
            inventory["shovel"] -= 1
            grid.clear(wx, wy)
            return "You used a shovel and removed the wall!"
        return "You can't walk through walls."

    def handle_landing(cell) -> str | None:
        """Interagerar med rutan du landar på."""
        nonlocal score, objectives_left

        # Frukt
        if isinstance(cell, pickups.Fruit):
            score += cell.value
            collected_names.append(cell.name)
            objectives_left -= 1
            grid.clear(player.x, player.y)
            return f"You picked up {cell.name}! +{cell.value} points."

        # Fälla
        if isinstance(cell, pickups.Trap):
            score -= cell.penalty
            return f"You stepped on a trap! -{cell.penalty} points."

        # Spade
        if isinstance(cell, pickups.Shovel):
            inventory["shovel"] += 1
            collected_names.append("shovel")
            objectives_left -= 1
            grid.clear(player.x, player.y)
            return "You picked up a shovel."

        # Nyckel
        if isinstance(cell, pickups.Key):
            inventory["key"] += 1
            collected_names.append("key")
            objectives_left -= 1
            grid.clear(player.x, player.y)
            return "You picked up a key."

        # Kista
        if isinstance(cell, pickups.Chest):
            if inventory["key"] > 0:
                inventory["key"] -= 1
                score += constants.TREASURE_POINTS
                collected_names.append("treasure")
                objectives_left -= 1
                grid.clear(player.x, player.y)
                return f"You opened the chest! +{constants.TREASURE_POINTS} points."
            return "The chest is locked. You need a key."

        # Exit
        if isinstance(cell, pickups.Exit):
            if objectives_left == 0:
                print("You reached the Exit and WIN! 🎉")
                raise SystemExit
            return "Exit does nothing yet. Collect/open everything first."

        return None

    def try_move(dx: int, dy: int, steps: int) -> None:
        """
        Movement. steps=1 normal, steps=2 jump.
        Jump interagerar bara där man landar.
        """
        nonlocal score, turns

        turns += 1

        px, py = player.pos()
        dest_x = px + dx * steps
        dest_y = py + dy * steps

        dest_cell = grid.get(dest_x, dest_y)

        # Om destinationen är vägg: samma effekt som att gå in i vägg
        if dest_cell == grid.wall:
            # Lava-kostnad dras även när man "försöker" (inkl jump in i vägg)
            score -= steps * constants.LAVA_COST_PER_STEP
            print(handle_wall_hit(dest_x, dest_y))
            fertile_soil_growth()
            return

        # Flytta
        player.move_to(dest_x, dest_y)

        # Lava-kostnad (per steg)
        score -= steps * constants.LAVA_COST_PER_STEP

        # Interaktion på landningsrutan
        msg = handle_landing(dest_cell)
        if msg:
            print(msg)

        fertile_soil_growth()

    # Spelloop
    while True:
        print()
        print(grid)
        print(f"Score: {score} | Turns: {turns} | Objectives left: {objectives_left}")

        cmd = input("\nCommand (WASD, i, q, jw/ja/js/jd): ").strip().lower()

        if cmd == "q":
            print("Bye!")
            break

        if cmd == "i":
            show_inventory()
            continue

        # Jump: j + direction
        if len(cmd) == 2 and cmd[0] == "j" and cmd[1] in constants.MOVE:
            dx, dy = constants.MOVE[cmd[1]]
            try_move(dx, dy, steps=2)
            continue

        # Normal move
        if cmd in constants.MOVE:
            dx, dy = constants.MOVE[cmd]
            try_move(dx, dy, steps=1)
            continue

        print("Unknown command. Use WASD, i, q or j+WASD.")


if __name__ == "__main__":
    main()
