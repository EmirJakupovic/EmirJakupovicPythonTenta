import random

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
    grid = Grid(width=20, height=12, empty=constants.SYMBOL_EMPTY, wall=constants.SYMBOL_WALL)

    sx, sy = find_start_near_center(grid)
    player = Player(sx, sy, symbol=constants.SYMBOL_PLAYER)
    grid.set_player(player)

    # Vi samlar spel-state i en dict för att slippa många nonlocal
    state = {
        "score": 0,
        "turns": 0,
        "objectives_left": 0,
        "grace_steps": 0,               # Version 3: grace period
        "inventory": {"key": 0, "shovel": 0},
        "collected": [],                # namn på saker du plockat upp
        "bombs": [],                     # [{"x":..,"y":..,"timer":..}]
        "enemies": [],                   # [(x,y),...]
    }

    # --- Placera V2-objekt ---
    fruit_count = pickups.place_fruits(grid, count=8)
    pickups.place_traps(grid, count=4)
    shovel_count = pickups.place_shovels(grid, count=1)
    key_count = pickups.place_keys(grid, count=1)
    chest_count = pickups.place_chests(grid, count=1)
    pickups.place_exit(grid)

    # Målet: plocka upp frukt/spade/nyckel och öppna kista
    state["objectives_left"] = fruit_count + shovel_count + key_count + chest_count

    # --- Version 3: fiender ---
    enemy_count = random.randint(constants.ENEMY_COUNT_MIN, constants.ENEMY_COUNT_MAX)
    state["enemies"] = pickups.place_enemies(grid, enemy_count)

    # -------------------- Hjälpfunktioner --------------------

    def show_inventory():
        """Visar inventory och samlade saker."""
        inv = state["inventory"]
        print(f"Keys: {inv['key']} | Shovels: {inv['shovel']} | Grace: {state['grace_steps']}")
        if state["collected"]:
            print("Collected:", ", ".join(state["collected"]))
        else:
            print("Collected: (none)")

    def start_grace_period():
        """Grace period startar efter att du plockat upp något."""
        state["grace_steps"] = constants.GRACE_STEPS_AFTER_PICKUP

    def apply_lava_or_grace(steps: int):
        """
        Drar lava per steg, men om grace_steps > 0 så dras inget.
        Jump räknas som 2 steg.
        """
        for _ in range(steps):
            if state["grace_steps"] > 0:
                state["grace_steps"] -= 1
            else:
                state["score"] -= constants.LAVA_COST_PER_STEP

    def fertile_soil_growth():
        """Bördig jord: var 25:e drag växer en ny frukt."""
        if state["turns"] % constants.GROW_EVERY_TURNS == 0:
            if pickups.spawn_one_fruit(grid):
                print("A new fruit grew somewhere! (fertile soil)")
            else:
                print("No space to grow a new fruit.")

    def handle_wall_hit(wx: int, wy: int) -> str:
        """
        Man kan inte gå genom väggar.
        Har man en spade: väggen tas bort och spaden förbrukas.
        """
        inv = state["inventory"]
        if inv["shovel"] > 0:
            inv["shovel"] -= 1
            grid.clear(wx, wy)
            return "You used a shovel and removed the wall!"
        return "You can't walk through walls."

    def handle_landing(cell) -> str | None:
        """Interagerar med rutan du landar på."""
        inv = state["inventory"]

        # Frukt
        if isinstance(cell, pickups.Fruit):
            state["score"] += cell.value
            state["collected"].append(cell.name)
            state["objectives_left"] -= 1
            grid.clear(player.x, player.y)
            start_grace_period()
            return f"You picked up {cell.name}! +{cell.value} points."

        # Fälla
        if isinstance(cell, pickups.Trap):
            state["score"] -= cell.penalty
            return f"You stepped on a trap! -{cell.penalty} points."

        # Spade
        if isinstance(cell, pickups.Shovel):
            inv["shovel"] += 1
            state["collected"].append("shovel")
            state["objectives_left"] -= 1
            grid.clear(player.x, player.y)
            start_grace_period()
            return "You picked up a shovel."

        # Nyckel
        if isinstance(cell, pickups.Key):
            inv["key"] += 1
            state["collected"].append("key")
            state["objectives_left"] -= 1
            grid.clear(player.x, player.y)
            start_grace_period()
            return "You picked up a key."

        # Kista
        if isinstance(cell, pickups.Chest):
            if inv["key"] > 0:
                inv["key"] -= 1
                state["score"] += constants.TREASURE_POINTS
                state["collected"].append("treasure")
                state["objectives_left"] -= 1
                grid.clear(player.x, player.y)
                start_grace_period()
                return f"You opened the chest! +{constants.TREASURE_POINTS} points."
            return "The chest is locked. You need a key."

        # Exit
        if isinstance(cell, pickups.Exit):
            if state["objectives_left"] == 0:
                print("You reached the Exit and WIN! 🎉")
                raise SystemExit
            return "Exit does nothing yet. Collect/open everything first."

        # Fiende (om du råkar landa på fiende)
        if isinstance(cell, pickups.Enemy):
            state["score"] -= constants.ENEMY_CATCH_PENALTY
            return "An enemy caught you! -20 points."

        return None

    # -------------------- Version 3: Trap-disarm --------------------

    def disarm_trap():
        """
        Kommando T: desarmera en fälla.
        Vi kollar din ruta + 4 grannar och tar bort första fällan vi hittar.
        Räknas som ett drag.
        """
        state["turns"] += 1

        px, py = player.pos()
        positions = [(px, py), (px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)]

        for x, y in positions:
            if isinstance(grid.get(x, y), pickups.Trap):
                grid.clear(x, y)
                print("Trap disarmed!")
                tick_after_turn()
                return

        print("No trap nearby to disarm.")
        tick_after_turn()

    # -------------------- Version 3: Bomb --------------------

    def place_bomb():
        """
        Kommando B: placera en bomb på spelarens ruta.
        Exploderar efter 3 drag och förstör 3x3.
        Räknas som ett drag.
        """
        state["turns"] += 1
        px, py = player.pos()

        # Enkel regel: max en bomb per ruta
        for b in state["bombs"]:
            if b["x"] == px and b["y"] == py:
                print("There is already a bomb here.")
                tick_after_turn()
                return

        state["bombs"].append({"x": px, "y": py, "timer": constants.BOMB_TIMER_START})

        # Om rutan är tom så sätter vi en symbol (syns när spelaren går därifrån)
        if grid.is_empty(px, py):
            grid.set(px, py, pickups.Bomb())

        print("Bomb placed! (explodes in 3 turns)")
        tick_after_turn()

    def explode_bomb(bomb: dict):
        """Explosion: tar bort allt i 3x3 runt bomben."""
        bx, by = bomb["x"], bomb["y"]

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                x = bx + dx
                y = by + dy

                # Om spelaren står i explosionen får man poängavdrag
                if (x, y) == player.pos():
                    state["score"] -= constants.BOMB_HIT_PENALTY
                    print("BOOM! You were hit by the explosion! -30 points.")

                # Tar bort allt, även väggar (enligt uppgiften)
                grid.clear(x, y)

    def tick_bombs():
        """Uppdaterar bomb-timers och exploderar när timer når 0."""
        to_explode = []
        for b in state["bombs"]:
            b["timer"] -= 1
            if b["timer"] <= 0:
                to_explode.append(b)

        for b in to_explode:
            explode_bomb(b)
            state["bombs"].remove(b)

    # -------------------- Version 3: Enemies --------------------

    def move_one_enemy_step(ex: int, ey: int) -> tuple[int, int]:
        """
        Flyttar fiende 1 steg mot spelaren utan diagonaler.
        Vi testar en axel i taget så det blir enkelt.
        """
        px, py = player.pos()

        # Försök i x-led först om det behövs
        if px != ex:
            nx = ex + (1 if px > ex else -1)
            ny = ey
            if not grid.is_wall(nx, ny):
                return nx, ny

        # Annars försök i y-led
        if py != ey:
            nx = ex
            ny = ey + (1 if py > ey else -1)
            if not grid.is_wall(nx, ny):
                return nx, ny

        return ex, ey

    def move_enemies():
        """
        Varje fiende har en chans att flytta ett steg närmare.
        Om en fiende når spelaren: -20 poäng och fienden flyttas till tom ruta.
        """
        new_positions = []

        for (ex, ey) in state["enemies"]:
            # Ibland står fienden still (lagom svårt)
            if random.random() > constants.ENEMY_MOVE_CHANCE:
                new_positions.append((ex, ey))
                continue

            nx, ny = move_one_enemy_step(ex, ey)

            # Om fienden går in i spelaren
            if (nx, ny) == player.pos():
                state["score"] -= constants.ENEMY_CATCH_PENALTY
                print("An enemy caught you! -20 points.")

                # Ta bort fienden från sin ruta
                grid.clear(ex, ey)

                # Placera fienden på ny tom ruta
                spot = pickups.find_empty_spot(grid)
                if spot:
                    rx, ry = spot
                    grid.set(rx, ry, pickups.Enemy())
                    new_positions.append((rx, ry))
                else:
                    # Om ingen plats finns, låt den försvinna
                    pass
                continue

            # Om destination inte är tom: låt fienden stå kvar (enkel regel)
            dest = grid.get(nx, ny)
            if dest != constants.SYMBOL_EMPTY:
                new_positions.append((ex, ey))
                continue

            # Flytta fienden på kartan
            grid.clear(ex, ey)
            grid.set(nx, ny, pickups.Enemy())
            new_positions.append((nx, ny))

        state["enemies"] = new_positions

    # -------------------- Turn “pipeline” --------------------

    def tick_after_turn():
        """
        Körs efter varje drag (rörelse, B, T).
        Samlar allt som ska hända "efter ditt drag" på ett ställe.
        """
        tick_bombs()
        move_enemies()
        fertile_soil_growth()

    # -------------------- Movement --------------------

    def try_move(dx: int, dy: int, steps: int) -> None:
        """
        steps=1 normalt, steps=2 jump.
        Jump interagerar bara där man landar.
        """
        state["turns"] += 1

        px, py = player.pos()
        dest_x = px + dx * steps
        dest_y = py + dy * steps

        cell = grid.get(dest_x, dest_y)

        # Vägg: du flyttar inte, men lava/grace räknas ändå (enligt uppgiften för jump in i vägg)
        if cell == grid.wall:
            apply_lava_or_grace(steps)
            print(handle_wall_hit(dest_x, dest_y))
            tick_after_turn()
            return

        # Flytta spelaren
        player.move_to(dest_x, dest_y)

        # Lava eller grace
        apply_lava_or_grace(steps)

        # Interagera med rutan du landar på
        msg = handle_landing(cell)
        if msg:
            print(msg)

        tick_after_turn()

    # -------------------- Game loop --------------------

    while True:
        print()
        print(grid)
        print(
            f"Score: {state['score']} | Turns: {state['turns']} | "
            f"Objectives left: {state['objectives_left']} | Grace: {state['grace_steps']}"
        )

        cmd = input("\nCommand (WASD, i, q, jw/ja/js/jd, b, t): ").strip().lower()

        if cmd == "q":
            print("Bye!")
            break

        if cmd == "i":
            show_inventory()
            continue

        # Version 3: bomb
        if cmd == "b":
            place_bomb()
            continue

        # Version 3: disarm trap
        if cmd == "t":
            disarm_trap()
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

        print("Unknown command. Use WASD, i, q, j+WASD, b or t.")


if __name__ == "__main__":
    main()