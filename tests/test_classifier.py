from unlock_pressure.classifier import classify_pressure
from unlock_pressure.models import PressureLevel


def test_high_supply():
    assert classify_pressure(0.051, 0.1) == PressureLevel.HIGH


def test_high_volume():
    assert classify_pressure(0.01, 2.01) == PressureLevel.HIGH


def test_medium():
    assert classify_pressure(0.021, 0.1) == PressureLevel.MEDIUM
    assert classify_pressure(0.01, 0.51) == PressureLevel.MEDIUM


def test_low():
    assert classify_pressure(0.02, 0.5) == PressureLevel.LOW
