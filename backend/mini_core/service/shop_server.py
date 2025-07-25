from typing import List, Dict, Any

from backend.mini_core.domain.shop import ShopProduct, ShopProductCategory
from backend.mini_core.repository.shop.shop_sqla import ShopProductSQLARepository, ShopProductCategorySQLARepository
from kit.service.base import CRUDService

__all__ = ['ShopProductService', 'ShopProductCategoryService']


class ShopProductService(CRUDService[ShopProduct]):
    def __init__(self, repo: ShopProductSQLARepository):
        super().__init__(repo)
        self._repo = repo

    @property
    def repo(self) -> ShopProductSQLARepository:
        return self._repo

    def get_by_id(self, product_id: int) -> Dict[str, Any]:
        """根据id获取商品"""
        if product_id:
            data = self._repo.get_by_id(product_id)
            if data is not None:
                return dict(data=data, code=200)
            else:
                return dict(data=None, code=404)
        else:
            return dict(data=None, code=404)

    def get_list(self, args: dict) -> Dict[str, Any]:
        """根据条件获取商品"""
        product_id = args.get("id")
        if product_id:
            data = self._repo.get_by_id(product_id)
            return dict(data=data, code=200)

        # 确保默认不包含已删除的数据
        if 'include_deleted' not in args:
            args['include_deleted'] = False

        data, total = self._repo.list(**args)
        return dict(data=data, total=total, code=200)

    def list_by_category(self, category_id: int) -> Dict[str, Any]:
        """获取指定分类下的所有商品"""
        data = self._repo.find(category_id=category_id, include_deleted=False)
        return dict(data=data, code=200)

    def get_recommended(self) -> Dict[str, Any]:
        """获取推荐商品"""
        data = self._repo.find(is_recommended=True, status="上架", include_deleted=False)
        return dict(data=data, code=200)

    def update_stock(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """更新商品库存"""
        product = self._repo.get_by_id(product_id)
        if not product:
            return dict(data=None, code=404, message="商品不存在")

        # 确保库存不小于0
        new_stock = max(0, product.stock + quantity)
        product.stock = new_stock

        # 检查是否低于库存预警值
        stock_warning = False
        if product.stock_alert and product.stock <= product.stock_alert:
            stock_warning = True

        result = self._repo.update(product_id, product)
        return dict(data=result, stock_warning=stock_warning, code=200)

    def update_pro(self, product_id: int, product: Dict) -> Dict[str, Any]:
        """更新商品信息"""
        print("product", product)
        re_data = self._repo.update(product_id,product)
        return dict(data=re_data, code=200)

    def create_pro(self, product: Dict) -> Dict[str, Any]:
        """创建新商品"""
        result = super().create(product)
        return dict(data=result, code=200)

    def delete_pro(self, product_id: int) -> Dict[str, Any]:
        """删除商品"""
        result = self._repo.logical_delete(product_id, commit=True)
        return dict(data=result, code=200)

    def change_status(self, product_id: int, status: str) -> Dict[str, Any]:
        """更改商品状态（上架/下架）"""
        product = self._repo.get_by_id(product_id)
        if not product:
            return dict(data=None, code=404, message="商品不存在")

        product.status = status
        result = self._repo.update(product_id, product)
        return dict(data=result, code=200)

    def batch_change_status(self, product_ids: List[int], action: str) -> Dict[str, Any]:
        """批量更改商品状态（上架/下架/删除）"""
        # 将action转换为对应的状态
        status_map = {
            "publish": "上架",
            "unpublish": "下架",
            "delete": "删除"
        }
        target_status = status_map.get(action)
        if not target_status:
            return dict(
                success_count=0,
                failed_count=len(product_ids),
                failed_items=[],
                code=400,
                message="无效的操作类型"
            )

        success_count = 0
        failed_count = 0
        failed_items = []

        for product_id in product_ids:
            try:
                product = self._repo.get_by_id(product_id)
                if not product:
                    failed_count += 1
                    failed_items.append({
                        "product_id": product_id,
                        "error": "商品不存在"
                    })
                    continue

                # 更新商品状态
                if action == "delete":
                    # 逻辑删除
                    success = self._repo.logical_delete(product_id, commit=False)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_items.append({
                            "product_id": product_id,
                            "error": "商品删除失败"
                        })
                else:
                    # 更新状态
                    product.status = target_status
                    self._repo.update(product_id, product)
                    success_count += 1

            except Exception as e:
                failed_count += 1
                failed_items.append({
                    "product_id": product_id,
                    "error": str(e)
                })

        # 提交事务
        try:
            self._repo.session.commit()
        except Exception as e:
            self._repo.session.rollback()
            return dict(
                success_count=0,
                failed_count=len(product_ids),
                failed_items=[{"product_id": pid, "error": "事务提交失败"} for pid in product_ids],
                code=500,
                message=f"批量操作失败: {str(e)}"
            )

        # 构建返回消息
        if failed_count == 0:
            message = f"成功{action}了{success_count}个商品"
        elif success_count == 0:
            message = f"批量{action}操作失败，所有商品都操作失败"
        else:
            message = f"批量{action}操作完成，成功{success_count}个，失败{failed_count}个"

        return dict(
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items,
            code=200,
            message=message
        )

    def logical_delete(self, product_id: int) -> Dict[str, Any]:
        """逻辑删除商品"""
        try:
            success = self._repo.logical_delete(product_id)
            if success:
                return dict(code=200, message="商品删除成功")
            else:
                return dict(code=404, message="商品不存在或已被删除")
        except Exception as e:
            return dict(code=500, message=f"删除失败: {str(e)}")

    def batch_logical_delete(self, product_ids: List[int]) -> Dict[str, Any]:
        """批量逻辑删除商品"""
        if not product_ids:
            return dict(code=400, message="未提供要删除的商品ID")

        try:
            deleted_count = self._repo.batch_logical_delete(product_ids)
            return dict(
                code=200,
                message=f"成功删除{deleted_count}个商品",
                data={"deleted_count": deleted_count}
            )
        except Exception as e:
            return dict(code=500, message=f"批量删除失败: {str(e)}")

    def restore_product(self, product_id: int) -> Dict[str, Any]:
        """恢复逻辑删除的商品"""
        try:
            success = self._repo.restore(product_id)
            if success:
                return dict(code=200, message="商品恢复成功")
            else:
                return dict(code=404, message="商品不存在或未被删除")
        except Exception as e:
            return dict(code=500, message=f"恢复失败: {str(e)}")

    def get_deleted_products(self, **kwargs) -> Dict[str, Any]:
        """获取已删除的商品列表"""
        try:
            products = self._repo.get_deleted_products(**kwargs)
            return dict(
                code=200,
                data=products,
                total=len(products)
            )
        except Exception as e:
            return dict(code=500, message=f"查询失败: {str(e)}")

    def get_all_products_including_deleted(self, args: dict) -> Dict[str, Any]:
        """获取所有商品（包括已删除的）"""
        # 明确指定包含已删除的数据
        args['include_deleted'] = True
        data, total = self._repo.list(**args)
        return dict(data=data, total=total, code=200)

    def toggle_recommendation(self, product_id: int) -> Dict[str, Any]:
        """切换商品推荐状态"""
        product = self._repo.get_by_id(product_id)
        if not product:
            return dict(data=None, code=404, message="商品不存在")

        product.is_recommended = not product.is_recommended
        result = self._repo.update(product_id, product)
        return dict(data=result, code=200)


class ShopProductCategoryService(CRUDService[ShopProductCategory]):
    def __init__(self, repo: ShopProductCategorySQLARepository):
        super().__init__(repo)
        self._repo = repo

    @property
    def repo(self) -> ShopProductCategorySQLARepository:
        return self._repo

    def get_table_filed(self, file_names: List[str]):
        data = self._repo.get_fields_by_names(field_names=file_names)
        return dict(data=data, code=200)

    def get_list(self, args: dict) -> Dict[str, Any]:
        """根据条件获取分类"""
        data, total = self._repo.list(**args)
        return dict(data=data, code=200, total=total)

    def find_data(self, args: dict) -> Dict[str, Any]:
        data = self._repo.find(id=args["id"])
        return dict(data=data, code=200)

    def list_by_parent(self, parent_id: int) -> Dict[str, Any]:
        """获取指定父分类下的所有子分类"""
        data = self._repo.find(parent_id=parent_id)
        return dict(data=data, code=200)

    def get_tree(self) -> Dict[str, Any]:
        """获取分类树结构"""
        # 先获取所有分类
        all_categories = self._repo.find()

        # 构建树结构
        root_categories = []
        category_map = {}

        # 先构建一个映射
        for category in all_categories:
            category_map[category.id] = {
                "id": category.id,
                "name": category.name,
                "code": category.code,
                "children": []
            }

        # 然后构建树
        for category in all_categories:
            if not category.parent_id:
                # 根分类
                root_categories.append(category_map[category.id])
            else:
                # 子分类，添加到父分类的children中
                if category.parent_id in category_map:
                    category_map[category.parent_id]["children"].append(category_map[category.id])

        return dict(data=root_categories, code=200)

    def update(self, category_id: int, category: ShopProductCategory) -> Dict[str, Any]:
        """更新分类信息"""
        result = super().update(category_id, category)
        return dict(data=result, code=200)

    def create(self, category: ShopProductCategory) -> Dict[str, Any]:
        """创建新分类"""
        result = super().create(category)
        return dict(data=result, code=200)

    def delete(self, category_id: int) -> Dict[str, Any]:
        """删除分类"""
        result = super().delete(category_id)
        return dict(data=result, code=200)

    def delete_batch(self, category_ids: List[int]) -> Dict[str, Any]:
        """批量删除分类"""
        results = []
        for category_id in category_ids:
            result = self.delete(category_id)
            results.append(result)
        return dict(data=results, code=200)
