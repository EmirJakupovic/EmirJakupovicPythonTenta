class Player:
    """Representerar spelaren och dess position."""

    def __init__(self, x: int, y: int, symbol: str = "@"):
        self.x = x
        self.y = y
        self.symbol = symbol

    def pos(self) -> tuple[int, int]:
        """Returnerar spelarens position."""
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        """Flyttar spelaren till en ny position."""
        self.x = x
        self.y = y