# backend/behavior_analysis/repository/__init__.py

from backend.extensions import db
from .behavior_sqla import (
    UserBehaviorSQLARepository,
    BehaviorEventSQLARepository,
    BehaviorSessionSQLARepository,
    BehaviorFunnelSQLARepository,
    BehaviorAnalysisSQLARepository
)

# 创建仓储实例
user_behavior_sqla_repo = UserBehaviorSQLARepository(db.session)
behavior_event_sqla_repo = BehaviorEventSQLARepository(db.session)
behavior_session_sqla_repo = BehaviorSessionSQLARepository(db.session)
behavior_funnel_sqla_repo = BehaviorFunnelSQLARepository(db.session)
behavior_analysis_sqla_repo = BehaviorAnalysisSQLARepository(db.session)

__all__ = [
    'UserBehaviorSQLARepository',
    'BehaviorEventSQLARepository',
    'BehaviorSessionSQLARepository', 
    'BehaviorFunnelSQLARepository',
    'BehaviorAnalysisSQLARepository',
    'user_behavior_sqla_repo',
    'behavior_event_sqla_repo',
    'behavior_session_sqla_repo',
    'behavior_funnel_sqla_repo',
    'behavior_analysis_sqla_repo'
] 