#!/usr/bin/env python3

import logging
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from llm.session_recorder import SessionRecorder  # noqa: E402
from llm.dispatcher import Dispatcher  # noqa: E402


def boot() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EGC.boot")

    try:
        recorder = SessionRecorder(session_id="boot-validation")
        dispatcher = Dispatcher(recorder=recorder)
        logger.info("Dispatcher OK (project_root=%s)", dispatcher.project_root)
    except Exception as exc:
        logger.error("Dispatcher boot failed: %s", exc)
        sys.exit(1)

    provider_choice = os.environ.get("LLM_PROVIDER", "ollama")
    try:
        from llm.providers import get_provider

        provider = get_provider(provider_choice)
        logger.info("Provider OK: %s", provider.__class__.__name__)
    except Exception as exc:
        logger.warning(
            "Provider '%s' unavailable (%s). Install extras or set LLM_PROVIDER.",
            provider_choice,
            exc,
        )

    print("BOOTSTRAP VALIDATED.")


if __name__ == "__main__":
    boot()
