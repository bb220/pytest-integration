# PromptLayer pytest integration

This project uses the PromptLayer API to run an evaluation as part of a pytest integration test.

1. Loads PromptLayer configuration from `.env`.
2. Triggers and polls a PromptLayer evaluation run.
3. Retrieves the final score and asserts it meets a minimum threshold.

## Getting started

Install dependencies with `uv`:

```bash
uv sync
```

Run the test suite with `uv`:

```bash
uv run pytest
```

## Quickstart
Create a local `.env` file from the example and provide your PromptLayer credentials:

```bash
cp .env.example .env
```

Set these values in `.env`:

```dotenv
PROMPTLAYER_API_KEY=your_api_key
PROMPTLAYER_REPORT_ID=your_report_id
```

These optional settings already have defaults and usually do not need to be changed:

```dotenv
PROMPTLAYER_BASE_URL=https://api.promptlayer.com
DEFAULT_SCORE_THRESHOLD=80.0
POLL_INTERVAL_SECONDS=5
TIMEOUT_SECONDS=300
```

Then run:

```bash
uv run pytest
```
