"""Admin tests."""
from admin.admin import Admin


def test_admin_defaults():
    a = Admin()
    assert a.username == "Admin"
    assert a.id
