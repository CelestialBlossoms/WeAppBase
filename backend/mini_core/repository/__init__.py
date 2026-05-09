from kit.repository.provider import repository


log_sqla_repo = repository('backend.mini_core.repository.card.card_sqla:CardSQLARepository', 'log_sqla_repo')
banner_sqla_repo = repository('backend.mini_core.repository.banner.banner_sqla:BannerSQLARepository', 'banner_sqla_repo')

distribution_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionSQLARepository', 'distribution_sqla_repo')
distribution_config_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionConfigSQLARepository', 'distribution_config_sqla_repo')
distribution_grade_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionGradeSQLARepository', 'distribution_grade_sqla_repo')
distribution_grade_update_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionGradeUpdateSQLARepository', 'distribution_grade_update_sqla_repo')
distribution_income_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionIncomeSQLARepository', 'distribution_income_sqla_repo')
distribution_log_sqla_repo = repository('backend.mini_core.repository.distribution.distribution_sqla:DistributionLogSQLARepository', 'distribution_log_sqla_repo')
distribution_withdrawal_sqla_repo = repository('backend.mini_core.repository.distribution.withdrawal_application:DistributionWithdrawalSQLARepository', 'distribution_withdrawal_sqla_repo')

shop_product_sqla_repo = repository('backend.mini_core.repository.shop.shop_sqla:ShopProductSQLARepository', 'shop_product_sqla_repo')
shop_product_category_sqla_repo = repository('backend.mini_core.repository.shop.shop_sqla:ShopProductCategorySQLARepository', 'shop_product_category_sqla_repo')

store_sqla_repo = repository('backend.mini_core.repository.store.store_sqla:ShopStoreSQLARepository', 'store_sqla_repo')
store_sqla_category_repo = repository('backend.mini_core.repository.store.store_car_sqla:ShopStoreCategorySQLARepository', 'store_sqla_category_repo')

shop_specification_sqla_repo = repository('backend.mini_core.repository.shop.shop_specification:ShopSpecificationSQLARepository', 'shop_specification_sqla_repo')
shop_specification_attribute_sqla_repo = repository('backend.mini_core.repository.shop.shop_specification:ShopSpecificationAttributeSQLARepository', 'shop_specification_attribute_sqla_repo')

shop_order_sqla_repo = repository('backend.mini_core.repository.order.order_sqla:ShopOrderSQLARepository', 'shop_order_sqla_repo')
shop_order_detail_sqla_repo = repository('backend.mini_core.repository.order.order_detail_sql:OrderDetailSQLARepository', 'shop_order_detail_sqla_repo')
order_log_sqla_repo = repository('backend.mini_core.repository.order.order_log_sql:OrderLogSQLARepository', 'order_log_sqla_repo')
shop_order_setting_sqla_repo = repository('backend.mini_core.repository.order.shop_order_setting_sqla:ShopOrderSettingSQLARepository', 'shop_order_setting_sqla_repo')
shop_return_reason_sqla_repo = repository('backend.mini_core.repository.order.shop_return_reason_sqla:ShopReturnReasonSQLARepository', 'shop_return_reason_sqla_repo')

shop_order_return_sqla_repo = repository('backend.mini_core.repository.order.order_return_sql:OrderReturnSQLARepository', 'shop_order_return_sqla_repo')
shop_order_return_detail_sqla_repo = repository('backend.mini_core.repository.order.order_return_sql:OrderReturnDetailSQLARepository', 'shop_order_return_detail_sqla_repo')
shop_order_return_log_sqla_repo = repository('backend.mini_core.repository.order.order_return_sql:OrderReturnLogSQLARepository', 'shop_order_return_log_sqla_repo')

shop_user_sqla_repo = repository('backend.mini_core.repository.shop.shop_user_sqla:ShopUserSQLARepository', 'shop_user_sqla_repo')
shop_user_address_sqla_repo = repository('backend.mini_core.repository.shop.shop_user_sqla:ShopUserAddressSQLARepository', 'shop_user_address_sqla_repo')

shop_order_cart_sqla_repo = repository('backend.mini_core.repository.order.shop_order_cart_sqla:ShopOrderCartSQLARepository', 'shop_order_cart_sqla_repo')
shop_order_logistics_sqla_repo = repository('backend.mini_core.repository.order.shop_order_logistics_sqla:ShopOrderLogisticsSQLARepository', 'shop_order_logistics_sqla_repo')
shop_order_review_repo = repository('backend.mini_core.repository.order.order_review:OrderReviewSQLARepository', 'shop_order_review_repo')
member_level_config_sqla_repo = repository('backend.mini_core.repository.shop.member_level_config:MemberLevelConfigSQLARepository', 'member_level_config_sqla_repo')
