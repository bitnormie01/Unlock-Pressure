import yaml

from unlock_pressure.emitter import emit_strategy, render_yaml
from unlock_pressure.models import (
    ImpactResult,
    PressureLevel,
    ReactionProfile,
    StrategyConfig,
    UnlockEvent,
)


def _reaction() -> ReactionProfile:
    return ReactionProfile(
        pressure_level=PressureLevel.HIGH,
        sample_size=3,
        median_pre_3d=-0.02,
        median_post_1d=-0.06,
        median_post_3d=-0.09,
        median_post_5d=-0.11,
        median_post_7d=-0.10,
    )


def test_high_pressure_50pct_reduction():
    card = emit_strategy(
        event=UnlockEvent("TOKEN-A", "2026-06-25", 60_000_000, "investor"),
        impact=ImpactResult(0.12, 3.0, 60_000_000),
        pressure=PressureLevel.HIGH,
        reaction=_reaction(),
        config=StrategyConfig(),
    )

    assert "50%" in card.position_sizing
    assert "3 days before" in card.exit_rule
    assert "< 1%" in card.invalidation


def test_yaml_parseable():
    card = emit_strategy(
        event=UnlockEvent("TOKEN-A", "2026-06-25", 60_000_000, "investor"),
        impact=ImpactResult(0.12, 3.0, 60_000_000),
        pressure=PressureLevel.HIGH,
        reaction=_reaction(),
        config=StrategyConfig(),
    )

    parsed = yaml.safe_load(render_yaml(card))

    assert parsed["token"] == "TOKEN-A"
    assert parsed["pressure"] == "HIGH"
    assert parsed["strategy"]["position_reduction_pct"] == 0.5
