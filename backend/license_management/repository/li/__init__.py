# -*- coding: utf-8 -*-
# author zyy
# from .mock import LiMockRepository
from kit.repository.provider import repository

li_mock_repo = repository('backend.license_management.repository.li.sqla:LiSQLARepository', 'li_mock_repo')
