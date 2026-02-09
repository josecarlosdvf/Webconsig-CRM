import pytest


@pytest.mark.asyncio
async def test_audit_logs(client, auth_headers):
    payload = {
        "name": "Audit Client",
        "email": "audit@example.com",
        "phone": "555-3333",
        "document": "999",
    }
    response = await client.post("/api/v1/crm/clients", json=payload, headers=auth_headers)
    assert response.status_code == 201
    client_id = response.json()["id"]

    response = await client.get("/api/v1/audit/logs", headers=auth_headers)
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/audit/logs/clients/{client_id}", headers=auth_headers
    )
    assert response.status_code == 200
