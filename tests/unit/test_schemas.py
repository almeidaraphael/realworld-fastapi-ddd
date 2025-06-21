from app.domain.users.models import NewUserRequest, UserResponse


def test_new_user_request_schema() -> None:
    """
    GIVEN a dictionary with user registration data
    WHEN NewUserRequest.model_validate is called
    THEN it should return a NewUserRequest object with the correct fields populated
    """
    data = {"user": {"username": "testuser", "email": "test@example.com", "password": "testpass"}}
    req = NewUserRequest.model_validate(data)
    assert req.user.username == "testuser"
    assert req.user.email == "test@example.com"
    assert req.user.password == "testpass"


def test_user_response_schema() -> None:
    """
    GIVEN a dictionary with user response data
    WHEN UserResponse.model_validate is called
    THEN it should return a UserResponse object with the correct fields populated
    """
    data = {
        "user": {
            "email": "test@example.com",
            "token": "sometoken",
            "username": "testuser",
            "bio": "",
            "image": "",
        }
    }
    resp = UserResponse.model_validate(data)
    assert resp.user.email == "test@example.com"
    assert resp.user.token == "sometoken"
    assert resp.user.username == "testuser"
