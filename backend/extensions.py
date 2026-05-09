from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from apispec.ext.marshmallow import MarshmallowPlugin
from sqlalchemy.orm import registry

from kit.hook import RedisHook, SocketIOApp, SqlAHook
from kit.hook.casbin import CasbinEnforcer


def schema_name_resolver(schema):
    """为 OpenAPI 生成稳定且唯一的 schema 名称。

    apispec 默认只使用类名，项目里存在多个模块同名 schema/domain，
    例如 Permission、DeleteIds、ShopUser、WxPay，会触发重复名称警告。
    """
    module = getattr(schema, '__module__', '')
    name = getattr(schema, '__name__', schema.__class__.__name__)
    full_name = f'{module}_{name}' if module else name
    return ''.join(char if char.isalnum() else '_' for char in full_name)


api = Api(
    spec_kwargs={
        'marshmallow_plugin': MarshmallowPlugin(
            schema_name_resolver=schema_name_resolver
        )
    }
)
db = SqlAHook()
migrate = Migrate()
metadata = db.metadata
mapper_registry = registry(metadata=metadata)
redis = RedisHook()
sio = SocketIOApp()
casbin_enforcer = CasbinEnforcer()
jwt = JWTManager()
