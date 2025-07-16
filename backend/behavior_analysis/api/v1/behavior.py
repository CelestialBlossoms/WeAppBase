# backend/behavior_analysis/api/v1/behavior.py

from flask.views import MethodView
from backend.business.service.auth import auth_required
from backend.behavior_analysis.service import BehaviorService
from backend.behavior_analysis.schema import (
    BehaviorTrackSchema,
    BehaviorOverviewQuerySchema,
    BehaviorFunnelQuerySchema,
    BehaviorUserPathQuerySchema,
    BehaviorProductAnalysisQuerySchema,
    BehaviorUserPortraitQuerySchema
)
from kit.util.blueprint import APIBlueprint

blp = APIBlueprint('behavior', 'behavior', url_prefix='/')


@blp.route('/track')
class BehaviorTrackAPI(MethodView):
    """行为数据上报API"""

    @blp.arguments(BehaviorTrackSchema)
    def post(self, args: dict):
        """上报用户行为数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.track_event(args)


@blp.route('/overview')
class BehaviorOverviewAPI(MethodView):
    """行为概览API"""
    decorators = [auth_required()]

    @blp.arguments(BehaviorOverviewQuerySchema, location='query')
    def get(self, args: dict):
        """获取行为概览数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.get_overview_data(
            date_range=args.get('date_range', '7d'),
            user_id=args.get('user_id', ''),
            agent_id=args.get('agent_id', '')
        )


@blp.route('/funnel')
class BehaviorFunnelAPI(MethodView):
    """漏斗分析API"""
    decorators = [auth_required()]

    @blp.arguments(BehaviorFunnelQuerySchema, location='query')
    def get(self, args: dict):
        """获取漏斗分析数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.get_funnel_analysis(
            funnel_id=args.get('funnel_id', ''),
            date_range=args.get('date_range', '7d'),
            agent_id=args.get('agent_id', ''),
        )


@blp.route('/user-path')
class BehaviorUserPathAPI(MethodView):
    """用户路径分析API"""
    decorators = [auth_required()]

    @blp.arguments(BehaviorUserPathQuerySchema, location='query')
    def get(self, args: dict):
        """获取用户路径分析数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.get_user_path_analysis(
            user_id=args.get('user_id', ''),
            date_range=args.get('date_range', '7d')
        )


@blp.route('/product-analysis')
class BehaviorProductAnalysisAPI(MethodView):
    """商品行为分析API"""
    decorators = [auth_required()]

    @blp.arguments(BehaviorProductAnalysisQuerySchema, location='query')
    def get(self, args: dict):
        """获取商品行为分析数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.get_product_analysis(
            product_id=args.get('product_id', 0),
            date_range=args.get('date_range', '7d')
        )


@blp.route('/user-portrait')
class BehaviorUserPortraitAPI(MethodView):
    """用户画像分析API"""
    decorators = [auth_required()]

    @blp.arguments(BehaviorUserPortraitQuerySchema, location='query')
    def get(self, args: dict):
        """获取用户画像分析数据"""
        from backend.behavior_analysis.repository import user_behavior_sqla_repo
        from backend.behavior_analysis.service import BehaviorService

        service = BehaviorService(user_behavior_sqla_repo)
        return service.get_user_portrait(user_id=args.get('user_id', ''))
