from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PressureLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class UnlockEvent:
    token_symbol: str
    unlock_date: str
    unlock_amount: float
    unlock_type: str


@dataclass(frozen=True)
class TokenInfo:
    symbol: str
    circulating_supply: float
    total_supply: float


@dataclass(frozen=True)
class TokenQuote:
    symbol: str
    price: float
    volume_24h: float
    market_cap: float


@dataclass(frozen=True)
class ImpactResult:
    supply_ratio: float
    volume_ratio: float
    unlock_value_usd: float


@dataclass(frozen=True)
class ReactionProfile:
    pressure_level: PressureLevel
    sample_size: int
    median_pre_3d: float
    median_post_1d: float
    median_post_3d: float
    median_post_5d: float
    median_post_7d: float


@dataclass(frozen=True)
class StrategyConfig:
    high_reduction_pct: float = 0.50
    medium_reduction_pct: float = 0.25
    low_reduction_pct: float = 0.0
    pre_event_days: int = 3
    max_drawdown_stop: float = -0.15


@dataclass(frozen=True)
class StrategyCard:
    event: UnlockEvent
    impact: ImpactResult
    pressure: PressureLevel
    reaction: ReactionProfile
    config: StrategyConfig
    entry_rule: str
    exit_rule: str
    position_sizing: str
    invalidation: str


@dataclass(frozen=True)
class BacktestResult:
    capital_preserved_pct: float
    max_drawdown_with: float
    max_drawdown_without: float
    equity_curve: list[dict[str, float | str]] = field(default_factory=list)
    trades: list[dict[str, float | str]] = field(default_factory=list)
