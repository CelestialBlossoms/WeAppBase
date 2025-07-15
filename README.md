# 起源小程序后端系统

![License](https://img.shields.io/badge/license-IKAS-blue.svg)
![Python](https://img.shields.io/badge/python-3.9-green.svg)
![Flask](https://img.shields.io/badge/flask-2.1.2-red.svg)

## 项目简介

起源小程序后端系统是一个基于Flask框架的综合性电商小程序后端服务，主要面向微信小程序提供完整的电商业务支持。系统采用现代化的微服务架构设计，支持商品管理、订单处理、用户管理、分销系统、支付集成等核心功能。

### 主要特性

- 🛒 **完整电商功能** - 商品管理、购物车、订单处理、库存管理
- 📱 **微信小程序集成** - 微信登录、微信支付、小程序授权
- 💰 **分销系统** - 多级分销、佣金结算、等级管理
- 🏪 **多门店支持** - 门店管理、配送设置、营业时间配置
- 📊 **数据分析** - 仪表盘统计、销售分析、用户行为分析
- 🔐 **权限管理** - 基于RBAC的角色权限控制
- 📦 **物流管理** - 订单跟踪、物流信息、配送状态
- 🎫 **会员系统** - 等级管理、积分体系、优惠券
- 📈 **行为分析** - 用户行为追踪、转化漏斗分析、个性化推荐

## 技术栈

### 后端框架
- **Flask** - 轻量级Web框架
- **Flask-SQLAlchemy** - ORM数据库操作
- **Flask-Migrate** - 数据库迁移工具
- **Flask-JWT-Extended** - JWT身份认证
- **Flask-Smorest** - RESTful API文档生成

### 数据库
- **MySQL** - 主数据库
- **Redis** - 缓存和会话存储
- **Oracle** - 企业数据库支持（可选）

### 异步任务
- **Celery** - 分布式任务队列
- **RabbitMQ** - 消息队列中间件

### 第三方集成
- **微信支付** - 支付接口集成
- **顺丰速运** - 物流API集成
- **Apache SkyWalking** - 应用性能监控

### 部署工具
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排
- **Gunicorn** - WSGI HTTP服务器

## 项目结构

```
mini_code/
├── backend/                    # 主要业务模块
│   ├── alarm/                 # 报警服务
│   ├── business/              # 业务服务
│   ├── license_management/    # 许可证管理
│   ├── log/                   # 日志服务
│   ├── mini_core/             # 小程序核心功能
│   │   ├── api/              # API接口层
│   │   ├── domain/           # 领域模型
│   │   ├── repository/       # 数据访问层
│   │   ├── service/          # 业务逻辑层
│   │   └── schema/           # 数据验证模式
│   ├── behavior_analysis/     # 行为分析模块
│   │   ├── api/              # 行为分析API
│   │   ├── domain/           # 行为分析领域模型
│   │   ├── repository/       # 行为数据存储
│   │   ├── service/          # 行为分析服务
│   │   └── schema/           # 行为数据验证
│   ├── role/                  # 角色权限管理
│   └── user/                  # 用户管理
├── kit/                       # 工具库
│   ├── domain/               # 领域基础组件
│   ├── repository/           # 仓储模式基类
│   ├── service/              # 服务基类
│   ├── util/                 # 工具函数
│   └── wechatpayv3/          # 微信支付v3 SDK
├── task/                      # 异步任务
├── conf/                      # 配置文件
├── migrations/                # 数据库迁移文件
├── tests/                     # 测试文件
└── requirements/              # 依赖管理
```

## 核心功能模块

### 1. 用户管理系统
- 微信小程序用户授权登录
- 用户信息管理和更新
- 收货地址管理
- 会员等级体系

### 2. 商品管理系统
- 商品信息管理（CRUD）
- 商品分类管理
- 规格属性管理
- 库存管理和预警
- 商品图片和视频管理

### 3. 订单管理系统
- 订单创建和状态管理
- 订单详情和日志记录
- 订单退货退款处理
- 订单配置和设置

### 4. 支付系统
- 微信支付集成（JSAPI、小程序支付）
- 支付回调处理
- 支付状态同步
- 退款处理

### 5. 分销系统
- 多级分销管理
- 分销商等级配置
- 佣金计算和结算
- 提现申请处理

### 6. 门店管理
- 门店信息管理
- 营业时间配置
- 配送范围设置
- 门店服务模式（外卖/自取/堂食）

### 7. 物流管理
- 订单发货管理
- 物流信息跟踪
- 配送状态更新
- 物流公司对接

### 8. 权限管理
- 基于RBAC的权限控制
- 角色和权限管理
- 菜单权限配置
- API接口权限验证

### 9. 行为分析系统 🆕
- **用户行为追踪** - 页面访问、点击事件、停留时长
- **转化漏斗分析** - 用户路径分析、转化率统计
- **商品行为分析** - 商品浏览、收藏、加购、购买行为
- **用户画像分析** - 用户偏好、消费习惯、活跃度分析
- **实时数据监控** - 实时用户行为数据展示
- **数据可视化** - 图表展示、趋势分析、对比分析
- **个性化推荐** - 基于用户行为的商品推荐

## 行为分析模块详细说明

### 功能特性
1. **数据采集**
   - 前端自动埋点收集用户行为数据
   - 支持自定义事件追踪
   - 实时数据上传和批量处理

2. **数据分析**
   - 用户行为路径分析
   - 转化漏斗分析
   - 商品热度分析
   - 用户留存分析

3. **数据展示**
   - 实时数据大屏
   - 多维度图表展示
   - 自定义报表生成
   - 数据导出功能

### API接口
- `POST /api/v1/behavior/track` - 行为数据上报
- `GET /api/v1/behavior/overview` - 行为概览数据
- `GET /api/v1/behavior/funnel` - 转化漏斗分析
- `GET /api/v1/behavior/user-path` - 用户路径分析
- `GET /api/v1/behavior/product-analysis` - 商品行为分析
- `GET /api/v1/behavior/user-portrait` - 用户画像分析

### 数据库设计
- `t_user_behavior` - 用户行为记录表
- `t_behavior_event` - 行为事件定义表
- `t_behavior_session` - 用户会话表
- `t_behavior_funnel` - 转化漏斗配置表
- `t_behavior_analysis` - 行为分析结果表

## 安装部署

### 环境要求

- Python 3.9+
- MySQL 5.8+
- Redis 5.0+
- Docker & Docker Compose（推荐）

### 开发环境安装

#### 1. 使用Poetry（推荐）

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

#### 2. 使用pip

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置文件

复制环境配置文件并修改相关配置：

```bash
.env
```

配置数据库连接、Redis连接、微信小程序配置等：

```env
# 数据库配置
DEV_DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 微信小程序配置
WECHAT_MULTIPLATFORM_APPID=your_wechat_appid
WECHAT_MULTIPLATFORM_SECRET=your_wechat_secret

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key

# 行为分析配置
BEHAVIOR_ANALYSIS_ENABLED=true
BEHAVIOR_DATA_RETENTION_DAYS=90
BEHAVIOR_REAL_TIME_ENABLED=true
```

### 数据库初始化

```bash
# 初始化数据库迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

## 使用指南

### 行为分析模块使用

#### 1. 前端数据上报
```javascript
// 页面访问事件
wx.request({
  url: '/api/v1/behavior/track',
  method: 'POST',
  data: {
    event_type: 'page_view',
    page_path: '/pages/product/detail',
    product_id: 123,
    user_id: 'user_123',
    session_id: 'session_456',
    timestamp: Date.now(),
    properties: {
      stay_duration: 30000,
      scroll_depth: 0.8
    }
  }
});

// 点击事件
wx.request({
  url: '/api/v1/behavior/track',
  method: 'POST',
  data: {
    event_type: 'click',
    element_id: 'add_to_cart_btn',
    product_id: 123,
    user_id: 'user_123',
    session_id: 'session_456',
    timestamp: Date.now()
  }
});
```

#### 2. 数据分析查询
```bash
# 获取行为概览
curl -X GET "http://localhost:5000/api/v1/behavior/overview?date_range=7d"

# 获取转化漏斗
curl -X GET "http://localhost:5000/api/v1/behavior/funnel?funnel_id=product_purchase"

# 获取用户路径分析
curl -X GET "http://localhost:5000/api/v1/behavior/user-path?user_id=123"
```

## 开发规范

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写完整的文档字符串
- 单元测试覆盖率不低于80%

### 数据库规范
- 使用下划线命名法
- 所有表名以`t_`开头
- 字段名使用下划线分隔
- 必须包含创建时间和更新时间字段

### API规范
- 使用RESTful API设计
- 统一响应格式
- 完整的错误处理
- API版本控制

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目地址: [https://github.com/your-username/wx_app_backend]

## 更新日志

### v2.0.0 (2024-01-XX)
- ✨ 新增行为分析模块
- 📊 新增用户行为追踪功能
- 📈 新增转化漏斗分析
- 🎯 新增个性化推荐系统
- 🔧 优化数据库性能
- 🐛 修复已知问题

### v1.0.0 (2023-XX-XX)
- 🎉 初始版本发布
- ✅ 基础电商功能
- ✅ 微信小程序集成
- ✅ 分销系统
- ✅ 权限管理

