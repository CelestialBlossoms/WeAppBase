-- 行为分析模块数据库迁移文件
-- 创建时间: 2024-01-15
-- 版本: 1.0.0

-- 1. 用户行为记录表
CREATE TABLE `t_user_behavior` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` varchar(64) NOT NULL COMMENT '用户ID',
  `session_id` varchar(64) NOT NULL COMMENT '会话ID',
  `event_type` varchar(50) NOT NULL COMMENT '事件类型',
  `event_name` varchar(100) NOT NULL COMMENT '事件名称',
  `page_path` varchar(200) DEFAULT NULL COMMENT '页面路径',
  `element_id` varchar(100) DEFAULT NULL COMMENT '元素ID',
  `product_id` bigint(20) DEFAULT NULL COMMENT '商品ID',
  `order_id` varchar(64) DEFAULT NULL COMMENT '订单ID',
  `properties` json DEFAULT NULL COMMENT '事件属性(JSON格式)',
  `device_info` json DEFAULT NULL COMMENT '设备信息',
  `location_info` json DEFAULT NULL COMMENT '位置信息',
  `timestamp` bigint(20) NOT NULL COMMENT '事件时间戳',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(500) DEFAULT NULL COMMENT '用户代理',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户行为记录表';

-- 2. 行为事件定义表
CREATE TABLE `t_behavior_event` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `event_code` varchar(50) NOT NULL UNIQUE COMMENT '事件代码',
  `event_name` varchar(100) NOT NULL COMMENT '事件名称',
  `event_category` varchar(50) NOT NULL COMMENT '事件分类',
  `description` text DEFAULT NULL COMMENT '事件描述',
  `properties_schema` json DEFAULT NULL COMMENT '属性模式定义',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_event_code` (`event_code`),
  KEY `idx_event_category` (`event_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行为事件定义表';

-- 3. 用户会话表
CREATE TABLE `t_behavior_session` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `session_id` varchar(64) NOT NULL UNIQUE COMMENT '会话ID',
  `user_id` varchar(64) NOT NULL COMMENT '用户ID',
  `start_time` datetime NOT NULL COMMENT '会话开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '会话结束时间',
  `duration` int(11) DEFAULT NULL COMMENT '会话时长(秒)',
  `page_count` int(11) DEFAULT 0 COMMENT '访问页面数',
  `event_count` int(11) DEFAULT 0 COMMENT '事件数量',
  `device_info` json DEFAULT NULL COMMENT '设备信息',
  `location_info` json DEFAULT NULL COMMENT '位置信息',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_start_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户会话表';

-- 4. 转化漏斗配置表
CREATE TABLE `t_behavior_funnel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `funnel_name` varchar(100) NOT NULL COMMENT '漏斗名称',
  `funnel_code` varchar(50) NOT NULL UNIQUE COMMENT '漏斗代码',
  `description` text DEFAULT NULL COMMENT '漏斗描述',
  `steps` json NOT NULL COMMENT '漏斗步骤配置',
  `time_window` int(11) DEFAULT 86400 COMMENT '时间窗口(秒)',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_funnel_code` (`funnel_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='转化漏斗配置表';

-- 5. 行为分析结果表
CREATE TABLE `t_behavior_analysis` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `analysis_type` varchar(50) NOT NULL COMMENT '分析类型',
  `analysis_name` varchar(100) NOT NULL COMMENT '分析名称',
  `date_range` varchar(20) NOT NULL COMMENT '日期范围',
  `data` json NOT NULL COMMENT '分析结果数据',
  `summary` text DEFAULT NULL COMMENT '分析摘要',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_analysis_type` (`analysis_type`),
  KEY `idx_date_range` (`date_range`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行为分析结果表';

-- 6. 插入默认事件定义数据
INSERT INTO `t_behavior_event` (`event_code`, `event_name`, `event_category`, `description`, `properties_schema`, `is_active`) VALUES
('page_view', '页面访问', 'page', '用户访问页面事件', '{"page_path": "string", "stay_duration": "number", "referrer": "string"}', 1),
('page_leave', '页面离开', 'page', '用户离开页面事件', '{"page_path": "string", "stay_duration": "number"}', 1),
('click', '点击事件', 'interaction', '用户点击元素事件', '{"element_id": "string", "click_position": "object"}', 1),
('scroll', '滚动事件', 'interaction', '用户滚动页面事件', '{"scroll_depth": "number"}', 1),
('product_view', '商品浏览', 'product', '用户浏览商品事件', '{"product_id": "number", "page_path": "string"}', 1),
('add_to_cart', '加入购物车', 'product', '用户添加商品到购物车事件', '{"product_id": "number", "quantity": "number"}', 1),
('remove_from_cart', '从购物车移除', 'product', '用户从购物车移除商品事件', '{"product_id": "number", "quantity": "number"}', 1),
('add_to_favorite', '添加收藏', 'product', '用户收藏商品事件', '{"product_id": "number"}', 1),
('remove_from_favorite', '取消收藏', 'product', '用户取消收藏商品事件', '{"product_id": "number"}', 1),
('order_create', '创建订单', 'order', '用户创建订单事件', '{"order_id": "string", "order_amount": "number"}', 1),
('order_pay', '订单支付', 'order', '用户支付订单事件', '{"order_id": "string", "payment_method": "string"}', 1),
('order_complete', '订单完成', 'order', '订单完成事件', '{"order_id": "string"}', 1),
('search', '搜索', 'search', '用户搜索事件', '{"keyword": "string", "result_count": "number"}', 1),
('search_result_click', '搜索结果点击', 'search', '用户点击搜索结果事件', '{"keyword": "string", "product_id": "number", "position": "number"}', 1),
('page_share', '页面分享', 'social', '用户分享页面事件', '{"share_type": "string", "product_id": "number"}', 1);

-- 7. 插入默认漏斗配置数据
INSERT INTO `t_behavior_funnel` (`funnel_name`, `funnel_code`, `description`, `steps`, `time_window`, `is_active`) VALUES
('商品购买漏斗', 'product_purchase', '从商品浏览到完成购买的转化漏斗', 
'[{"event_type": "product_view", "step_name": "商品浏览"}, {"event_type": "add_to_cart", "step_name": "加入购物车"}, {"event_type": "order_create", "step_name": "创建订单"}, {"event_type": "order_pay", "step_name": "完成支付"}]', 
86400, 1),
('用户注册漏斗', 'user_register', '从访问到完成注册的转化漏斗',
'[{"event_type": "page_view", "step_name": "访问注册页"}, {"event_type": "click", "step_name": "点击注册按钮"}, {"event_type": "order_create", "step_name": "完成注册"}]',
86400, 1);

-- 8. 创建索引优化查询性能
-- 复合索引用于常用查询
CREATE INDEX `idx_user_event_time` ON `t_user_behavior` (`user_id`, `event_type`, `create_time`);
CREATE INDEX `idx_session_event_time` ON `t_user_behavior` (`session_id`, `event_type`, `create_time`);
CREATE INDEX `idx_product_event_time` ON `t_user_behavior` (`product_id`, `event_type`, `create_time`);

-- 9. 创建分区表（可选，用于大数据量场景）
-- ALTER TABLE `t_user_behavior` PARTITION BY RANGE (TO_DAYS(create_time)) (
--     PARTITION p202401 VALUES LESS THAN (TO_DAYS('2024-02-01')),
--     PARTITION p202402 VALUES LESS THAN (TO_DAYS('2024-03-01')),
--     PARTITION p202403 VALUES LESS THAN (TO_DAYS('2024-04-01')),
--     PARTITION p_future VALUES LESS THAN MAXVALUE
-- );

-- 10. 创建视图用于常用查询
CREATE VIEW `v_daily_behavior_stats` AS
SELECT 
    DATE(create_time) as date,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(CASE WHEN event_type = 'page_view' THEN 1 END) as page_views,
    COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
    COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) as add_to_cart,
    COUNT(CASE WHEN event_type = 'order_create' THEN 1 END) as orders
FROM `t_user_behavior`
GROUP BY DATE(create_time);

-- 11. 创建存储过程用于数据清理
DELIMITER //
CREATE PROCEDURE `cleanup_old_behavior_data`(IN days_to_keep INT)
BEGIN
    DECLARE cutoff_date DATE;
    SET cutoff_date = DATE_SUB(CURDATE(), INTERVAL days_to_keep DAY);
    
    DELETE FROM `t_user_behavior` WHERE DATE(create_time) < cutoff_date;
    DELETE FROM `t_behavior_session` WHERE DATE(create_time) < cutoff_date;
    DELETE FROM `t_behavior_analysis` WHERE DATE(create_time) < cutoff_date;
    
    SELECT ROW_COUNT() as deleted_rows;
END //
DELIMITER ;

-- 12. 创建触发器用于自动更新会话信息
DELIMITER //
CREATE TRIGGER `update_session_on_behavior_insert`
AFTER INSERT ON `t_user_behavior`
FOR EACH ROW
BEGIN
    -- 更新或创建会话记录
    INSERT INTO `t_behavior_session` (session_id, user_id, start_time, event_count, device_info)
    VALUES (NEW.session_id, NEW.user_id, FROM_UNIXTIME(NEW.timestamp/1000), 1, NEW.device_info)
    ON DUPLICATE KEY UPDATE
        event_count = event_count + 1,
        update_time = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- 13. 创建事件用于定期清理数据（可选）
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT `cleanup_behavior_data_monthly`
-- ON SCHEDULE EVERY 1 MONTH
-- STARTS CURRENT_TIMESTAMP
-- DO CALL cleanup_old_behavior_data(90);

-- 14. 创建用户权限（根据实际需要调整）
-- GRANT SELECT, INSERT, UPDATE, DELETE ON `t_user_behavior` TO 'behavior_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON `t_behavior_session` TO 'behavior_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON `t_behavior_event` TO 'behavior_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON `t_behavior_funnel` TO 'behavior_user'@'%';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON `t_behavior_analysis` TO 'behavior_user'@'%';

-- 完成
SELECT '行为分析模块数据库迁移完成' as message; 