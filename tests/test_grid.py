from src.grid import Grid
from src import constants


def test_outside_grid_is_wall():
    """Krav: Man ska inte kunna gå utanför kartan (utanför = vägg)."""
    g = Grid(width=10, height=6, empty=constants.SYMBOL_EMPTY, wall=constants.SYMBOL_WALL)

    assert g.get(-1, 0) == g.wall
    assert g.get(0, -1) == g.wall
    assert g.get(999, 0) == g.wall
    assert g.get(0, 999) == g.wall


def test_outer_walls_exist():
    """Krav: Väggar ska finnas runt ytterkanten."""
    g = Grid(width=10, height=6, empty=constants.SYMBOL_EMPTY, wall=constants.SYMBOL_WALL)

    # Översta och nedersta raden ska vara vägg
    for x in range(g.width):
        assert g.get(x, 0) == g.wall
        assert g.get(x, g.height - 1) == g.wall

    # Vänster och höger kolumn ska vara vägg
    for y in range(g.height):
        assert g.get(0, y) == g.wall
        assert g.get(g.width - 1, y) == g.wall


def test_clear_makes_cell_empty():
    """Krav: clear ska kunna tömma en ruta."""
    g = Grid(width=10, height=6, empty=constants.SYMBOL_EMPTY, wall=constants.SYMBOL_WALL)

    g.set(2, 2, "X")
    assert g.get(2, 2) == "X"

    g.clear(2, 2)
    assert g.get(2, 2) == g.empty