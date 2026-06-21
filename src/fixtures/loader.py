from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from unlock_pressure.models import TokenInfo, TokenQuote, UnlockEvent


class FixtureStore:
    def __init__(self, fixture_dir: Path | None = None) -> None:
        self.fixture_dir = fixture_dir or Path(__file__).resolve().parents[2] / "fixtures"

    def get_unlocks(self) -> list[UnlockEvent]:
        rows = self._read_json("unlocks.json")
        return [
            UnlockEvent(
                token_symbol=str(row["token_symbol"]),
                unlock_date=str(row["unlock_date"]),
                unlock_amount=float(row["unlock_amount"]),
                unlock_type=str(row["unlock_type"]),
            )
            for row in rows
        ]

    def get_token_info(self, symbol: str) -> TokenInfo:
        rows = self._read_json("token_info.json")
        row = rows[symbol]
        return TokenInfo(
            symbol=str(row["symbol"]),
            circulating_supply=float(row["circulating_supply"]),
            total_supply=float(row["total_supply"]),
        )

    def get_quotes(self, symbol: str) -> list[TokenQuote]:
        rows = self._read_json("quotes.json")
        latest = rows["latest"][symbol]
        return [
            TokenQuote(
                symbol=str(latest["symbol"]),
                price=float(latest["price"]),
                volume_24h=float(latest["volume_24h"]),
                market_cap=float(latest["market_cap"]),
            )
        ]

    def get_price_series(self) -> list[dict[str, Any]]:
        rows = self._read_json("quotes.json")
        return list(rows["price_series"])

    def _read_json(self, filename: str) -> Any:
        return json.loads((self.fixture_dir / filename).read_text(encoding="utf-8"))
