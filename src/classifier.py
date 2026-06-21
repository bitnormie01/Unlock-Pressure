from __future__ import annotations

from unlock_pressure.models import PressureLevel


def classify_pressure(supply_ratio: float, volume_ratio: float) -> PressureLevel:
    if supply_ratio > 0.05 or volume_ratio > 2.0:
        return PressureLevel.HIGH
    if supply_ratio > 0.02 or volume_ratio > 0.5:
        return PressureLevel.MEDIUM
    return PressureLevel.LOW
