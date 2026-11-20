"""A safe switch used only to demonstrate Jenkins' failed-build behavior."""

import os

import pytest


def test_controlled_failure_switch():
    """Pass normally; fail deliberately when the Jenkins parameter is enabled."""
    inject_failure = os.getenv("INJECT_TEST_FAILURE", "false").strip().lower()
    if inject_failure in {"1", "true", "yes", "on"}:
        pytest.fail("Intentional controlled failure: INJECT_TEST_FAILURE is enabled")
