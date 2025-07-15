# backend/behavior_analysis/repository/behavior_sqla.py

import datetime as dt
import json
from typing import List, Dict, Any, Optional, Type, Tuple
from sqlalchemy import Column, String, Integer, DateTime, BigInteger, Text, JSON, func, and_, desc
from sqlalchemy import event
from sqlalchemy import Table
from backend.extensions import mapper_registry
from backend.behavior_analysis.domain.behavior import (
    UserBehavior, BehaviorEvent, BehaviorSession, BehaviorFunnel, BehaviorAnalysis
)
from backend.mini_core.service import shop_user_service
from kit.repository.sqla import SQLARepository
from kit.util.sqla import id_column

__all__ = [
    'UserBehaviorSQLARepository',
    'BehaviorEventSQLARepository',
    'BehaviorSessionSQLARepository',
    'BehaviorFunnelSQLARepository',
    'BehaviorAnalysisSQLARepository'
]

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
        """获取概览数据"""
        # 计算时间范围
        end_time = dt.datetime.now()
        if date_range == '1d':
            start_time = end_time - dt.timedelta(days=1)
        elif date_range == '7d':
            start_time = end_time - dt.timedelta(days=7)
        elif date_range == '30d':
            start_time = end_time - dt.timedelta(days=30)
        elif date_range == '90d':
            start_time = end_time - dt.timedelta(days=90)
        else:
            start_time = end_time - dt.timedelta(days=7)

        # 构建查询条件
        conditions = [
            UserBehavior.create_time >= start_time,
            UserBehavior.create_time <= end_time
        ]

        if user_id:
            conditions.append(UserBehavior.user_id == user_id)
        if agent_id:
            conditions.append(UserBehavior.agent_id == agent_id)
        # 基础统计
        total_events = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions)
        ).scalar() or 0

        # 用户统计
        total_users = shop_user_service.get_total_users()
        #查询t_shop_user表中的用户总数
        # 会话统计
        total_sessions = self.session.query(func.count(func.distinct(UserBehavior.session_id))).filter(
            and_(*conditions)
        ).scalar() or 0

        # 活跃用户（有多个事件的用户）
        active_users = self.session.query(func.count(func.distinct(UserBehavior.user_id))).filter(
            and_(*conditions, getattr(UserBehavior.event_type, 'in_')(['page_view', 'click', 'add_to_cart']))
        ).scalar() or 0

        # 平均会话时长（简化计算）
        avg_session_duration = 1800  # 默认30分钟

        # 跳出率（只有一个页面的会话比例）
        single_page_sessions = self.session.query(func.count(func.distinct(UserBehavior.session_id))).filter(
            and_(*conditions, UserBehavior.event_type == 'page_view')
        ).subquery()

        # 总会话数
        total_sessions_subquery = self.session.query(func.count(func.distinct(UserBehavior.session_id))).filter(
            and_(*conditions)
        ).subquery()

        bounce_rate = 0.35  # 默认35%

        # 热门事件
        top_events = self.session.query(
            UserBehavior.event_name,
            func.count(UserBehavior.id).label('count')
        ).filter(
            and_(*conditions)
        ).group_by(UserBehavior.event_name).order_by(
            desc('count')
        ).limit(10).all()

        # 热门页面
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

    def get_funnel_data(self, funnel_config: Optional[BehaviorFunnel], date_range: str, agent_id: str = None) -> Dict[str, Any]:
        """获取漏斗数据"""
        # 计算时间范围
        end_time = dt.datetime.now()
        if date_range == '1d':
            start_time = end_time - dt.timedelta(days=1)
        elif date_range == '7d':
            start_time = end_time - dt.timedelta(days=7)
        elif date_range == '30d':
            start_time = end_time - dt.timedelta(days=30)
        elif date_range == '90d':
            start_time = end_time - dt.timedelta(days=90)
        else:
            start_time = end_time - dt.timedelta(days=7)

        steps = funnel_config.steps if funnel_config else []
        funnel_data = {
            'funnel_name': funnel_config.funnel_name if funnel_config else '',
            'steps': []
        }

        previous_count = None
        for step in steps:
            event_type = step.get('event_type')
            step_name = step.get('step_name', event_type)
            # 统计该步骤的事件数量
            count = self.session.query(func.count()).filter(
                and_(
                    UserBehavior.create_time >= start_time,
                    UserBehavior.create_time <= end_time,
                    UserBehavior.agent_id == agent_id if agent_id else UserBehavior.agent_id.isnot(None),
                    UserBehavior.event_type == event_type
                )
            ).scalar() or 0

            # 计算转化率
            conversion_rate = 100.0 if previous_count is None or previous_count == 0 else (count / previous_count) * 100

            funnel_data['steps'].append({
                'step_name': step_name,
                'step_count': count,
                'conversion_rate': round(conversion_rate, 2)
            })

            previous_count = count

        # 计算总体转化率
        if funnel_data['steps']:
            first_step = funnel_data['steps'][0]['step_count']
            last_step = funnel_data['steps'][-1]['step_count']
            total_conversion_rate = (last_step / first_step * 100) if first_step > 0 else 0
            funnel_data['total_conversion_rate'] = round(total_conversion_rate, 2)

        return funnel_data

    def get_user_path_data(self, user_id: str, date_range: str) -> Dict[str, Any]:
        """获取用户路径数据"""
        # 计算时间范围
        end_time = dt.datetime.now()
        if date_range == '1d':
            start_time = end_time - dt.timedelta(days=1)
        elif date_range == '7d':
            start_time = end_time - dt.timedelta(days=7)
        elif date_range == '30d':
            start_time = end_time - dt.timedelta(days=30)
        elif date_range == '90d':
            start_time = end_time - dt.timedelta(days=90)
        else:
            start_time = end_time - dt.timedelta(days=7)

        # 获取用户的所有会话
        sessions = self.session.query(func.distinct(UserBehavior.session_id)).filter(
            and_(
                UserBehavior.user_id == user_id,
                UserBehavior.create_time >= start_time,
                UserBehavior.create_time <= end_time
            )
        ).all()

        paths = []
        for session in sessions:
            session_id = session[0]

            # 获取会话中的页面访问顺序
            page_events = self.session.query(UserBehavior.page_path).filter(
                and_(
                    UserBehavior.session_id == session_id,
                    UserBehavior.event_type == 'page_view'
                )
            ).order_by(UserBehavior.timestamp).all()

            if page_events:
                path = [event[0] for event in page_events if event[0]]
                if path:
                    paths.append(path)

        # 统计路径
        path_stats = {}
        for path in paths:
            path_key = ' -> '.join(path)
            path_stats[path_key] = path_stats.get(path_key, 0) + 1

        # 转换为列表格式
        path_list = []
        for path_str, count in path_stats.items():
            path_parts = path_str.split(' -> ')
            conversion_rate = 100.0 if len(paths) > 0 else 0
            path_list.append({
                'path': path_parts,
                'count': count,
                'conversion_rate': conversion_rate
            })

        # 按数量排序
        path_list.sort(key=lambda x: x['count'], reverse=True)

        return {
            'user_id': user_id,
            'paths': path_list[:10],  # 只返回前10个路径
            'avg_path_length': sum(len(p['path']) for p in path_list) / len(path_list) if path_list else 0,
            'most_common_entry': path_list[0]['path'][0] if path_list else '',
            'most_common_exit': path_list[0]['path'][-1] if path_list else ''
        }

    def get_product_analysis_data(self, product_id: int, date_range: str) -> Dict[str, Any]:
        """获取商品行为分析数据"""
        # 计算时间范围
        end_time = dt.datetime.now()
        if date_range == '1d':
            start_time = end_time - dt.timedelta(days=1)
        elif date_range == '7d':
            start_time = end_time - dt.timedelta(days=7)
        elif date_range == '30d':
            start_time = end_time - dt.timedelta(days=30)
        elif date_range == '90d':
            start_time = end_time - dt.timedelta(days=90)
        else:
            start_time = end_time - dt.timedelta(days=7)

        conditions = [
            UserBehavior.product_id == product_id,
            UserBehavior.create_time >= start_time,
            UserBehavior.create_time <= end_time
        ]

        # 商品浏览
        views = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'product_view')
        ).scalar() or 0

        # 商品点击
        clicks = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'product_click')
        ).scalar() or 0

        # 加入购物车
        add_to_cart = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'add_to_cart')
        ).scalar() or 0

        # 购买
        purchases = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'order_create')
        ).scalar() or 0

        # 收藏
        favorite_count = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'add_to_favorite')
        ).scalar() or 0

        # 分享
        share_count = self.session.query(func.count(UserBehavior.id)).filter(
            and_(*conditions, UserBehavior.event_type == 'page_share')
        ).scalar() or 0

        # 计算转化率
        conversion_rates = {
            'view_to_click': round((clicks / views * 100) if views > 0 else 0, 2),
            'click_to_cart': round((add_to_cart / clicks * 100) if clicks > 0 else 0, 2),
            'cart_to_purchase': round((purchases / add_to_cart * 100) if add_to_cart > 0 else 0, 2),
            'view_to_purchase': round((purchases / views * 100) if views > 0 else 0, 2)
        }

        # 平均浏览时长（简化计算）
        avg_view_duration = 45.5

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
