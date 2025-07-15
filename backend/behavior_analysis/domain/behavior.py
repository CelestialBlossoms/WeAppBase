# backend/behavior_analysis/domain/behavior.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from marshmallow_dataclass import dataclass as ma_dataclass

from kit.domain.entity import Entity


@ma_dataclass
class UserBehavior(Entity):
    """用户行为记录领域模型"""

    user_id: str = field(
        default=None,
        metadata=dict(
            description='用户ID',
        ),
    )
    agent_id: str = field(
        default=None,
        metadata=dict(
            description='推荐人ID',
        ),
    )
    session_id: str = field(
        default=None,
        metadata=dict(
            description='会话ID',
        ),
    )

    event_type: str = field(
        default=None,
        metadata=dict(
            description='事件类型',
        ),
    )

    event_name: str = field(
        default=None,
        metadata=dict(
            description='事件名称',
        ),
    )

    page_path: Optional[str] = field(
        default=None,
        metadata=dict(
            description='页面路径',
        ),
    )

    element_id: Optional[str] = field(
        default=None,
        metadata=dict(
            description='元素ID',
        ),
    )

    product_id: Optional[int] = field(
        default=None,
        metadata=dict(
            description='商品ID',
        ),
    )

    order_id: Optional[str] = field(
        default=None,
        metadata=dict(
            description='订单ID',
        ),
    )

    properties: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='事件属性(JSON格式)',
        ),
    )

    device_info: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='设备信息',
        ),
    )

    location_info: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='位置信息',
        ),
    )

    timestamp: int = field(
        default=None,
        metadata=dict(
            description='事件时间戳',
        ),
    )

    ip_address: Optional[str] = field(
        default=None,
        metadata=dict(
            description='IP地址',
        ),
    )

    user_agent: Optional[str] = field(
        default=None,
        metadata=dict(
            description='用户代理',
        ),
    )


@ma_dataclass
class BehaviorEvent(Entity):
    """行为事件定义领域模型"""

    event_code: str = field(
        default=None,
        metadata=dict(
            description='事件代码',
        ),
    )

    event_name: str = field(
        default=None,
        metadata=dict(
            description='事件名称',
        ),
    )

    event_category: str = field(
        default=None,
        metadata=dict(
            description='事件分类',
        ),
    )

    description: Optional[str] = field(
        default=None,
        metadata=dict(
            description='事件描述',
        ),
    )

    properties_schema: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='属性模式定义',
        ),
    )

    is_active: bool = field(
        default=True,
        metadata=dict(
            description='是否启用',
        ),
    )


@ma_dataclass
class BehaviorSession(Entity):
    """用户会话领域模型"""

    session_id: str = field(
        default=None,
        metadata=dict(
            description='会话ID',
        ),
    )

    user_id: str = field(
        default=None,
        metadata=dict(
            description='用户ID',
        ),
    )

    start_time: datetime = field(
        default=None,
        metadata=dict(
            description='会话开始时间',
        ),
    )

    end_time: Optional[datetime] = field(
        default=None,
        metadata=dict(
            description='会话结束时间',
        ),
    )

    duration: Optional[int] = field(
        default=None,
        metadata=dict(
            description='会话时长(秒)',
        ),
    )

    page_count: int = field(
        default=0,
        metadata=dict(
            description='访问页面数',
        ),
    )

    event_count: int = field(
        default=0,
        metadata=dict(
            description='事件数量',
        ),
    )

    device_info: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='设备信息',
        ),
    )

    location_info: Optional[Dict[str, Any]] = field(
        default=None,
        metadata=dict(
            description='位置信息',
        ),
    )


@ma_dataclass
class BehaviorFunnel(Entity):
    """转化漏斗配置领域模型"""

    funnel_name: str = field(
        default=None,
        metadata=dict(
            description='漏斗名称',
        ),
    )

    funnel_code: str = field(
        default=None,
        metadata=dict(
            description='漏斗代码',
        ),
    )

    description: Optional[str] = field(
        default=None,
        metadata=dict(
            description='漏斗描述',
        ),
    )

    steps: List[Dict[str, Any]] = field(
        default_factory=list,
        metadata=dict(
            description='漏斗步骤配置',
        ),
    )

    time_window: int = field(
        default=86400,
        metadata=dict(
            description='时间窗口(秒)',
        ),
    )

    is_active: bool = field(
        default=True,
        metadata=dict(
            description='是否启用',
        ),
    )


@ma_dataclass
class BehaviorAnalysis(Entity):
    """行为分析结果领域模型"""

    analysis_type: str = field(
        default=None,
        metadata=dict(
            description='分析类型',
        ),
    )

    analysis_name: str = field(
        default=None,
        metadata=dict(
            description='分析名称',
        ),
    )

    date_range: str = field(
        default=None,
        metadata=dict(
            description='日期范围',
        ),
    )

    data: Dict[str, Any] = field(
        default_factory=dict,
        metadata=dict(
            description='分析结果数据',
        ),
    )

    summary: Optional[str] = field(
        default=None,
        metadata=dict(
            description='分析摘要',
        ),
    )
