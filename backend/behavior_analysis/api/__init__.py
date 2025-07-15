# backend/behavior_analysis/api/__init__.py

from .v1 import behavior_v1_blp
from .v1.behavior import blp as behavior_blp

__all__ = [
    'behavior_v1_blp',
    'behavior_blp'
] 