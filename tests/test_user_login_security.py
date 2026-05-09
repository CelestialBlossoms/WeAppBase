import pytest
from flask import Flask
from werkzeug.security import generate_password_hash


@pytest.fixture
def user_service_module():
    app = Flask(__name__)
    app.config['DATABASE_TYPE'] = 'mysql'
    with app.app_context():
        from backend.user.service.user import UserService
        from backend.user.message import UserMessage
        from kit.exceptions import ServiceBadRequest

        yield UserService, UserMessage, ServiceBadRequest


def test_verify_password_accepts_supported_hash(user_service_module):
    UserService, _, _ = user_service_module
    stored_password = generate_password_hash('secret')

    is_valid, should_upgrade = UserService._verify_password(stored_password, 'secret')

    assert is_valid is True
    assert should_upgrade is False


def test_verify_password_rejects_wrong_password(user_service_module):
    UserService, _, _ = user_service_module
    stored_password = generate_password_hash('secret')

    is_valid, should_upgrade = UserService._verify_password(stored_password, 'wrong')

    assert is_valid is False
    assert should_upgrade is False


def test_verify_password_allows_legacy_plaintext_and_requests_upgrade(user_service_module):
    UserService, _, _ = user_service_module
    is_valid, should_upgrade = UserService._verify_password('legacy-secret', 'legacy-secret')

    assert is_valid is True
    assert should_upgrade is True


class EmptyUserRepository:
    def get_by_username(self, username):
        return None


def test_login_uses_generic_error_for_unknown_user(user_service_module):
    UserService, UserMessage, ServiceBadRequest = user_service_module
    service = UserService(EmptyUserRepository())

    with pytest.raises(ServiceBadRequest) as exc_info:
        service.login({'username': 'missing-user', 'password': 'secret'})

    assert exc_info.value.message == UserMessage.USER_PASSWORD_ERROR
