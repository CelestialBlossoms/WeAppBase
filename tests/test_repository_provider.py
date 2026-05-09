from kit.repository.provider import override_repositories, repository


class DummyRepository:
    def __init__(self, session):
        self.session = session

    def get_session(self):
        return self.session


class FakeRepository:
    def get_session(self):
        return 'fake-session'


def test_repository_proxy_uses_session_factory():
    repo = repository(
        DummyRepository,
        'dummy_repo',
        session_factory=lambda: 'test-session',
    )

    assert repo.get_session() == 'test-session'


def test_repository_proxy_can_be_overridden():
    repo = repository(
        DummyRepository,
        'dummy_repo',
        session_factory=lambda: 'real-session',
    )

    with override_repositories(dummy_repo=FakeRepository()):
        assert repo.get_session() == 'fake-session'

    assert repo.get_session() == 'real-session'
