from django.urls import resolve, reverse


def test_token_obtain():
    assert reverse("users:token_obtain_pair") == "/api/token/"
    assert resolve("/api/token/").view_name == "users:token_obtain_pair"


def test_token_refresh():
    assert reverse("users:token_refresh") == "/api/token/refresh/"
    assert resolve("/api/token/refresh/").view_name == "users:token_refresh"


def test_token_verify():
    assert reverse("users:token_verify") == "/api/token/verify/"
    assert resolve("/api/token/verify/").view_name == "users:token_verify"


def test_token_logout():
    assert reverse("users:token_blacklist") == "/api/token/logout/"
    assert resolve("/api/token/logout/").view_name == "users:token_blacklist"
