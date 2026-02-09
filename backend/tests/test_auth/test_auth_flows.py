import pytest


@pytest.mark.asyncio
async def test_auth_flow(client, auth_headers):
    role_payload = {"name": "admin"}
    response = await client.post("/api/v1/auth/roles", json=role_payload, headers=auth_headers)
    assert response.status_code == 201
    role_id = response.json()["id"]

    user_payload = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "secret",
        "role_ids": [role_id],
    }
    response = await client.post("/api/v1/auth/users", json=user_payload, headers=auth_headers)
    assert response.status_code == 201
    user_id = response.json()["id"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "user1", "password": "secret"},
        headers={"X-Tenant-Id": auth_headers["X-Tenant-Id"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]

    response = await client.post(
        f"/api/v1/auth/users/{user_id}/change-password",
        json={"password": "new-secret"},
        headers=auth_headers,
    )
    assert response.status_code == 204
