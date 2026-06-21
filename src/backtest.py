from __future__ import annotations

from typing import Protocol

from unlock_pressure.models import BacktestResult, PressureLevel, StrategyCard


class PriceSeriesStore(Protocol):
    def get_price_series(self) -> list[dict]:
        ...


def run_backtest(strategy: StrategyCard, fixture_store: PriceSeriesStore) -> BacktestResult:
    series = _find_series(strategy, fixture_store.get_price_series())
    prices = {str(key): float(value) for key, value in series["prices"].items()}
    start_price = prices.get("-3", prices.get("0", 1.0))
    ordered_offsets = [-3, 0, 1, 3, 5, 7, 14]
    reduction = _reduction_for_strategy(strategy)

    equity_curve: list[dict[str, float | str]] = []
    with_values: list[float] = []
    without_values: list[float] = []
    for offset in ordered_offsets:
        key = str(offset)
        if key not in prices:
            continue
        hold_equity = prices[key] / start_price
        protected_equity = reduction + ((1.0 - reduction) * hold_equity)
        without_values.append(hold_equity)
        with_values.append(protected_equity)
        equity_curve.append(
            {
                "offset_days": float(offset),
                "with_strategy": protected_equity,
                "without_strategy": hold_equity,
            }
        )

    final_with = with_values[-1]
    final_without = without_values[-1]
    preserved = max(0.0, final_with - final_without) * 100

    return BacktestResult(
        capital_preserved_pct=preserved,
        max_drawdown_with=_max_drawdown(with_values),
        max_drawdown_without=_max_drawdown(without_values),
        equity_curve=equity_curve,
        trades=[
            {
                "symbol": strategy.event.token_symbol,
                "unlock_date": strategy.event.unlock_date,
                "reduction_pct": reduction,
            }
        ],
    )


def _find_series(strategy: StrategyCard, rows: list[dict]) -> dict:
    for row in rows:
        if (
            row.get("symbol") == strategy.event.token_symbol
            and row.get("unlock_date") == strategy.event.unlock_date
        ):
            return row
    raise ValueError(f"missing price series for {strategy.event.token_symbol}")


def _reduction_for_strategy(strategy: StrategyCard) -> float:
    if strategy.pressure == PressureLevel.HIGH:
        return strategy.config.high_reduction_pct
    if strategy.pressure == PressureLevel.MEDIUM:
        return strategy.config.medium_reduction_pct
    return strategy.config.low_reduction_pct


def _max_drawdown(values: list[float]) -> float:
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = min(drawdown, (value / peak) - 1.0)
    return drawdown
