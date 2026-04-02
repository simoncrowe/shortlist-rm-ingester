# shortlist-rm-ingester

A Python ingestion service that scrapes property rental listings from a major UK property portal and forwards structured data to a downstream [runner](https://github.com/simoncrowe/shortlist-runner) service for further processing.

Part of the [Shortlist](https://github.com/simoncrowe?tab=repositories&q=shortlist) project.

## How it works

The ingester extracts listing data from search result pages, parses individual property pages into structured profiles (description, price, location, URL), and deduplicates using Redis. New listings are POSTed to a configurable runner endpoint.

Key design choices:
- Generator-based streaming for memory-efficient processing
- Protocol-based abstraction over the deduplication store
- User-agent rotation and randomised request delays
- Structured JSON logging via structlog

## Usage

The CLI has three commands:

```bash
# Scrape listings and send to the runner service
python -m rm_ingester ingest <results_url> <runner_url>

# Scrape and record listings to Redis (useful for testing)
python -m rm_ingester record <results_url>

# Replay recorded listings to the runner
python -m rm_ingester replay <runner_url>
```

Options:
- `--redis-host` (default: `127.0.0.1`)
- `--redis-pass`

## Development

Requires [Poetry](https://python-poetry.org/).

```bash
poetry install
poetry run pytest
```

Linting and type checking run via pre-commit hooks (flake8, mypy, isort, cspell).

## License

MIT
