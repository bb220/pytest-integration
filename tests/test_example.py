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
                status_response = client.get(f"/reports/{run_report_id}")
                status_response.raise_for_status()
                last_status = status_response.json().get("status")

                if last_status == "COMPLETED":
                    break

                if last_status in {"FAILED", "CANCELLED"}:
                    pytest.fail(
                        f"PromptLayer report run ended with status {last_status}"
                    )

                time.sleep(POLL_INTERVAL_SECONDS)
            else:
                pytest.fail(
                    f"Timed out waiting for PromptLayer report {run_report_id} "
                    f"to complete; last status was {last_status!r}"
                )

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
