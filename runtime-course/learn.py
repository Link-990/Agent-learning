"""Compatibility wrapper for the Runtime course's canonical runner."""

from pathlib import Path
import runpy


CANONICAL_RUNNER = Path(__file__).resolve().parent.parent / "03-Agent-Runtime" / "learn.py"


if __name__ == "__main__":
    runpy.run_path(str(CANONICAL_RUNNER), run_name="__main__")
