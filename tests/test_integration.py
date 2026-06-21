from unlock_pressure.backtest import run_backtest
from unlock_pressure.classifier import classify_pressure
from unlock_pressure.emitter import emit_strategy
from unlock_pressure.fixtures.loader import FixtureStore
from unlock_pressure.impact import compute_supply_impact, compute_volume_impact
from unlock_pressure.models import ImpactResult, PressureLevel, ReactionProfile, StrategyConfig


def test_full_pipeline():
    store = FixtureStore()
    event = store.get_unlocks()[0]
    info = store.get_token_info(event.token_symbol)
    quote = store.get_quotes(event.token_symbol)[0]

    supply_ratio = compute_supply_impact(event.unlock_amount, info.circulating_supply)
    volume_ratio = compute_volume_impact(event.unlock_amount, quote.price, quote.volume_24h)
    pressure = classify_pressure(supply_ratio, volume_ratio)
    reaction = ReactionProfile(pressure, 3, -0.02, -0.05, -0.08, -0.1, -0.09)
    card = emit_strategy(
        event,
        ImpactResult(supply_ratio, volume_ratio, event.unlock_amount * quote.price),
        pressure,
        reaction,
        StrategyConfig(),
    )

    result = run_backtest(card, store)

    assert pressure == PressureLevel.HIGH
    assert card.event.token_symbol == event.token_symbol
    assert result.capital_preserved_pct > 0
    assert len(result.equity_curve) >= 2
