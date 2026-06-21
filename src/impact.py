from __future__ import annotations


def compute_supply_impact(unlock_amount: float, circulating_supply: float) -> float:
    if circulating_supply <= 0:
        return 0.0
    return unlock_amount / circulating_supply


def compute_volume_impact(
    unlock_amount: float, price: float, daily_volume_usd: float
) -> float:
    if daily_volume_usd <= 0 or price <= 0:
        return 0.0
    return (unlock_amount * price) / daily_volume_usd
