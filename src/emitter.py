from __future__ import annotations

import yaml

from unlock_pressure.models import (
    ImpactResult,
    PressureLevel,
    ReactionProfile,
    StrategyCard,
    StrategyConfig,
    UnlockEvent,
)


def emit_strategy(
    event: UnlockEvent,
    impact: ImpactResult,
    pressure: PressureLevel,
    reaction: ReactionProfile,
    config: StrategyConfig,
) -> StrategyCard:
    reduction = _reduction_for_pressure(pressure, config)
    percent = int(reduction * 100)
    return StrategyCard(
        event=event,
        impact=impact,
        pressure=pressure,
        reaction=reaction,
        config=config,
        entry_rule=(
            "Re-enter after volume normalizes near the 30-day average and "
            "daily range contracts below 2x its recent average."
        ),
        exit_rule=f"Reduce exposure {config.pre_event_days} days before unlock.",
        position_sizing=f"Reduce spot exposure by {percent}% for {pressure.value} pressure.",
        invalidation="Invalidate if unlock is absorbed with < 1% price drop within 24h.",
    )


def render_yaml(card: StrategyCard) -> str:
    payload = _card_payload(card)
    return yaml.safe_dump(payload, sort_keys=False)


def render_markdown(card: StrategyCard) -> str:
    payload = _card_payload(card)
    lines = [
        f"# {payload['token']} Unlock Pressure Card",
        "",
        f"- Pressure: {payload['pressure']}",
        f"- Unlock date: {payload['unlock_date']}",
        f"- Unlock amount: {payload['unlock_amount']:,.0f}",
        f"- Supply impact: {payload['impact']['supply_ratio_pct']:.2f}%",
        f"- Volume impact: {payload['impact']['volume_ratio_pct']:.2f}%",
        f"- Historical 5d median: {payload['history']['median_post_5d_pct']:.2f}%",
        f"- Position rule: {card.position_sizing}",
        f"- Exit rule: {card.exit_rule}",
        f"- Re-entry rule: {card.entry_rule}",
        f"- Invalidation: {card.invalidation}",
    ]
    return "\n".join(lines) + "\n"


def _reduction_for_pressure(pressure: PressureLevel, config: StrategyConfig) -> float:
    if pressure == PressureLevel.HIGH:
        return config.high_reduction_pct
    if pressure == PressureLevel.MEDIUM:
        return config.medium_reduction_pct
    return config.low_reduction_pct


def _card_payload(card: StrategyCard) -> dict[str, object]:
    reduction = _reduction_for_pressure(card.pressure, card.config)
    return {
        "token": card.event.token_symbol,
        "unlock_date": card.event.unlock_date,
        "unlock_amount": card.event.unlock_amount,
        "unlock_type": card.event.unlock_type,
        "pressure": card.pressure.value,
        "impact": {
            "supply_ratio_pct": card.impact.supply_ratio * 100,
            "volume_ratio_pct": card.impact.volume_ratio * 100,
            "unlock_value_usd": card.impact.unlock_value_usd,
        },
        "history": {
            "sample_size": card.reaction.sample_size,
            "median_pre_3d_pct": card.reaction.median_pre_3d * 100,
            "median_post_1d_pct": card.reaction.median_post_1d * 100,
            "median_post_3d_pct": card.reaction.median_post_3d * 100,
            "median_post_5d_pct": card.reaction.median_post_5d * 100,
            "median_post_7d_pct": card.reaction.median_post_7d * 100,
        },
        "strategy": {
            "position_reduction_pct": reduction,
            "pre_event_days": card.config.pre_event_days,
            "max_drawdown_stop": card.config.max_drawdown_stop,
            "entry_rule": card.entry_rule,
            "exit_rule": card.exit_rule,
            "position_sizing": card.position_sizing,
            "invalidation": card.invalidation,
        },
    }
