"""Solution 2 — Pipeline lai Form + Free-text.

Package tự chứa, KHÔNG phụ thuộc vào artifact của hướng rule-based cũ đã bị loại.
Backend deterministic offline; mọi thành phần có interface để cắm LLM/Map API thật.
"""

from .pipeline import run

__all__ = ["run"]
