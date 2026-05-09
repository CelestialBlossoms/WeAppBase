"""轻量级 repository provider。

业务代码历史上直接在各模块 ``__init__.py`` 中创建 repository 全局实例。
这里保留原有导入名称，但把实例改成延迟代理，方便测试替换 session 或 mock repo。
"""
from contextlib import contextmanager
from contextvars import ContextVar
from importlib import import_module
from typing import Any, Callable, Dict, Iterator, Optional, Type, Union


_repo_overrides: ContextVar[Dict[str, Any]] = ContextVar(
    'repo_overrides', default={}
)


def default_session_factory():
    """延迟获取 db.session，避免导入 repository 时立即绑定真实 session。"""
    from backend.extensions import db

    return db.session


class LazyRepositoryProxy:
    """按需创建 repository，并支持测试时覆盖为 mock 对象。"""

    def __init__(
        self,
        repo_cls: Union[Type, str],
        name: str,
        session_factory: Callable[[], Any] = default_session_factory,
    ):
        self._repo_cls = repo_cls
        self._name = name
        self._session_factory = session_factory

    def _load_repo_cls(self) -> Type:
        if not isinstance(self._repo_cls, str):
            return self._repo_cls

        module_name, class_name = self._repo_cls.split(':', 1)
        repo_cls = getattr(import_module(module_name), class_name)
        self._repo_cls = repo_cls
        return repo_cls

    @property
    def name(self) -> str:
        return self._name

    def resolve(self):
        override = _repo_overrides.get().get(self._name)
        if override is not None:
            return override
        return self._load_repo_cls()(self._session_factory())

    def __getattr__(self, item: str):
        return getattr(self.resolve(), item)


def repository(
    repo_cls: Union[Type, str],
    name: Optional[str] = None,
    session_factory: Callable[[], Any] = default_session_factory,
) -> LazyRepositoryProxy:
    return LazyRepositoryProxy(repo_cls, name or repo_cls.__name__, session_factory)


@contextmanager
def override_repositories(**repositories: Any) -> Iterator[None]:
    """临时替换 repository，主要用于单元测试。"""
    current = dict(_repo_overrides.get())
    current.update(repositories)
    token = _repo_overrides.set(current)
    try:
        yield
    finally:
        _repo_overrides.reset(token)
