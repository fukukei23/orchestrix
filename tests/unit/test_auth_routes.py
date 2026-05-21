"""Auth APIルートのテスト"""


def _register_user(client, username="testuser", email="test@example.com", password="Password123"):
    return client.post("/api/v1/auth/register", json={
        "username": username, "email": email, "password": password
    })


class TestRegister:

    def test_register_success(self, client):
        resp = _register_user(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_username(self, client):
        _register_user(client, username="dup", email="a@b.com")
        resp = _register_user(client, username="dup", email="other@b.com")
        assert resp.status_code == 400

    def test_register_duplicate_email(self, client):
        _register_user(client, username="user1", email="dup@b.com")
        resp = _register_user(client, username="user2", email="dup@b.com")
        assert resp.status_code == 400


class TestLogin:

    def test_login_success(self, client):
        _register_user(client, username="loginuser", password="MyPass123")
        resp = client.post("/api/v1/auth/login", json={
            "username": "loginuser", "password": "MyPass123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        _register_user(client, username="user1", password="Correct123")
        resp = client.post("/api/v1/auth/login", json={
            "username": "user1", "password": "WrongPass"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "ghost", "password": "nopass"
        })
        assert resp.status_code == 401


class TestGetCurrentUser:

    def test_me_with_valid_token(self, client):
        reg = _register_user(client, username="meuser")
        user_id = reg.json()["id"]

        login = client.post("/api/v1/auth/login", json={
            "username": "meuser", "password": "Password123"
        })
        token = login.json()["access_token"]

        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert resp.status_code == 200
        assert resp.json()["username"] == "meuser"

    def test_me_without_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 403

    def test_me_with_invalid_token(self, client):
        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        assert resp.status_code in [401, 403]


class TestLogout:

    def test_logout_success(self, client):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert "message" in resp.json()
