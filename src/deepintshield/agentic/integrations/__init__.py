"""Per-framework enforcement adapters (L2).

Each module exposes a thin wrapper that gates a framework's tools through the
shared :func:`deepintshield.agentic.gate.enforce` core. They are imported
lazily by :class:`~deepintshield.agentic.surface.AgenticSurface` so a missing
framework dependency never breaks an unrelated import.
"""

__all__: list[str] = []
