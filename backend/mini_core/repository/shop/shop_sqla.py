import datetime as dt
from typing import Type, Tuple, List, Optional

from flask_jwt_extended import get_current_user
from sqlalchemy import Column, String, Table, Integer, DateTime, Text, Enum, Boolean, Numeric, ForeignKey,JSON
from kit.util.sqla import id_column, JsonText
from backend.extensions import mapper_registry
from backend.mini_core.domain.shop import ShopProductCategory, ShopProduct
from kit.repository.sqla import SQLARepository
from kit.util.sqla import id_column

__all__ = ['ShopProductCategorySQLARepository', 'ShopProductSQLARepository']

product_category_table = Table(
    'shop_product_category',
    mapper_registry.metadata,
    id_column(),
    Column('name', String(64), nullable=False, comment='分类名称'),
    Column('remark', Text, comment='备注'),
    Column('type', String(32), comment='类型'),
    Column('parent_id', Integer, comment='上级分类ID'),
    Column('code', String(32), comment='编号'),
    Column('icon', Text, comment='图标路径'),
    Column('image', Text, comment='图片路径'),
    Column("upload_video",Text,comment="upload_video"),
    Column('sort_order', Integer, comment='排序'),
    Column('status', Enum('正常', '停用'), comment='状态'),
    Column('is_audit', Boolean, default=False, comment='是否审核'),
    Column('audit_type', Enum('自动', '人工'), comment='审核类型'),
    Column('store_id', Integer, comment='所属门店ID'),
    Column('attribute', JSON, comment='attribute'),
    Column('content', Text, comment='内容'),
    Column('create_time', DateTime, default=dt.datetime.now),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
)

shop_product_table = Table(
    'shop_product',
    mapper_registry.metadata,
    id_column(),
    Column('category_id', Integer, comment='商品分类ID'),
    Column('code', String(32), comment='商品编号'),
    Column('name', String(128), nullable=False, comment='商品名称'),
    Column('alias', String(64), comment='别名'),
    Column('type', Enum('实物商品', '虚拟商品'), comment='类型'),
    Column('support_overseas_shipping', Boolean, default=False, comment='是否支持海外直邮'),
    Column('keywords', String(255), comment='标签(关键词)'),
    Column('purchase_notice', Text, comment='购买须知'),
    Column('features', Text, comment='商品特色'),
    Column('unit', String(20), comment='单位/比如: 份/瓶/箱/斤'),
    Column('weight', Numeric(10, 2), comment='商品重量(kg)'),
    Column('market_price', Numeric(10, 2), comment='市场价'),
    Column('price', Numeric(10, 2), comment='价格'),
    Column('tax_rate', Numeric(5, 2), comment='税率'),
    Column('points_required', Integer, comment='需要积分'),
    Column('points_reward', Integer, comment='赠送积分'),
    Column('min_purchase_qty', Integer, comment='最少购买'),
    Column('stock', Integer, comment='库存'),
    Column('stock_alert', Integer, comment='库存预警'),
    Column('no_stock_mode', Boolean, default=False, comment='无库存'),
    Column('auto_offline', Boolean, default=False, comment='自动下架'),
    Column('member_card_id', String(64), comment='自动发卡'),
    Column('freight_template_id', Integer, comment='运送物流模板'),
    Column('extend_freight_template_id', Integer, comment='扩展物流模板'),
    Column('discount', String(20), comment='优惠券'),
    Column('sort_order', Integer, comment='排序'),
    Column('is_recommended', Boolean, default=False, comment='是否推荐'),
    Column('display_mode', String(20), comment='是否展示'),
    Column('status', Enum('上架', '下架'), comment='状态'),
    Column('video_code', String(128), comment='视频编号'),
    Column('video_url', Text, comment='视频地址'),
    Column('detail', Text, comment='详细介绍'),
    Column('images', JsonText, comment='商品图片(JSON格式，包含多张图片URL)'),
    Column('specifications', JsonText, comment='商品规格(JSON格式，包含规格名称和规格值)'),
    Column('services', JsonText, comment='售后服务(JSON格式，包含服务类型和适用状态)'),
    Column('attributes', JsonText, comment='扩展属性(JSON格式，包含属性名和属性值)'),
    Column('spec_combinations', JsonText, comment='规格组合(JSON格式，包含初始方式/颜色/尺寸等搭配)'),
    Column('create_time', DateTime, default=dt.datetime.now),
    Column('update_time', DateTime, default=dt.datetime.now, onupdate=dt.datetime.now),
    Column('updater', String(64), comment='更新者'),
    Column('store_id', Integer, comment='店铺ID'),
    # 逻辑删除字段
    Column('is_deleted', Boolean, default=False, comment='是否已删除'),
    Column('delete_time', Integer, default=0, comment='删除时间戳'),
)

mapper_registry.map_imperatively(ShopProduct, shop_product_table)

mapper_registry.map_imperatively(ShopProductCategory, product_category_table)


class ShopProductCategorySQLARepository(SQLARepository):
    @property
    def model(self) -> Type[ShopProductCategory]:
        return ShopProductCategory

    @property
    def query_params(self) -> Tuple:
        return 'name', 'code','status', 'type', 'parent_id'


class ShopProductSQLARepository(SQLARepository):
    @property
    def model(self) -> Type[ShopProduct]:
        return ShopProduct

    @property
    def query_params(self) -> Tuple:
        return 'status', 'type','category_id','name', 'code',"is_recommended"

    def get_queryset(self, **kwargs):
        """重写查询方法，自动过滤已删除的数据"""
        # 获取父类的查询条件
        conditions = self._get_conditions(**kwargs)
        sort_conditions = self._get_sort_conditions(**kwargs)

        # 添加逻辑删除过滤条件（除非明确指定要查询已删除的数据）
        if not kwargs.get('include_deleted', False):
            conditions.append(self.model.is_deleted == False)

        return self.session.query(self.model).filter(*conditions).order_by(*sort_conditions)

    def find(self, **kwargs) -> Optional[ShopProduct]:
        """重写find方法，自动过滤已删除的数据"""
        if not kwargs:
            return None

        # 添加逻辑删除过滤条件（除非明确指定要查询已删除的数据）
        if not kwargs.get('include_deleted', False):
            kwargs['is_deleted'] = False

        query = self.session.query(self.model).filter_by(**kwargs)
        return query.first()

    def find_all(self, **kwargs) -> List[ShopProduct]:
        """重写find_all方法，自动过滤已删除的数据"""
        # 添加逻辑删除过滤条件（除非明确指定要查询已删除的数据）
        if not kwargs.get('include_deleted', False):
            kwargs['is_deleted'] = False

        query = self.session.query(self.model).filter_by(**kwargs)
        return query.all()

    def get_by_id(self, entity_id: int) -> Optional[ShopProduct]:
        """重写get_by_id方法，自动过滤已删除的数据"""
        if entity_id is None:
            return None
        return self.session.query(self.model).filter(
            self.model.id == entity_id,
            self.model.is_deleted == False
        ).first()

    def logical_delete(self, product_id: int, commit: bool = True) -> bool:
        """
        逻辑删除商品

        Args:
            product_id: 商品ID
            commit: 是否立即提交事务

        Returns:
            bool: 删除是否成功
        """
        import time
        try:
            result = self.session.query(self.model).filter(
                self.model.id == product_id,
                self.model.is_deleted == False
            ).update({
                'is_deleted': True,
                'delete_time': int(time.time()),
                'update_time': dt.datetime.now()
            })

            if commit:
                self.session.commit()

            return result > 0
        except Exception as e:
            if commit:
                self.session.rollback()
            raise e

    def batch_logical_delete(self, product_ids: List[int], commit: bool = True) -> int:
        """
        批量逻辑删除商品

        Args:
            product_ids: 商品ID列表
            commit: 是否立即提交事务

        Returns:
            int: 成功删除的数量
        """
        import time
        try:
            result = self.session.query(self.model).filter(
                self.model.id.in_(product_ids),
                self.model.is_deleted == False
            ).update({
                'is_deleted': True,
                'delete_time': int(time.time()),
                'update_time': dt.datetime.now()
            }, synchronize_session=False)

            if commit:
                self.session.commit()

            return result
        except Exception as e:
            if commit:
                self.session.rollback()
            raise e

    def restore(self, product_id: int, commit: bool = True) -> bool:
        """
        恢复逻辑删除的商品

        Args:
            product_id: 商品ID
            commit: 是否立即提交事务

        Returns:
            bool: 恢复是否成功
        """
        try:
            result = self.session.query(self.model).filter(
                self.model.id == product_id,
                self.model.is_deleted == True
            ).update({
                'is_deleted': False,
                'delete_time': 0,
                'update_time': dt.datetime.now()
            })

            if commit:
                self.session.commit()

            return result > 0
        except Exception as e:
            if commit:
                self.session.rollback()
            raise e

    def get_deleted_products(self, **kwargs) -> List[ShopProduct]:
        """
        获取已删除的商品列表

        Args:
            **kwargs: 查询条件

        Returns:
            List[ShopProduct]: 已删除的商品列表
        """
        query = self.session.query(self.model).filter(self.model.is_deleted == True)

        # 添加其他查询条件
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query.all()

    # @property
    # def fuzzy_query_params(self) -> Tuple:
    #     return 'name', 'code',


