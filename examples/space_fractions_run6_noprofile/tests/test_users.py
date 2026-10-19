"""User model tests."""
def test_user_attributes():
    from users.user import User
    u = User(id="u1", username="kid")
    assert u.username == "kid"
