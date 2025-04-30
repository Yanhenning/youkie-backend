from enum import Enum


class SummarizationStyle(str, Enum):
    BULLET_POINTS = "bullet_points"
    BRIEF_TEXT = "brief_text"
    NORMAL = "normal"
