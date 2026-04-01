import os
import time

import httpx
import pytest


BASE_URL = "https://api.promptlayer.com"
DEFAULT_SCORE_THRESHOLD = 80.0
POLL_INTERVAL_SECONDS = 5
TIMEOUT_SECONDS = 300


def test_assert_ai_chat_quality():
    api_key = os.environ.get("PROMPTLAYER_API_KEY")
    report_id = os.environ.get("PROMPTLAYER_REPORT_ID")
    run_name = f"pytest-ai-chat-quality-{int(time.time())}"

    with httpx.Client(
        base_url=BASE_URL,
        headers={"X-API-KEY": api_key},
        timeout=30.0,
    ) as client:
        try:
            # Trigger an evaluation run for the configured report.
            run_response = client.post(
                f"/reports/{report_id}/run",
                json={"name": run_name},
            )
            run_response.raise_for_status()
            run_report_id = run_response.json().get("report_id")
            assert run_report_id, "PromptLayer run response did not include report_id"

            deadline = time.monotonic() + TIMEOUT_SECONDS
            last_status = None

            while time.monotonic() < deadline:
                # Check the evaluation run status until it completes.
                status_response = client.get(f"/reports/{run_report_id}")
                status_response.raise_for_status()
                last_status = status_response.json().get("status")

                if last_status == "COMPLETED":
                    break

                if last_status != "RUNNING":
                    pytest.fail(
                        "PromptLayer report run returned unexpected status "
                        f"{last_status!r}; expected 'RUNNING' or 'COMPLETED'"
                    )

                time.sleep(POLL_INTERVAL_SECONDS)
            else:
                pytest.fail(
                    f"Timed out waiting for PromptLayer report {run_report_id} "
                    f"to complete; last status was {last_status!r}"
                )

            # Fetch the completed evaluation run score.
            score_response = client.get(f"/reports/{run_report_id}/score")
            score_response.raise_for_status()
        except httpx.HTTPError as exc:
            pytest.fail(f"PromptLayer API request failed: {exc}")

    overall_score = score_response.json().get("score", {}).get("overall_score")

    assert isinstance(overall_score, (int, float)), (
        f"PromptLayer score response missing numeric score.overall_score: "
        f"{score_response.json()}"
    )
    assert overall_score >= DEFAULT_SCORE_THRESHOLD, (
        f"PromptLayer overall_score {overall_score} "
        f"did not meet threshold {DEFAULT_SCORE_THRESHOLD}"
    )
