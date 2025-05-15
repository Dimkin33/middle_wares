"""Пакет контроллеров для теннисного приложения."""

from .list_controllers import list_matches_controller, reset_match_controller
from .match_controllers import match_score_controller, new_match_controller
from .view_controllers import TemplateViewController

__all__ = [
    "new_match_controller",
    "match_score_controller",
    "list_matches_controller",
    "reset_match_controller",
    "TemplateViewController",
]
