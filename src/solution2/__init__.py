"""Solution 2 — Pipeline lai Form + Free-text.

Package tự chứa, KHÔNG import từ Solution 1 (src/demo/run_pipeline.py).
Backend deterministic offline; mọi thành phần có interface để cắm LLM/Map API thật.
"""

from .pipeline import run

__all__ = ["run"]
