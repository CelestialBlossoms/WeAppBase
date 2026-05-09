# WeAppBase

## 项目说明

这是一个基于 Flask、SQLAlchemy、Celery、Redis 和 MySQL 的后端项目。

- Web 启动入口：`autoapp.py`
- Celery 启动入口：`celery_worker.py`
- 数据库迁移入口：`migrate_app.py`
- 容器工作目录：`/app`

## 数据库迁移

项目使用 Flask-Migrate 管理数据库结构。

当前项目的表结构采用 SQLAlchemy classical mapping 方式定义，表定义主要分布在：

```text
backend/**/repository/**/sqla.py
backend/**/repository/**/*_sql.py
```

这些表不是通过声明式 `db.Model` 定义的，所以迁移入口会先通过
`backend/migration_models.py` 导入所有表定义模块，再让 Alembic 读取
`mapper_registry.metadata` 中的完整表结构。

### 初始化数据库表

先确保 MySQL 中已经创建好目标数据库，然后在容器内执行：

```bash
FLASK_APP=migrate_app.py python -m flask db upgrade
```

如果通过 Docker Compose 执行：

```bash
docker compose run --rm -e FLASK_APP=migrate_app.py web python -m flask db upgrade
```

不要重复执行：

```bash
flask db init
```

因为项目已经包含 `migrations/` 目录，重复初始化会报：

```text
Directory migrations already exists and is not empty
```

### 查看当前迁移版本

```bash
FLASK_APP=migrate_app.py python -m flask db current
```

### 后续新增迁移

修改 SQLAlchemy 表结构后，执行：

```bash
FLASK_APP=migrate_app.py python -m flask db migrate -m "描述本次结构变更"
FLASK_APP=migrate_app.py python -m flask db upgrade
```


