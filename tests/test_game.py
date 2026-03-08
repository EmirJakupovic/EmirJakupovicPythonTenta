from src import constants


def test_lava_cost_per_step_is_1():
    """Krav: The floor is lava - varje steg ska kosta 1 poäng."""
    assert constants.LAVA_COST_PER_STEP == 1


def test_grace_period_is_5_steps():
    """Krav (V3): Efter pickup kan man gå 5 steg utan att lava dras."""
    assert constants.GRACE_STEPS_AFTER_PICKUP == 5


def test_bomb_timer_is_3_turns():
    """Krav (V3): Bomb exploderar efter 3 drag."""
    assert constants.BOMB_TIMER_START == 3