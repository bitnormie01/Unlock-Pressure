from unlock_pressure.fixtures.loader import FixtureStore
from unlock_pressure.models import TokenInfo, TokenQuote, UnlockEvent


def test_unlocks():
    store = FixtureStore()

    unlocks = store.get_unlocks()

    assert len(unlocks) >= 5
    assert all(isinstance(event, UnlockEvent) for event in unlocks)
    assert {event.token_symbol for event in unlocks} == {"TOKEN-A", "TOKEN-B", "TOKEN-C"}


def test_token_info():
    store = FixtureStore()

    info = store.get_token_info("TOKEN-A")

    assert isinstance(info, TokenInfo)
    assert info.symbol == "TOKEN-A"
    assert info.circulating_supply > 0
    assert info.total_supply >= info.circulating_supply


def test_quotes():
    store = FixtureStore()

    quotes = store.get_quotes("TOKEN-C")
    series = store.get_price_series()

    assert quotes
    assert all(isinstance(quote, TokenQuote) for quote in quotes)
    assert quotes[0].symbol == "TOKEN-C"
    assert any(row["symbol"] == "TOKEN-C" for row in series)
