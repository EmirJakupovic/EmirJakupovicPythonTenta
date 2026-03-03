class Grid:
    """
    Kartan ansvarar för rutor, väggar och rendering.
    Objekt med attributet .symbol visas med den symbolen.
    """

    def __init__(self, width: int = 20, height: int = 12, empty: str = ".", wall: str = "#"):
        self.width = width
        self.height = height
        self.empty = empty
        self.wall = wall

        # _cells[y][x]
        self._cells = [[self.empty for _ in range(self.width)] for _ in range(self.height)]
        self.player = None

        self.make_walls()

    def set_player(self, player) -> None:
        self.player = player

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int):
        # Utanför kartan räknas som vägg så spelaren inte kan gå ut
        if not self.in_bounds(x, y):
            return self.wall
        return self._cells[y][x]

    def set(self, x: int, y: int, value) -> None:
        if self.in_bounds(x, y):
            self._cells[y][x] = value

    def clear(self, x: int, y: int) -> None:
        self.set(x, y, self.empty)

    def is_empty(self, x: int, y: int) -> bool:
        return self.get(x, y) == self.empty

    def make_walls(self) -> None:
        """
        Skapar ytterväggar + inre väggar med loopar.
        Viktigt: lämna öppningar så att inga områden blir låsta.
        """
        # Ytterram
        for x in range(self.width):
            self.set(x, 0, self.wall)
            self.set(x, self.height - 1, self.wall)

        for y in range(self.height):
            self.set(0, y, self.wall)
            self.set(self.width - 1, y, self.wall)

        # Inre vertikal vägg med en öppning
        x = self.width // 3
        door_y = self.height // 2
        for y in range(1, self.height - 1):
            if y == door_y:
                continue
            self.set(x, y, self.wall)

        # Inre horisontell vägg med en öppning
        y = self.height // 3
        door_x = self.width // 2
        for x2 in range(1, self.width - 1):
            if x2 == door_x:
                continue
            self.set(x2, y, self.wall)

    def __str__(self) -> str:
        """Renderar kartan som text, och ritar spelaren ovanpå."""
        lines = []
        px, py = (None, None)
        if self.player:
            px, py = self.player.x, self.player.y

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == px and y == py:
                    row.append(self.player.symbol)
                    continue

                cell = self._cells[y][x]
                if hasattr(cell, "symbol"):
                    row.append(cell.symbol)
                else:
                 §   row.append(str(cell))
            lines.append("".join(row))
        return "\n".join(lines)
