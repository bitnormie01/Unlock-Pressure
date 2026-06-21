from unlock_pressure.backtest import run_backtest
from unlock_pressure.emitter import emit_strategy
from unlock_pressure.models import (
    BacktestResult,
    ImpactResult,
    PressureLevel,
    ReactionProfile,
    StrategyConfig,
    UnlockEvent,
)


class FakeStore:
    def get_price_series(self):
        return [
            {
                "symbol": "TOKEN-A",
                "unlock_date": "2026-06-25",
                "prices": {"-3": 1.0, "0": 1.0, "1": 0.94, "3": 0.91, "5": 0.88},
            }
        ]


def test_returns_result():
    strategy = emit_strategy(
        UnlockEvent("TOKEN-A", "2026-06-25", 60_000_000, "investor"),
        ImpactResult(0.12, 3.0, 60_000_000),
        PressureLevel.HIGH,
        ReactionProfile(PressureLevel.HIGH, 3, -0.02, -0.06, -0.09, -0.11, -0.10),
        StrategyConfig(),
    )

    result = run_backtest(strategy, FakeStore())

    assert isinstance(result, BacktestResult)
    assert result.capital_preserved_pct > 0
    assert result.max_drawdown_with > result.max_drawdown_without
    assert len(result.equity_curve) >= 2
    assert result.trades[0]["symbol"] == "TOKEN-A"
