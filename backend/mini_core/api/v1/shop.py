from flask.views import MethodView
from typing import List

from backend.mini_core.schema.shop import (
    ProductCategoryQueryArgSchema, ReProductCategorySchema, ReProductCategoryListSchema,
    ShopProductQueryArgSchema, ReShopProductSchema, ReShopProductListSchema,
    ShopProductStockUpdateArgSchema, ShopProductStatusUpdateArgSchema,
    ReShopProductStockUpdateSchema, ReProductCategoryTreeSchema,ProductCategorySchema,ShopProductSchema,
    ProductCategoryBatchDeleteSchema, ShopProductBatchStatusUpdateArgSchema, ReShopProductBatchStatusUpdateSchema
)
from backend.mini_core.schema.banner import (BannerIDSchema)
from kit.schema.base import  FieldQuerySchema
from backend.mini_core.domain.shop import ShopProduct, ShopProductCategory
from backend.business.service.auth import auth_required
from backend.mini_core.service import (
    shop_product_service, shop_product_category_service
)
from kit.util.blueprint import APIBlueprint

blp = APIBlueprint('shop', 'shop', url_prefix='/')


@blp.route('/product-category-field')
class ProductCategoryAPI(MethodView):
    """商品分类API"""
    decorators = [auth_required()]

    @blp.arguments(FieldQuerySchema)
    @blp.response()
    def post(self, args: dict):
        """查询商品分类列表"""
        return shop_product_category_service.get_table_filed(args["fields"])

@blp.route('/product-category')
class ProductCategoryAPI(MethodView):
    """商品分类API"""

    @blp.arguments(ProductCategoryQueryArgSchema, location='query')
    @blp.response(ReProductCategoryListSchema)
    def get(self, args: dict):
        """查询商品分类列表"""
        return shop_product_category_service.get_list(args)

    @auth_required()
    @blp.arguments(ProductCategorySchema)
    @blp.response(ReProductCategorySchema)
    def post(self, category):
        """创建或更新商品分类"""
        return shop_product_category_service.create(category)


@blp.route('/product-category/<int:category_id>')
class ProductCategoryDetailAPI(MethodView):
    """商品分类详情API"""

    @blp.response(ReProductCategorySchema)
    def get(self, category_id: int):
        """获取指定ID的商品分类"""
        return shop_product_category_service.find_data({"id": category_id})

    @blp.arguments(ProductCategorySchema)
    @blp.response(ReProductCategorySchema)
    def put(self, category, category_id: int):
        """更新指定ID的商品分类"""
        return shop_product_category_service.update(category_id, category)

    @blp.response(ReProductCategorySchema)
    def delete(self, category_id: int):
        """删除指定ID的商品分类"""
        return shop_product_category_service.delete(category_id)


@blp.route('/product-category/batch-delete')
class ProductCategoryBatchDeleteAPI(MethodView):
    """批量删除商品分类API"""

    @blp.arguments(ProductCategoryBatchDeleteSchema)
    @blp.response()
    def post(self, args):
        """批量删除指定ID的商品分类"""
        category_ids = args["category_ids"]
        return shop_product_category_service.delete_batch(category_ids)


@blp.route('/product-category/tree')
class ProductCategoryTreeAPI(MethodView):
    """商品分类树API"""

    @blp.response(ReProductCategoryTreeSchema)
    def get(self):
        """获取商品分类树结构"""
        return shop_product_category_service.get_tree()


@blp.route('/product-category/children/<int:parent_id>')
class ProductCategoryChildrenAPI(MethodView):
    """商品子分类API"""

    @blp.response(ReProductCategoryListSchema)
    def get(self, parent_id: int):
        """获取指定父分类下的所有子分类"""
        return shop_product_category_service.list_by_parent(parent_id)


@blp.route('/shop-product')
class ShopProductAPI(MethodView):
    """商品API"""

    @blp.arguments(ShopProductQueryArgSchema, location='query')
    @blp.response(ReShopProductListSchema)
    def get(self, args: dict):
        """查询商品列表"""
        return shop_product_service.get_list(args)

    @auth_required()
    @blp.arguments(ShopProductSchema)
    @blp.response(ReShopProductSchema)
    def post(self, product):
        """创建商品"""
        return shop_product_service.create_pro(product)


@blp.route('/shop-product/<int:product_id>')
class ShopProductDetailAPI(MethodView):
    """商品详情API"""

    @blp.response(ReShopProductSchema)
    def get(self, product_id: int):
        """获取指定ID的商品"""
        data = shop_product_service.get_by_id(product_id)
        return data

    @blp.arguments(ShopProductSchema)
    @blp.response(ReShopProductSchema)
    def put(self, product, product_id: int):
        """更新指定ID的商品"""
        return shop_product_service.update_pro(product_id, product)

    @blp.response(ReShopProductSchema)
    def delete(self, product_id: int):
        """删除指定ID的商品"""
        return shop_product_service.logical_delete(product_id)


@blp.route('/shop-product/category/<int:category_id>')
class ShopProductByCategoryAPI(MethodView):
    """按分类查询商品API"""

    @blp.response(ReShopProductListSchema)
    def get(self, category_id: int):
        """获取指定分类下的所有商品"""
        return shop_product_service.list_by_category(category_id)


@blp.route('/shop-product/recommended')
class ShopProductRecommendedAPI(MethodView):
    """推荐商品API"""

    @blp.response(ReShopProductListSchema)
    def get(self):
        """获取所有推荐商品"""
        return shop_product_service.get_recommended()


@blp.route('/shop-product/stock')
class ShopProductStockAPI(MethodView):
    """商品库存API"""

    @blp.arguments(ShopProductStockUpdateArgSchema)
    @blp.response(ReShopProductStockUpdateSchema)
    def post(self, args):
        """更新商品库存"""
        return shop_product_service.update_stock(args["id"], args["quantity"])


@blp.route('/shop-product/status')
class ShopProductStatusAPI(MethodView):
    """商品状态API"""

    @blp.arguments(ShopProductStatusUpdateArgSchema)
    @blp.response(ReShopProductSchema)
    def post(self, args):
        """更新商品状态"""
        return shop_product_service.change_status(args["id"], args["status"])


@blp.route('/shop-product/toggle-recommendation/<int:product_id>')
class ShopProductToggleRecommendationAPI(MethodView):
    """切换商品推荐状态API"""

    @blp.response(ReShopProductSchema)
    def post(self, product_id: int):
        """切换商品的推荐状态"""
        return shop_product_service.toggle_recommendation(product_id)


@blp.route('/shop-product/batch')
class ShopProductBatchAPI(MethodView):
    """批量商品操作API"""
    decorators = [auth_required()]

    @blp.arguments(ShopProductBatchStatusUpdateArgSchema)
    @blp.response(ReShopProductBatchStatusUpdateSchema)
    def post(self, args):
        """批量更新商品状态（上架/下架/删除）"""
        return shop_product_service.batch_change_status(args["ids"], args["action"])


@blp.route('/shop-product/logical-delete/<int:product_id>')
class ShopProductLogicalDeleteAPI(MethodView):
    """商品逻辑删除API"""
    decorators = [auth_required()]

    @blp.response()
    def delete(self, product_id: int):
        """逻辑删除商品"""
        return shop_product_service.logical_delete(product_id)


@blp.route('/shop-product/batch-logical-delete')
class ShopProductBatchLogicalDeleteAPI(MethodView):
    """批量逻辑删除商品API"""
    decorators = [auth_required()]

    @blp.arguments(ShopProductBatchStatusUpdateArgSchema)
    @blp.response()
    def post(self, args):
        """批量逻辑删除商品"""
        return shop_product_service.batch_logical_delete(args["ids"])


@blp.route('/shop-product/restore/<int:product_id>')
class ShopProductRestoreAPI(MethodView):
    """商品恢复API"""
    decorators = [auth_required()]

    @blp.response()
    def post(self, product_id: int):
        """恢复逻辑删除的商品"""
        return shop_product_service.restore_product(product_id)


@blp.route('/shop-product/deleted')
class ShopProductDeletedAPI(MethodView):
    """已删除商品查询API"""
    decorators = [auth_required()]

    @blp.response(ReShopProductListSchema)
    def get(self):
        """获取已删除的商品列表"""
        return shop_product_service.get_deleted_products()


@blp.route('/shop-product/all-including-deleted')
class ShopProductAllIncludingDeletedAPI(MethodView):
    """获取所有商品（包括已删除的）API"""
    decorators = [auth_required()]

    @blp.arguments(ShopProductQueryArgSchema, location='query')
    @blp.response(ReShopProductListSchema)
    def get(self, args: dict):
        """获取所有商品（包括已删除的）"""
        return shop_product_service.get_all_products_including_deleted(args)


