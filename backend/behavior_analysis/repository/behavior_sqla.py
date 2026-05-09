# backend/behavior_analysis/repository/behavior_sqla.py

import datetime as dt
import json
from typing import List, Dict, Any, Optional, Type, Tuple
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Text, JSON, func, and_, desc, case
from sqlalchemy import event
from sqlalchemy import Table
from backend.extensions import mapper_registry
from backend.behavior_analysis.domain.behavior import (
    UserBehavior, BehaviorEvent, BehaviorSession, BehaviorFunnel, BehaviorAnalysis
)
from backend.mini_core.service import shop_user_service
from backend.mini_core.service.distribution_server import DistributionService, DistributionSQLARepository
from kit.repository.sqla import SQLARepository
from kit.util.sqla import id_column

__all__ = [
    'UserBehaviorSQLARepository',
    'BehaviorEventSQLARepository',
    'BehaviorSessionSQLARepository',
    'BehaviorFunnelSQLARepository',
    'BehaviorAnalysisSQLARepository'
]

# ============================================================
# 索引建议（按优先级排列，建议在数据库手动执行）：
#
# 1. (create_time, event_type) 复合索引
#    CREATE INDEX idx_ub_create_event ON t_user_behavior(create_time, event_type);
#    → 加速 overview 时间+事件聚合、funnel 漏斗各步骤计数、product-analysis 时间+事件过滤
#
# 2. (product_id, create_time) 复合索引
#    CREATE INDEX idx_ub_product_create ON t_user_behavior(product_id, create_time);
#    → 加速 product-analysis 按商品+时间的过滤，避免全表扫描
#
# 3. (user_id, create_time) 复合索引
#    CREATE INDEX idx_ub_user_create ON t_user_behavior(user_id, create_time);
#    → 加速 user-path 按用户+时间的过滤，overview 按用户过滤
#
# 4. (session_id, event_type, timestamp) 复合索引
#    CREATE INDEX idx_ub_session_event_ts ON t_user_behavior(session_id, event_type, timestamp);
#    → 加速 user-path 按会话获取页面访问顺序的排序查询
#
# 现有单列索引 (user_id, agent_id, session_id, event_type, product_id,
# timestamp, create_time) 在复合索引建立后可能冗余，建议通过
# EXPLAIN 分析后按需保留或清理。
# ============================================================

# 用户行为记录表
user_behavior_table = Table(
    't_user_behavior',
    mapper_registry.metadata,
    id_column(),
    Column('user_id', String(64), nullable=False, index=True, comment='用户ID'),
    Column('agent_id', String(64), nullable=False, index=True, comment='推荐人ID'),
    Column('session_id', String(64), nullable=False, index=True, comment='会话ID'),
    Column('event_type', String(50), nullable=False, index=True, comment='事件类型'),
    Column('event_name', String(100), nullable=False, comment='事件名称'),
    Column('page_path', String(200), comment='页面路径'),
    Column('element_id', String(100), comment='元素ID'),
    Column('product_id', BigInteger, index=True, comment='商品ID'),
    Column('order_id', String(64), comment='订单ID'),
    Column('properties', JSON, comment='事件属性(JSON格式)'),
    Column('device_info', JSON, comment='设备信息'),
    Column('location_info', JSON, comment='位置信息'),
    Column('timestamp', BigInteger, nullable=False, index=True, comment='事件时间戳'),
    Column('ip_address', String(45), comment='IP地址'),
    Column('user_agent', Text, comment='用户代理'),
    Column('create_time', DateTime, default=dt.datetime.now, index=True),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
)

# 行为事件定义表
behavior_event_table = Table(
    't_behavior_event',
    mapper_registry.metadata,
    id_column(),
    Column('event_code', String(50), unique=True, nullable=False, index=True, comment='事件代码'),
    Column('event_name', String(100), nullable=False, comment='事件名称'),
    Column('event_category', String(50), nullable=False, index=True, comment='事件分类'),
    Column('description', Text, comment='事件描述'),
    Column('properties_schema', JSON, comment='属性模式定义'),
    Column('is_active', Integer, default=1, comment='是否启用'),
    Column('create_time', DateTime, default=dt.datetime.now),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
)

# 用户会话表
behavior_session_table = Table(
    't_behavior_session',
    mapper_registry.metadata,
    id_column(),
    Column('session_id', String(64), unique=True, nullable=False, index=True, comment='会话ID'),
    Column('user_id', String(64), nullable=False, index=True, comment='用户ID'),
    Column('start_time', DateTime, nullable=False, index=True, comment='会话开始时间'),
    Column('end_time', DateTime, comment='会话结束时间'),
    Column('duration', Integer, comment='会话时长(秒)'),
    Column('page_count', Integer, default=0, comment='访问页面数'),
    Column('event_count', Integer, default=0, comment='事件数量'),
    Column('device_info', JSON, comment='设备信息'),
    Column('location_info', JSON, comment='位置信息'),
    Column('create_time', DateTime, default=dt.datetime.now),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
)

# 转化漏斗配置表
behavior_funnel_table = Table(
    't_behavior_funnel',
    mapper_registry.metadata,
    id_column(),
    Column('funnel_name', String(100), nullable=False, comment='漏斗名称'),
    Column('funnel_code', String(50), unique=True, nullable=False, index=True, comment='漏斗代码'),
    Column('description', Text, comment='漏斗描述'),
    Column('steps', JSON, nullable=False, comment='漏斗步骤配置'),
    Column('time_window', Integer, default=86400, comment='时间窗口(秒)'),
    Column('is_active', Integer, default=1, comment='是否启用'),
    Column('create_time', DateTime, default=dt.datetime.now),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
)

# 行为分析结果表
behavior_analysis_table = Table(
    't_behavior_analysis',
    mapper_registry.metadata,
    id_column(),
    Column('analysis_type', String(50), nullable=False, index=True, comment='分析类型'),
    Column('analysis_name', String(100), nullable=False, comment='分析名称'),
    Column('date_range', String(20), nullable=False, index=True, comment='日期范围'),
    Column('data', JSON, nullable=False, comment='分析结果数据'),
    Column('summary', Text, comment='分析摘要'),
    Column('create_time', DateTime, default=dt.datetime.now, index=True),
)

# 映射关系
mapper_registry.map_imperatively(UserBehavior, user_behavior_table)
mapper_registry.map_imperatively(BehaviorEvent, behavior_event_table)
mapper_registry.map_imperatively(BehaviorSession, behavior_session_table)
mapper_registry.map_imperatively(BehaviorFunnel, behavior_funnel_table)
mapper_registry.map_imperatively(BehaviorAnalysis, behavior_analysis_table)


def _parse_date_range(date_range: str) -> Tuple[dt.datetime, dt.datetime]:
    """将 date_range 字符串解析为 (start_time, end_time)"""
    end_time = dt.datetime.now()
    days = {'1d': 1, '7d': 7, '30d': 30, '90d': 90}
    start_time = end_time - dt.timedelta(days=days.get(date_range, 7))
    return start_time, end_time


class UserBehaviorSQLARepository(SQLARepository):
    """用户行为记录仓储"""

    @property
    def model(self) -> Type[UserBehavior]:
        return UserBehavior

    @property
    def query_params(self) -> Tuple:
        return 'user_id', 'session_id', 'event_type', 'product_id', 'order_id'

    @property
    def range_query_params(self) -> Tuple:
        return 'timestamp', 'create_time'

    def get_overview_data(self, date_range: str, user_id: Optional[str] = None, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """获取概览数据——聚合下推到 SQL，减少扫描次数"""
        start_time, end_time = _parse_date_range(date_range)

        conditions = [
            UserBehavior.create_time >= start_time,
            UserBehavior.create_time <= end_time
        ]
        if user_id:
            conditions.append(UserBehavior.user_id == user_id)
        if agent_id:
            conditions.append(UserBehavior.agent_id == agent_id)

        # 一次扫描完成：总事件、总会话、活跃用户
        main_stats = self.session.query(
            func.count(UserBehavior.id).label('total_events'),
            func.count(func.distinct(UserBehavior.session_id)).label('total_sessions'),
            func.count(func.distinct(
                case(
                    (UserBehavior.event_type.in_(['page_view', 'click', 'add_to_cart']), UserBehavior.user_id),
                    else_=None
                )
            )).label('active_users')
        ).filter(and_(*conditions)).first()

        total_events = main_stats.total_events or 0
        total_sessions = main_stats.total_sessions or 0
        active_users = main_stats.active_users or 0

        # 用户总数——外部服务（全量注册用户）
        if agent_id:
            distribution_service = DistributionService(DistributionSQLARepository(session=self.session))
            total_users = distribution_service.get_total_by_agent_id(agent_id)
        else:
            total_users = shop_user_service.get_total_users()

        # 跳出率：仅含 page_view 事件的会话占比（单次 GROUP BY + HAVING）
        bounce_subq = self.session.query(UserBehavior.session_id).filter(
            and_(*conditions)
        ).group_by(UserBehavior.session_id).having(
            and_(
                func.count(func.distinct(UserBehavior.event_type)) == 1,
                func.max(UserBehavior.event_type) == 'page_view'
            )
        ).subquery()
        bounce_sessions = self.session.query(func.count()).select_from(bounce_subq).scalar() or 0
        bounce_rate = round((bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2)

        # 平均会话时长——从 t_behavior_session 取真实值
        avg_duration_result = self.session.query(
            func.avg(BehaviorSession.duration)
        ).filter(
            and_(
                BehaviorSession.start_time >= start_time,
                BehaviorSession.start_time <= end_time
            )
        ).scalar()
        avg_session_duration = round(avg_duration_result) if avg_duration_result else 0

        # 热门事件 TOP10（GROUP BY 已在 SQL 侧）
        top_events = self.session.query(
            UserBehavior.event_name,
            func.count(UserBehavior.id).label('count')
        ).filter(and_(*conditions)).group_by(UserBehavior.event_name).order_by(
            desc('count')
        ).limit(10).all()

        # 热门页面 TOP10
        top_pages = self.session.query(
            UserBehavior.page_path,
            func.count(UserBehavior.id).label('views')
        ).filter(
            and_(*conditions, UserBehavior.event_type == 'page_view')
        ).group_by(UserBehavior.page_path).order_by(
            desc('views')
        ).limit(10).all()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_sessions': total_sessions,
            'total_events': total_events,
            'avg_session_duration': avg_session_duration,
            'bounce_rate': bounce_rate,
            'top_events': [{'event_type': e[0], 'count': e[1]} for e in top_events],
            'top_pages': [{'page_path': p[0], 'views': p[1]} for p in top_pages]
        }

    def get_funnel_config(self, funnel_id: str) -> Optional[BehaviorFunnel]:
        """获取漏斗配置"""
        return self.session.query(BehaviorFunnel).filter(BehaviorFunnel.funnel_code == funnel_id).first()

    def get_funnel_data(self, funnel_config: Optional[BehaviorFunnel], date_range: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """获取漏斗数据——单次扫描，CASE WHEN 条件聚合替代逐步骤 COUNT"""
        start_time, end_time = _parse_date_range(date_range)
        steps = funnel_config.steps if funnel_config else []

        funnel_data: Dict[str, Any] = {
            'funnel_name': funnel_config.funnel_name if funnel_config else '',
            'steps': []
        }

        if not steps:
            funnel_data['total_conversion_rate'] = 0
            return funnel_data

        base_conditions = [
            UserBehavior.create_time >= start_time,
            UserBehavior.create_time <= end_time
        ]
        if agent_id:
            base_conditions.append(UserBehavior.agent_id == agent_id)

        # 一次扫描，对每个步骤用 CASE WHEN 分别计数
        step_exprs = []
        step_names: List[str] = []
        for step in steps:
            event_type = step.get('event_type')
            step_name = step.get('step_name', event_type)
            step_names.append(step_name)
            step_exprs.append(
                func.sum(case((UserBehavior.event_type == event_type, 1), else_=0)).label(step_name)
            )

        row = self.session.query(*step_exprs).filter(and_(*base_conditions)).first()
        counts = [(row[i] or 0) for i in range(len(step_names))]

        for i, (step, step_name) in enumerate(zip(steps, step_names)):
            count = counts[i]
            previous_count = counts[i - 1] if i > 0 else None
            conversion_rate = 100.0 if previous_count is None or previous_count == 0 else (count / previous_count) * 100
            funnel_data['steps'].append({
                'step_name': step_name,
                'step_count': count,
                'conversion_rate': round(conversion_rate, 2)
            })

        # 总体转化率
        if funnel_data['steps']:
            first_step = funnel_data['steps'][0]['step_count']
            last_step = funnel_data['steps'][-1]['step_count']
            total_conversion_rate = (last_step / first_step * 100) if first_step > 0 else 0
            funnel_data['total_conversion_rate'] = round(total_conversion_rate, 2)
        else:
            funnel_data['total_conversion_rate'] = 0

        return funnel_data

    def get_user_path_data(self, user_id: str, date_range: str) -> Dict[str, Any]:
        """获取用户路径数据——单次查询替代 N+1，Python 侧按会话分组"""
        start_time, end_time = _parse_date_range(date_range)

        # 一次查询获取该用户所有 page_view 事件，按 session + 时间排序
        rows = self.session.query(
            UserBehavior.session_id,
            UserBehavior.page_path
        ).filter(
            and_(
                UserBehavior.user_id == user_id,
                UserBehavior.create_time >= start_time,
                UserBehavior.create_time <= end_time,
                UserBehavior.event_type == 'page_view'
            )
        ).order_by(UserBehavior.session_id, UserBehavior.timestamp).all()

        # 按 session 分组构建路径
        paths: List[List[str]] = []
        current_session = None
        current_path: List[str] = []
        for row in rows:
            sid, page = row
            if sid != current_session:
                if current_path:
                    paths.append(current_path)
                current_session = sid
                current_path = []
            if page:
                current_path.append(page)
        if current_path:
            paths.append(current_path)

        # 路径频次统计
        path_stats: Dict[str, int] = {}
        for path in paths:
            path_key = ' -> '.join(path)
            path_stats[path_key] = path_stats.get(path_key, 0) + 1

        total_paths = len(paths)
        path_list: List[Dict[str, Any]] = []
        for path_str, count in path_stats.items():
            path_parts = path_str.split(' -> ')
            conversion_rate = round((count / total_paths * 100), 2) if total_paths > 0 else 0
            path_list.append({
                'path': path_parts,
                'count': count,
                'conversion_rate': conversion_rate
            })

        path_list.sort(key=lambda x: x['count'], reverse=True)
        top_paths = path_list[:10]

        return {
            'user_id': user_id,
            'paths': top_paths,
            'avg_path_length': sum(len(p['path']) for p in top_paths) / len(top_paths) if top_paths else 0,
            'most_common_entry': top_paths[0]['path'][0] if top_paths else '',
            'most_common_exit': top_paths[0]['path'][-1] if top_paths else ''
        }

    def get_product_analysis_data(self, product_id: int, date_range: str) -> Dict[str, Any]:
        """获取商品行为分析数据——单次扫描，CASE WHEN 条件聚合替代 6 次 COUNT"""
        start_time, end_time = _parse_date_range(date_range)

        conditions = [
            UserBehavior.product_id == product_id,
            UserBehavior.create_time >= start_time,
            UserBehavior.create_time <= end_time
        ]

        # 一次扫描完成 6 种事件计数
        stats = self.session.query(
            func.sum(case((UserBehavior.event_type == 'product_view', 1), else_=0)).label('views'),
            func.sum(case((UserBehavior.event_type == 'product_click', 1), else_=0)).label('clicks'),
            func.sum(case((UserBehavior.event_type == 'add_to_cart', 1), else_=0)).label('add_to_cart'),
            func.sum(case((UserBehavior.event_type == 'order_create', 1), else_=0)).label('purchases'),
            func.sum(case((UserBehavior.event_type == 'add_to_favorite', 1), else_=0)).label('favorite_count'),
            func.sum(case((UserBehavior.event_type == 'page_share', 1), else_=0)).label('share_count'),
        ).filter(and_(*conditions)).first()

        views = stats.views or 0
        clicks = stats.clicks or 0
        add_to_cart = stats.add_to_cart or 0
        purchases = stats.purchases or 0
        favorite_count = stats.favorite_count or 0
        share_count = stats.share_count or 0

        conversion_rates = {
            'view_to_click': round((clicks / views * 100) if views > 0 else 0, 2),
            'click_to_cart': round((add_to_cart / clicks * 100) if clicks > 0 else 0, 2),
            'cart_to_purchase': round((purchases / add_to_cart * 100) if add_to_cart > 0 else 0, 2),
            'view_to_purchase': round((purchases / views * 100) if views > 0 else 0, 2)
        }

        # 平均浏览时长——从会话表取真实数据
        avg_duration_result = self.session.query(
            func.avg(BehaviorSession.duration)
        ).filter(
            and_(
                BehaviorSession.start_time >= start_time,
                BehaviorSession.start_time <= end_time,
                BehaviorSession.session_id.in_(
                    self.session.query(UserBehavior.session_id).filter(
                        and_(*conditions, UserBehavior.event_type == 'product_view')
                    ).subquery()
                )
            )
        ).scalar()
        avg_view_duration = round(avg_duration_result, 2) if avg_duration_result else 0

        return {
            'product_id': product_id,
            'product_name': f'商品{product_id}',
            'views': views,
            'clicks': clicks,
            'add_to_cart': add_to_cart,
            'purchases': purchases,
            'conversion_rates': conversion_rates,
            'avg_view_duration': avg_view_duration,
            'favorite_count': favorite_count,
            'share_count': share_count
        }


class BehaviorEventSQLARepository(SQLARepository):
    """行为事件定义仓储"""

    @property
    def model(self) -> Type[BehaviorEvent]:
        return BehaviorEvent

    @property
    def query_params(self) -> Tuple:
        return 'event_code', 'event_category', 'is_active'


class BehaviorSessionSQLARepository(SQLARepository):
    """用户会话仓储"""

    @property
    def model(self) -> Type[BehaviorSession]:
        return BehaviorSession

    @property
    def query_params(self) -> Tuple:
        return 'session_id', 'user_id'


class BehaviorFunnelSQLARepository(SQLARepository):
    """转化漏斗配置仓储"""

    @property
    def model(self) -> Type[BehaviorFunnel]:
        return BehaviorFunnel

    @property
    def query_params(self) -> Tuple:
        return 'funnel_code', 'is_active'


class BehaviorAnalysisSQLARepository(SQLARepository):
    """行为分析结果仓储"""

    @property
    def model(self) -> Type[BehaviorAnalysis]:
        return BehaviorAnalysis

    @property
    def query_params(self) -> Tuple:
        return 'analysis_type', 'date_range'
