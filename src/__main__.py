from __future__ import annotations

import argparse
import statistics
from pathlib import Path
from typing import Sequence

from unlock_pressure.backtest import run_backtest
from unlock_pressure.classifier import classify_pressure
from unlock_pressure.emitter import emit_strategy, render_markdown, render_yaml
from unlock_pressure.fixtures.loader import FixtureStore
from unlock_pressure.impact import compute_supply_impact, compute_volume_impact
from unlock_pressure.models import ImpactResult, PressureLevel, ReactionProfile, StrategyConfig


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="unlock-pressure")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--mode", choices=["fixture", "live"], default="fixture")
    run_parser.add_argument("--min-pressure", choices=["low", "medium", "high"], default="low")
    run_parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args(argv)

    if args.command == "run":
        if args.mode == "live":
            print("Live mode requires optional CMC credentials and is skipped in this demo.")
            return 2
        return _run_fixture(args.output_dir, args.min_pressure)
    return 1


def _run_fixture(output_dir: str, min_pressure: str) -> int:
    store = FixtureStore()
    config = StrategyConfig()
    cards = []
    for event in store.get_unlocks():
        info = store.get_token_info(event.token_symbol)
        quote = store.get_quotes(event.token_symbol)[0]
        supply_ratio = compute_supply_impact(event.unlock_amount, info.circulating_supply)
        volume_ratio = compute_volume_impact(event.unlock_amount, quote.price, quote.volume_24h)
        pressure = classify_pressure(supply_ratio, volume_ratio)
        if _pressure_rank(pressure) < _pressure_rank(PressureLevel(min_pressure.upper())):
            continue
        impact = ImpactResult(
            supply_ratio=supply_ratio,
            volume_ratio=volume_ratio,
            unlock_value_usd=event.unlock_amount * quote.price,
        )
        reaction = _reaction_profile(pressure, store)
        cards.append(emit_strategy(event, impact, pressure, reaction, config))

    cards.sort(
        key=lambda card: (
            _pressure_rank(card.pressure),
            card.impact.volume_ratio,
            card.impact.supply_ratio,
        ),
        reverse=True,
    )
    if not cards:
        print("Unlock Pressure: no fixture events matched the requested pressure filter.")
        return 0

    top = cards[0]
    backtest = run_backtest(top, store)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "strategy-card.yaml").write_text(render_yaml(top), encoding="utf-8")
    (target_dir / "strategy-card.md").write_text(render_markdown(top), encoding="utf-8")

    print("Unlock Pressure fixture scan")
    print("============================")
    for card in cards:
        print(
            f"{card.event.token_symbol:7} {card.event.unlock_date} "
            f"{card.pressure.value:6} supply={card.impact.supply_ratio * 100:5.2f}% "
            f"volume={card.impact.volume_ratio * 100:6.1f}%"
        )
    print()
    print(f"Top event: {top.event.token_symbol} {top.event.unlock_date} {top.pressure.value}")
    print(f"Historical 5d median: {top.reaction.median_post_5d * 100:.2f}%")
    print(f"Backtest capital preserved: {backtest.capital_preserved_pct:.2f}%")
    print(f"Strategy files: {target_dir / 'strategy-card.yaml'}, {target_dir / 'strategy-card.md'}")
    return 0


def _reaction_profile(pressure: PressureLevel, store: FixtureStore) -> ReactionProfile:
    rows = [
        row
        for row in store.get_price_series()
        if _classify_series(row, store) == pressure
    ]
    return ReactionProfile(
        pressure_level=pressure,
        sample_size=len(rows),
        median_pre_3d=_median_change(rows, "-3"),
        median_post_1d=_median_change(rows, "1"),
        median_post_3d=_median_change(rows, "3"),
        median_post_5d=_median_change(rows, "5"),
        median_post_7d=_median_change(rows, "7"),
    )


def _classify_series(row: dict, store: FixtureStore) -> PressureLevel:
    event = next(
        event
        for event in store.get_unlocks()
        if event.token_symbol == row["symbol"] and event.unlock_date == row["unlock_date"]
    )
    info = store.get_token_info(event.token_symbol)
    current_price = float(row["prices"]["0"])
    volume = float(row.get("volume_24h", store.get_quotes(event.token_symbol)[0].volume_24h))
    return classify_pressure(
        compute_supply_impact(event.unlock_amount, info.circulating_supply),
        compute_volume_impact(event.unlock_amount, current_price, volume),
    )


def _median_change(rows: list[dict], offset: str) -> float:
    changes = []
    for row in rows:
        base = float(row["prices"]["0"])
        if base > 0 and offset in row["prices"]:
            changes.append((float(row["prices"][offset]) / base) - 1.0)
    if not changes:
        return 0.0
    return statistics.median(changes)


def _pressure_rank(pressure: PressureLevel) -> int:
    return {
        PressureLevel.LOW: 1,
        PressureLevel.MEDIUM: 2,
        PressureLevel.HIGH: 3,
    }[pressure]


if __name__ == "__main__":
    raise SystemExit(main())
