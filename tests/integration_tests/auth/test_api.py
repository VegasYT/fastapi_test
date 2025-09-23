import pytest


@pytest.mark.parametrize("email, password, first_name, last_name, status_code", [
    ("putin@kremlin.ru", "pass", "Владимир", "Путин", 200),
    ("putin@kremlin.ru", "pass", "Владимир", "Путин", 400),
    ("zel@mail.ua", None, "Кхе", "Кхе", 422),
])
async def test_auth_flow(
        email, password, first_name, last_name, status_code,
        db, ac
):
    reg_resp = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
    )
    assert reg_resp.status_code == status_code

    if status_code == 200:
        await ac.post(
            "/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        assert ac.cookies["access_token"]

        me_resp = await ac.get("/auth/me")
        me_data = me_resp.json()
        assert me_data["email"] == email
        assert me_data["first_name"] == first_name
        assert me_data["last_name"] == last_name

        logout_resp = await ac.post("/auth/logout")
        assert logout_resp.status_code == 200

        me_logout_resp = await ac.get("/auth/me")
        assert me_logout_resp.status_code == 401
        assert "access_token" not in ac.cookies