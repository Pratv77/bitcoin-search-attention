"""Locked analysis settings.

These constants mirror ``research_protocol.md``. Do not change them after the
protocol is locked without recording a deviation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisConfig:
    primary_threshold: float = 1.00
    alternate_threshold: float = 0.70
    trailing_low_weeks: int = 52
    pre_trigger_weeks: int = 8
    post_trigger_weeks: int = 16
    event_window_weeks: int = 25
    week_ending: str = "SUN"
    currency: str = "usd"
    coin_id: str = "bitcoin"


CONFIG = AnalysisConfig()
