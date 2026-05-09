import pytest
from flask import Flask
from marshmallow import ValidationError


# ============================================================
# Schema 参数校验测试
# ============================================================

@pytest.fixture
def schema():
    from backend.mini_core.schema.store.store import NearbyStoreQueryArgSchema
    return NearbyStoreQueryArgSchema()


class TestNearbyStoreSchemaValidation:
    """NearbyStoreQueryArgSchema 参数校验"""

    # —— 正常参数 ——

    def test_valid_minimal_params(self, schema):
        """仅提供必填的经纬度，distance/page/size 使用默认值"""
        result = schema.load({"latitude": 30.5, "longitude": 120.5})
        assert result["latitude"] == 30.5
        assert result["longitude"] == 120.5
        assert result["distance"] == 5.0
        assert result["page"] == 1
        assert result["size"] == 20

    def test_valid_all_params(self, schema):
        """提供所有参数"""
        result = schema.load({
            "latitude": 39.9042,
            "longitude": 116.4074,
            "distance": 10.0,
            "page": 3,
            "size": 50
        })
        assert result["distance"] == 10.0
        assert result["page"] == 3
        assert result["size"] == 50

    def test_latitude_boundary_values(self, schema):
        """纬度边界值：-90 和 90 应通过"""
        schema.load({"latitude": -90, "longitude": 0})
        schema.load({"latitude": 90, "longitude": 0})
        schema.load({"latitude": 0, "longitude": 0})

    def test_longitude_boundary_values(self, schema):
        """经度边界值：-180 和 180 应通过"""
        schema.load({"latitude": 0, "longitude": -180})
        schema.load({"latitude": 0, "longitude": 180})

    def test_distance_boundary_values(self, schema):
        """距离边界值：0.1 和 50 应通过"""
        r1 = schema.load({"latitude": 0, "longitude": 0, "distance": 0.1})
        assert r1["distance"] == 0.1
        r2 = schema.load({"latitude": 0, "longitude": 0, "distance": 50.0})
        assert r2["distance"] == 50.0

    def test_page_and_size_boundary(self, schema):
        """分页边界值"""
        r1 = schema.load({"latitude": 0, "longitude": 0, "page": 1, "size": 1})
        assert r1["page"] == 1
        assert r1["size"] == 1
        r2 = schema.load({"latitude": 0, "longitude": 0, "page": 1, "size": 100})
        assert r2["size"] == 100

    # —— 纬度非法值 ——

    def test_latitude_below_minimum(self, schema):
        """纬度 < -90"""
        with pytest.raises(ValidationError, match="纬度"):
            schema.load({"latitude": -91, "longitude": 0})

    def test_latitude_above_maximum(self, schema):
        """纬度 > 90"""
        with pytest.raises(ValidationError, match="纬度"):
            schema.load({"latitude": 90.1, "longitude": 0})

    def test_latitude_non_numeric(self, schema):
        """纬度非数字"""
        with pytest.raises(ValidationError):
            schema.load({"latitude": "abc", "longitude": 0})

    # —— 经度非法值 ——

    def test_longitude_below_minimum(self, schema):
        """经度 < -180"""
        with pytest.raises(ValidationError, match="经度"):
            schema.load({"latitude": 0, "longitude": -181})

    def test_longitude_above_maximum(self, schema):
        """经度 > 180"""
        with pytest.raises(ValidationError, match="经度"):
            schema.load({"latitude": 0, "longitude": 180.1})

    def test_longitude_non_numeric(self, schema):
        """经度非数字"""
        with pytest.raises(ValidationError):
            schema.load({"latitude": 0, "longitude": "xyz"})

    # —— 距离非法值 ——

    def test_distance_negative(self, schema):
        """负距离"""
        with pytest.raises(ValidationError, match="距离"):
            schema.load({"latitude": 0, "longitude": 0, "distance": -5})

    def test_distance_zero(self, schema):
        """零距离"""
        with pytest.raises(ValidationError, match="距离"):
            schema.load({"latitude": 0, "longitude": 0, "distance": 0})

    def test_distance_too_large(self, schema):
        """距离超过 50km 上限"""
        with pytest.raises(ValidationError, match="距离"):
            schema.load({"latitude": 0, "longitude": 0, "distance": 50.1})

    def test_distance_non_numeric(self, schema):
        """距离非数字"""
        with pytest.raises(ValidationError):
            schema.load({"latitude": 0, "longitude": 0, "distance": "far"})

    # —— 缺少必填参数 ——

    def test_missing_latitude(self, schema):
        """缺少纬度"""
        with pytest.raises(ValidationError):
            schema.load({"longitude": 120.5})

    def test_missing_longitude(self, schema):
        """缺少经度"""
        with pytest.raises(ValidationError):
            schema.load({"latitude": 30.5})

    def test_empty_body(self, schema):
        """空参数"""
        with pytest.raises(ValidationError):
            schema.load({})

    # —— 分页非法值 ——

    def test_page_zero(self, schema):
        """页码为 0"""
        with pytest.raises(ValidationError, match="页码"):
            schema.load({"latitude": 0, "longitude": 0, "page": 0})

    def test_page_negative(self, schema):
        """页码为负"""
        with pytest.raises(ValidationError, match="页码"):
            schema.load({"latitude": 0, "longitude": 0, "page": -1})

    def test_size_zero(self, schema):
        """size 为 0"""
        with pytest.raises(ValidationError, match="每页个数"):
            schema.load({"latitude": 0, "longitude": 0, "size": 0})

    def test_size_exceeds_max(self, schema):
        """size 超过 100"""
        with pytest.raises(ValidationError, match="每页个数"):
            schema.load({"latitude": 0, "longitude": 0, "size": 101})


# ============================================================
# 距离排序与分页 SQL 结构测试
# ============================================================

@pytest.fixture
def store_repo():
    """仓库 fixture：SQLite 内存库（store 表结构兼容 MySQL 函数子集）"""
    import datetime as dt
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    app = Flask(__name__)
    app.config['DATABASE_TYPE'] = 'mysql'

    with app.app_context():
        from backend.extensions import mapper_registry
        from backend.mini_core.repository.store.store_sqla import (
            shop_store_table, ShopStoreSQLARepository
        )

        engine = create_engine('sqlite:///:memory:')
        # 注册 SQLite 缺少的 MySQL 数学函数
        import math
        def _register_sqlite_math(conn):
            conn.connection.create_function('radians', 1, math.radians)
            conn.connection.create_function('cos', 1, math.cos)
            conn.connection.create_function('sin', 1, math.sin)
            conn.connection.create_function('acos', 1, math.acos)

        from sqlalchemy import event
        event.listen(engine, 'connect', _register_sqlite_math)

        mapper_registry.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        repo = ShopStoreSQLARepository(session)
        try:
            yield repo, session
        finally:
            session.close()
            engine.dispose()


def _store(name, lat, lng, **kwargs):
    """快速构造商店记录"""
    from backend.mini_core.domain.store import ShopStore
    import datetime as dt
    defaults = {
        'name': name,
        'latitude': lat,
        'longitude': lng,
        'status': '正常',
        'create_time': dt.datetime.now(),
        'update_time': dt.datetime.now(),
    }
    defaults.update(kwargs)
    store = ShopStore(**defaults)
    return store


class TestNearbyStoreDistanceSorting:
    """验证距离排序和分页"""

    def test_results_sorted_by_distance_ascending(self, store_repo):
        """附近商店按距离升序排列"""
        repo, session = store_repo
        # 以 (30, 120) 为圆心，插入不同位置的商店
        session.add_all([
            _store("远处", 30.05, 120.05),   # ~7.8 km
            _store("近处", 30.01, 120.01),   # ~1.6 km
            _store("中间", 30.03, 120.03),   # ~4.7 km
        ])
        session.commit()

        results, total = repo.get_nearby_stores(30.0, 120.0, distance=10.0)

        assert total == 3
        distances = [r['distance'] for r in results]
        assert distances == sorted(distances)  # 升序

    def test_distance_filter_excludes_far_stores(self, store_repo):
        """超过 distance 的商店不返回"""
        repo, session = store_repo
        session.add_all([
            _store("近", 30.005, 120.005),    # ~0.8 km
            _store("远", 30.10, 120.10),      # ~15.7 km
        ])
        session.commit()

        results, total = repo.get_nearby_stores(30.0, 120.0, distance=5.0)

        assert total == 1
        assert results[0]['name'] == '近'

    def test_pagination_limit_and_offset(self, store_repo):
        """分页 LIMIT/OFFSET 生效"""
        repo, session = store_repo
        import datetime as dt
        # 在相同位置插入 25 个商店
        stores = []
        for i in range(25):
            s = _store(f"store-{i}", 30.001, 120.001)
            s.id = i + 1
            stores.append(s)
        session.add_all(stores)
        session.commit()

        page1, total = repo.get_nearby_stores(30.0, 120.0, distance=10.0, page=1, size=10)
        page2, total2 = repo.get_nearby_stores(30.0, 120.0, distance=10.0, page=2, size=10)
        page3, total3 = repo.get_nearby_stores(30.0, 120.0, distance=10.0, page=3, size=10)

        assert total == 25
        assert total2 == 25
        assert total3 == 25
        assert len(page1) == 10
        assert len(page2) == 10
        assert len(page3) == 5

        # 第 1 页和第 2 页不重叠
        ids_page1 = {r['id'] for r in page1}
        ids_page2 = {r['id'] for r in page2}
        assert ids_page1.isdisjoint(ids_page2)

    def test_no_results_returns_empty_list(self, store_repo):
        """范围内无商店时返回空列表"""
        repo, session = store_repo
        session.add(_store("独店", 31.0, 121.0))
        session.commit()

        results, total = repo.get_nearby_stores(30.0, 120.0, distance=1.0)

        assert total == 0
        assert results == []

    def test_inactive_stores_excluded(self, store_repo):
        """停用状态的商店不出现在结果中"""
        repo, session = store_repo
        session.add_all([
            _store("正常店", 30.001, 120.001, status='正常'),
            _store("停用店", 30.001, 120.001, status='停用'),
        ])
        session.commit()

        results, total = repo.get_nearby_stores(30.0, 120.0, distance=10.0)

        assert total == 1
        assert results[0]['name'] == '正常店'


# ============================================================
# Service 层参数校验
# ============================================================

@pytest.fixture
def store_service():
    app = Flask(__name__)
    app.config['DATABASE_TYPE'] = 'mysql'
    with app.app_context():
        from backend.mini_core.service.store.store import ShopStoreService
        from backend.mini_core.repository.store.store_sqla import ShopStoreSQLARepository
        yield ShopStoreService


class DummyNearbyRepo:
    """用于验证 service 层正确传递分页参数到 repo"""
    def __init__(self):
        self.last_call = None

    def get_nearby_stores(self, latitude, longitude, distance, page, size):
        self.last_call = (latitude, longitude, distance, page, size)
        return [], 0


class TestServiceParameterForwarding:
    """验证 Service 正确转发参数到 Repository"""

    def test_default_values_forwarded(self, store_service):
        dummy = DummyNearbyRepo()
        svc = store_service(dummy)
        svc.get_nearby(39.9, 116.4)
        assert dummy.last_call == (39.9, 116.4, 5.0, 1, 20)

    def test_all_params_forwarded(self, store_service):
        dummy = DummyNearbyRepo()
        svc = store_service(dummy)
        svc.get_nearby(39.9, 116.4, 10.0, page=3, size=50)
        assert dummy.last_call == (39.9, 116.4, 10.0, 3, 50)

    def test_result_structure(self, store_service):
        dummy = DummyNearbyRepo()
        svc = store_service(dummy)
        result = svc.get_nearby(39.9, 116.4)
        assert result['code'] == 200
        assert result['data'] == []
        assert result['total'] == 0
