# backend/behavior_analysis/service/behavior_service.py

import datetime as dt
from typing import Dict, Any, Optional
from flask import g

from kit.service.base import CRUDService
from backend.behavior_analysis.domain.behavior import UserBehavior
from backend.behavior_analysis.repository.behavior_sqla import UserBehaviorSQLARepository


class BehaviorService(CRUDService[UserBehavior]):
    """行为数据服务"""

    def __init__(self, repo: UserBehaviorSQLARepository):
        super().__init__(repo)
        self._repo = repo

    def track_event(self, event_data: dict) -> dict:
        """记录行为事件"""
        try:
            # 获取客户端IP
            ip_address = None
            if hasattr(g, 'ip'):
                ip_address = g.ip

            # 获取用户代理
            user_agent = None
            if hasattr(g, 'request'):
                user_agent = g.request.headers.get('User-Agent')

            # 创建行为记录
            behavior = UserBehavior(
                user_id=event_data.get('user_id'),
                agent_id=event_data.get('agent_id'),
                session_id=event_data.get('session_id'),
                event_type=event_data.get('event_type'),
                event_name=event_data.get('event_name'),
                page_path=event_data.get('page_path'),
                element_id=event_data.get('element_id'),
                product_id=event_data.get('product_id'),
                order_id=event_data.get('order_id'),
                properties=event_data.get('properties'),
                device_info=event_data.get('device_info'),
                location_info=event_data.get('location_info'),
                timestamp=event_data.get('timestamp'),
                ip_address=ip_address,
                user_agent=user_agent
            )

            # 保存到数据库
            result = self.create(behavior)

            return {
                'code': 200,
                'message': '数据上报成功',
                'data': {
                    'track_id': result.id
                }
            }

        except Exception as e:
            return {
                'code': 500,
                'message': f'数据上报失败: {str(e)}',
                'data': None
            }

    def get_overview_data(self, date_range: str, user_id: str = None, agent_id: str = None) -> dict:
        """获取概览数据"""
        try:
            data = self._repo.get_overview_data(date_range, user_id, agent_id)
            return {
                'code': 200,
                'data': data
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取概览数据失败: {str(e)}',
                'data': None
            }

    def get_funnel_analysis(self, funnel_id: str, date_range: str, agent_id: str = None) -> dict:
        """获取漏斗分析"""
        try:
            # 这里应该从配置中获取漏斗定义
            # 暂时使用硬编码的漏斗配置
            # funnel_config = {
            #     'funnel_name': '商品购买漏斗',
            #     'steps': [
            #         {'event_type': 'product_view', 'step_name': '商品浏览'},
            #         {'event_type': 'add_to_cart', 'step_name': '加入购物车'},
            #         {'event_type': 'order_create', 'step_name': '创建订单'},
            #         {'event_type': 'order_pay', 'step_name': '完成支付'}
            #     ]
            # }
            # 从数据库中获取漏斗配置
            funnel_config = self._repo.get_funnel_config(funnel_id)

            data = self._repo.get_funnel_data(funnel_config, date_range, agent_id)
            return {
                'code': 200,
                'data': data
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取漏斗分析失败: {str(e)}',
                'data': None
            }

    def get_user_path_analysis(self, user_id: str, date_range: str) -> dict:
        """获取用户路径分析"""
        try:
            data = self._repo.get_user_path_data(user_id, date_range)
            return {
                'code': 200,
                'data': data
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取用户路径分析失败: {str(e)}',
                'data': None
            }

    def get_product_analysis(self, product_id: int, date_range: str) -> dict:
        """获取商品行为分析"""
        try:
            data = self._repo.get_product_analysis_data(product_id, date_range)
            return {
                'code': 200,
                'data': data
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取商品行为分析失败: {str(e)}',
                'data': None
            }

    def get_user_portrait(self, user_id: str) -> dict:
        """获取用户画像"""
        try:
            # 获取用户基本信息
            basic_info = self._get_user_basic_info(user_id)

            # 获取行为模式
            behavior_patterns = self._get_user_behavior_patterns(user_id)

            # 获取商品偏好
            product_preferences = self._get_user_product_preferences(user_id)

            # 获取购买行为
            purchase_behavior = self._get_user_purchase_behavior(user_id)

            # 计算活跃度等级
            engagement_level = self._calculate_engagement_level(user_id)

            data = {
                'user_id': user_id,
                'basic_info': basic_info,
                'behavior_patterns': behavior_patterns,
                'product_preferences': product_preferences,
                'purchase_behavior': purchase_behavior,
                'engagement_level': engagement_level
            }

            return {
                'code': 200,
                'data': data
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取用户画像失败: {str(e)}',
                'data': None
            }

    def _get_user_basic_info(self, user_id: str) -> dict:
        """获取用户基本信息"""
        # 这里应该从用户表获取信息
        # 暂时返回模拟数据
        return {
            'register_time': '2024-01-01',
            'last_active': dt.datetime.now().strftime('%Y-%m-%d'),
            'total_sessions': 25,
            'total_events': 156
        }

    def _get_user_behavior_patterns(self, user_id: str) -> dict:
        """获取用户行为模式"""
        # 这里应该分析用户的行为模式
        # 暂时返回模拟数据
        return {
            'preferred_time': '20:00-22:00',
            'preferred_day': '周末',
            'avg_session_duration': 1800,
            'bounce_rate': 0.2
        }

    def _get_user_product_preferences(self, user_id: str) -> dict:
        """获取用户商品偏好"""
        # 这里应该分析用户的商品偏好
        # 暂时返回模拟数据
        return {
            'favorite_categories': ['数码', '服装'],
            'price_range': '100-500',
            'brand_preferences': ['品牌A', '品牌B']
        }

    def _get_user_purchase_behavior(self, user_id: str) -> dict:
        """获取用户购买行为"""
        # 这里应该分析用户的购买行为
        # 暂时返回模拟数据
        return {
            'total_orders': 8,
            'total_amount': 2500.0,
            'avg_order_value': 312.5,
            'purchase_frequency': '每周1次'
        }

    def _calculate_engagement_level(self, user_id: str) -> str:
        """计算用户活跃度等级"""
        # 这里应该根据用户行为计算活跃度
        # 暂时返回模拟数据
        return '高活跃用户'
