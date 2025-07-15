# backend/behavior_analysis/api/v1/__init__.py

from flask_smorest import Blueprint

behavior_v1_blp = Blueprint(
    '行为分析服务', 'behavior', url_prefix='/api/v1/behavior', description='行为分析服务接口'
)

from .behavior import blp as behavior_blp

behavior_v1_blp.register_blueprint(behavior_blp)

__all__ = [
    'behavior_v1_blp',
    'behavior_blp'
] 