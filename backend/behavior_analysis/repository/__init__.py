from kit.repository.provider import repository


user_behavior_sqla_repo = repository('backend.behavior_analysis.repository.behavior_sqla:UserBehaviorSQLARepository', 'user_behavior_sqla_repo')
behavior_event_sqla_repo = repository('backend.behavior_analysis.repository.behavior_sqla:BehaviorEventSQLARepository', 'behavior_event_sqla_repo')
behavior_session_sqla_repo = repository('backend.behavior_analysis.repository.behavior_sqla:BehaviorSessionSQLARepository', 'behavior_session_sqla_repo')
behavior_funnel_sqla_repo = repository('backend.behavior_analysis.repository.behavior_sqla:BehaviorFunnelSQLARepository', 'behavior_funnel_sqla_repo')
behavior_analysis_sqla_repo = repository('backend.behavior_analysis.repository.behavior_sqla:BehaviorAnalysisSQLARepository', 'behavior_analysis_sqla_repo')


__all__ = [
    'user_behavior_sqla_repo',
    'behavior_event_sqla_repo',
    'behavior_session_sqla_repo',
    'behavior_funnel_sqla_repo',
    'behavior_analysis_sqla_repo',
]
