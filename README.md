# Unlock Pressure

Unlock Pressure is a Track 2 Strategy Skill for spotting token unlock events that may create near-term sell pressure. It is fixture-backed: the CLI reads local unlock schedules, token supply, quote, volume, and historical price-path evidence; classifies the pressure level; emits a reviewable strategy card; and replays the top event against fixture prices.

The sample run surfaces `TOKEN-A` on `2026-06-25` as a `HIGH` pressure investor unlock: 60,000,000 tokens, 12.00% of circulating supply, 300.00% of 24h volume, and a fixture median 5-day post-unlock reaction of -12.00%.

## Track 2 Fit

This project fits Track 2 because it turns market evidence into an explicit, inspectable strategy artifact instead of an opaque signal. Judges can see the inputs, the pressure thresholds, the generated action rules, and the fixture-backed backtest result.

The strategy card includes:

- Pressure level: `LOW`, `MEDIUM`, or `HIGH`.
- Impact metrics: supply ratio, volume ratio, and unlock value in USD.
- Historical reaction: median pre/post unlock returns for matching pressure events.
- Risk action: reduce spot exposure 3 days before the unlock.
- Position sizing: 50% reduction for `HIGH`, 25% for `MEDIUM`, 0% for `LOW`.
- Re-entry and invalidation rules: volume/range normalization for re-entry and absorption within 24h for invalidation.
- Backtest summary: fixture capital preserved, drawdown with and without the strategy, equity curve, and trade row.

## Evidence Inputs

All evidence is local and reproducible:

- `fixtures/unlocks.json` contains 10 unlock events across `TOKEN-A`, `TOKEN-B`, and `TOKEN-C`.
- `fixtures/token_info.json` contains circulating and total supply for each token.
- `fixtures/quotes.json` contains latest price, 24h volume, market cap, and historical price paths around unlock dates.

Pressure classification is intentionally simple and auditable:

- `HIGH` when unlock size is greater than 5% of circulating supply or greater than 2x 24h volume.
- `MEDIUM` when unlock size is greater than 2% of circulating supply or greater than 0.5x 24h volume.
- `LOW` otherwise.

## Quick Start

From `07-unlock-pressure`:

```bash
python -m pip install -e ".[dev]"
python -m unlock_pressure run --mode fixture --min-pressure low --output-dir outputs
python -m pytest tests -v
```

Useful filters:

```bash
python -m unlock_pressure run --mode fixture --min-pressure medium --output-dir outputs
python -m unlock_pressure run --mode fixture --min-pressure high --output-dir outputs
```

Fixture mode requires no credentials and makes no network calls.

## Generated Outputs

The fixture command writes:

- `outputs/strategy-card.yaml`
- `outputs/strategy-card.md`

The checked-in sample output is a `TOKEN-A` `HIGH` pressure card with:

- 12.00% supply impact.
- 300.00% volume impact.
- 60,000,000 USD unlock value.
- Historical sample size of 3 matching high-pressure events.
- 50% spot exposure reduction before the event.
- Re-entry and invalidation rules rendered in both YAML and Markdown.

## Project Map

- `src/__main__.py` wires the CLI, fixture scan, output writing, and live-mode boundary.
- `src/fixtures/loader.py` loads unlock, token info, quote, and price-path fixtures.
- `src/impact.py` computes supply and volume impact with zero-value guards.
- `src/classifier.py` maps impact ratios to `LOW`, `MEDIUM`, and `HIGH`.
- `src/emitter.py` builds the strategy card and renders YAML/Markdown.
- `src/backtest.py` replays the exposure-reduction rule against fixture prices.
- `src/models.py` defines the typed dataclasses used across the pipeline.
- `fixtures/` stores the evidence inputs.
- `outputs/` stores reproducible sample strategy cards.
- `tests/` covers loaders, impact math, classification, card rendering, CLI output, backtest, and the full pipeline.

## Verification

Run the full test suite from `07-unlock-pressure`:

```bash
python -m pytest tests -v
```

The tests assert fixture loading, pressure thresholds, YAML parseability, CLI generation of both output files, positive capital-preservation behavior, and end-to-end pipeline behavior.

## Safety And Live Mode Boundary

- No live trading.
- No wallet execution.
- No orders, swaps, transfers, private keys, or transaction signing.
- No capital is required.
- Fixture mode is the supported review path and works without credentials.
- The CLI accepts `--mode live`, but it exits early with a message that optional CMC credentials would be required. No CMC client or live data path is implemented in this project.
