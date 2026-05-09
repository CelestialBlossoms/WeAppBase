"""根据 SQLAlchemy metadata 创建项目表

Revision ID: 0001_create_project_tables
Revises:
Create Date: 2026-05-09 00:00:00
"""
from alembic import op

from backend.extensions import db
from backend.migration_models import load_project_models


revision = '0001_create_project_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """创建当前项目 metadata 中声明的所有表。"""
    load_project_models()
    bind = op.get_bind()
    db.metadata.create_all(bind=bind, checkfirst=True)


def downgrade():
    """删除当前项目 metadata 中声明的所有表。"""
    load_project_models()
    bind = op.get_bind()
    db.metadata.drop_all(bind=bind, checkfirst=True)
