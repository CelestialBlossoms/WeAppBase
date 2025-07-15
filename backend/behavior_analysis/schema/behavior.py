# backend/behavior_analysis/schema/behavior.py

from marshmallow import Schema, fields, validate, ValidationError
from typing import Dict, Any, Optional


class BehaviorTrackSchema(Schema):
    """行为数据上报验证模式"""

    event_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    event_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    session_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    agent_id = fields.Str(validate=validate.Length(min=0, max=64))
    page_path = fields.Str(validate=validate.Length(max=200))
    element_id = fields.Str(validate=validate.Length(max=100))
    product_id = fields.Int()
    order_id = fields.Str(validate=validate.Length(max=64))
    properties = fields.Dict()
    device_info = fields.Dict()
    location_info = fields.Dict()
    timestamp = fields.Int(required=True)


class BehaviorOverviewQuerySchema(Schema):
    """行为概览查询参数验证模式"""

    date_range = fields.Str(required=True, validate=validate.OneOf(['1d', '7d', '30d', '90d']))
    user_id = fields.Str(validate=validate.Length(max=64))


class BehaviorFunnelQuerySchema(Schema):
    """漏斗分析查询参数验证模式"""

    funnel_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    date_range = fields.Str(required=True, validate=validate.OneOf(['1d', '7d', '30d', '90d']))
    agent_id = fields.Str(validate=validate.Length(min=0, max=64))


class BehaviorUserPathQuerySchema(Schema):
    """用户路径分析查询参数验证模式"""

    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    date_range = fields.Str(required=True, validate=validate.OneOf(['1d', '7d', '30d', '90d']))


class BehaviorProductAnalysisQuerySchema(Schema):
    """商品行为分析查询参数验证模式"""

    product_id = fields.Int(required=True)
    date_range = fields.Str(required=True, validate=validate.OneOf(['1d', '7d', '30d', '90d']))


class BehaviorUserPortraitQuerySchema(Schema):
    """用户画像分析查询参数验证模式"""

    user_id = fields.Str(required=True, validate=validate.Length(min=1, max=64))


# 响应模式
class BehaviorOverviewResponseSchema(Schema):
    """行为概览响应模式"""

    total_users = fields.Int()
    active_users = fields.Int()
    total_sessions = fields.Int()
    total_events = fields.Int()
    avg_session_duration = fields.Float()
    bounce_rate = fields.Float()
    top_events = fields.List(fields.Dict())
    top_pages = fields.List(fields.Dict())


class BehaviorFunnelResponseSchema(Schema):
    """漏斗分析响应模式"""

    funnel_name = fields.Str()
    steps = fields.List(fields.Dict())
    total_conversion_rate = fields.Float()


class BehaviorUserPathResponseSchema(Schema):
    """用户路径分析响应模式"""

    user_id = fields.Str()
    paths = fields.List(fields.Dict())
    avg_path_length = fields.Float()
    most_common_entry = fields.Str()
    most_common_exit = fields.Str()


class BehaviorProductAnalysisResponseSchema(Schema):
    """商品行为分析响应模式"""

    product_id = fields.Int()
    product_name = fields.Str()
    views = fields.Int()
    clicks = fields.Int()
    add_to_cart = fields.Int()
    purchases = fields.Int()
    conversion_rates = fields.Dict()
    avg_view_duration = fields.Float()
    favorite_count = fields.Int()
    share_count = fields.Int()


class BehaviorUserPortraitResponseSchema(Schema):
    """用户画像分析响应模式"""

    user_id = fields.Str()
    basic_info = fields.Dict()
    behavior_patterns = fields.Dict()
    product_preferences = fields.Dict()
    purchase_behavior = fields.Dict()
    engagement_level = fields.Str()
