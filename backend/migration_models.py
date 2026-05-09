"""为 Flask-Migrate 加载项目里的 SQLAlchemy 表映射。

项目使用 classical mapping，不是声明式 ``db.Model``。
Alembic 只有在导入定义 ``Table(...)`` 的模块后，才能从
``mapper_registry.metadata`` 中看到完整表结构。
"""
from importlib import import_module


MODEL_MODULES = (
    'backend.alarm.repository.alarm.sqla',
    'backend.alarm.repository.alarm_rule.sqla',
    'backend.behavior_analysis.repository.behavior_sqla',
    'backend.license_management.repository.li.sqla',
    'backend.log.repository.log.sqla',
    'backend.role.repository.role.sqla',
    'backend.user.repository.department.sqla',
    'backend.user.repository.permission.sqla',
    'backend.user.repository.user.sqla',
    'backend.mini_core.repository.banner.banner_sqla',
    'backend.mini_core.repository.card.card_sqla',
    'backend.mini_core.repository.distribution.distribution_sqla',
    'backend.mini_core.repository.distribution.withdrawal_application',
    'backend.mini_core.repository.order.order_detail_sql',
    'backend.mini_core.repository.order.order_log_sql',
    'backend.mini_core.repository.order.order_return_sql',
    'backend.mini_core.repository.order.order_review',
    'backend.mini_core.repository.order.order_sqla',
    'backend.mini_core.repository.order.shop_order_cart_sqla',
    'backend.mini_core.repository.order.shop_order_logistics_sqla',
    'backend.mini_core.repository.order.shop_order_setting_sqla',
    'backend.mini_core.repository.order.shop_return_reason_sqla',
    'backend.mini_core.repository.shop.member_level_config',
    'backend.mini_core.repository.shop.shop_specification',
    'backend.mini_core.repository.shop.shop_sqla',
    'backend.mini_core.repository.shop.shop_user_sqla',
    'backend.mini_core.repository.store.store_car_sqla',
    'backend.mini_core.repository.store.store_sqla',
)


def load_project_models() -> None:
    """导入所有包含表定义和映射关系的模块。"""
    for module_name in MODEL_MODULES:
        import_module(module_name)
