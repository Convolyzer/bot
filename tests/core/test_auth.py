from core import AuthManager
from .test_store import get_store


def test_allow():
    store = get_store()
    auth = AuthManager(store)
    assert auth.is_allowed(123)
    auth.allow(123)
    assert auth.is_allowed(123)

def test_disallow():
    store = get_store()
    auth = AuthManager(store)
    auth.allow(123)
    assert auth.is_allowed(123)
    auth.disallow(123)
    assert not auth.is_allowed(123)

def test_multiple_allow():
    store = get_store()
    auth = AuthManager(store)
    auth.allow(123)
    auth.allow(123)

def test_multiple_disallow():
    store = get_store()
    auth = AuthManager(store)
    auth.allow(123)
    auth.disallow(123)
    auth.disallow(123)