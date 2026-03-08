class Grid:
    """Hanterar kartan, väggar och objekt."""

    def __init__(self, width: int = 20, height: int = 12, empty: str = ".", wall: str = "#"):
        self.width = width
        self.height = height
        self.empty = empty
        self.wall = wall
        self.player = None

        self._cells = [
            [self.empty for _ in range(self.width)]
            for _ in range(self.height)
        ]

        self.make_walls()

    def set_player(self, player) -> None:
        """Kopplar spelaren till kartan."""
        self.player = player

    def in_bounds(self, x: int, y: int) -> bool:
        """Kontrollerar om positionen ligger inom kartan."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int):
        """Returnerar innehållet i en ruta."""
        if not self.in_bounds(x, y):
            return self.wall
        return self._cells[y][x]

    def set(self, x: int, y: int, value) -> None:
        """Sätter ett värde i en ruta."""
        if self.in_bounds(x, y):
            self._cells[y][x] = value

    def clear(self, x: int, y: int) -> None:
        """Tömmer en ruta."""
        if self.in_bounds(x, y):
            self._cells[y][x] = self.empty

    def is_empty(self, x: int, y: int) -> bool:
        """Kontrollerar om en ruta är tom."""
        return self.get(x, y) == self.empty

    def is_wall(self, x: int, y: int) -> bool:
        """Kontrollerar om en ruta är en vägg."""
        return self.get(x, y) == self.wall

    def make_walls(self) -> None:
        """Skapar ytterväggar och inre väggar med öppningar."""
        for x in range(self.width):
            self.set(x, 0, self.wall)
            self.set(x, self.height - 1, self.wall)

        for y in range(self.height):
            self.set(0, y, self.wall)
            self.set(self.width - 1, y, self.wall)

        x = self.width // 3
        door_y = self.height // 2
        for y in range(1, self.height - 1):
            if y != door_y:
                self.set(x, y, self.wall)

        y = self.height // 3
        door_x = self.width // 2
        for x2 in range(1, self.width - 1):
            if x2 != door_x:
                self.set(x2, y, self.wall)

    def __str__(self) -> str:
        """Returnerar kartan som text."""
        lines = []

        px, py = (None, None)
        if self.player is not None:
            px, py = self.player.x, self.player.y

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == px and y == py:
                    row.append(self.player.symbol)
                else:
                    cell = self._cells[y][x]
                    if hasattr(cell, "symbol"):
                        row.append(cell.symbol)
                    else:
                        row.append(str(cell))
            lines.append("".join(row))

        return "\n".join(lines)