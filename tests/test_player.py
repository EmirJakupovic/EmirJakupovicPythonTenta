from src.player import Player


def test_player_starts_at_given_position():
    """Krav: Spelaren ska ha en tydlig startposition."""
    p = Player(5, 7)
    assert p.pos() == (5, 7)


def test_player_move_to_updates_position():
    """Krav: Spelarens förflyttning ska uppdatera positionen."""
    p = Player(1, 1)
    p.move_to(3, 4)
    assert p.pos() == (3, 4)


def test_player_symbol_default_or_custom():
    """Krav: Spelaren ska kunna ha en symbol på kartan."""
    p1 = Player(0, 0)
    assert isinstance(p1.symbol, str)

    p2 = Player(0, 0, symbol="@")
    assert p2.symbol == "@"