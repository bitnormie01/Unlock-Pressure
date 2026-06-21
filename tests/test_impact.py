from unlock_pressure.impact import compute_supply_impact, compute_volume_impact


def test_supply_impact():
    assert compute_supply_impact(5_000_000, 100_000_000) == 0.05


def test_volume_impact():
    assert compute_volume_impact(10_000_000, 2.0, 40_000_000) == 0.5


def test_zero_guards():
    assert compute_supply_impact(5_000_000, 0) == 0.0
    assert compute_volume_impact(10_000_000, 2.0, 0) == 0.0
    assert compute_volume_impact(10_000_000, 0.0, 40_000_000) == 0.0
