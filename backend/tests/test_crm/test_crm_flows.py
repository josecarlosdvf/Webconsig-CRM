import pytest


@pytest.mark.asyncio
async def test_crm_clients_and_leads_flow(client, auth_headers):
    create_client = {
        "name": "Client One",
        "email": "client@example.com",
        "phone": "555-0001",
        "document": "123",
    }
    response = await client.post("/api/v1/crm/clients", json=create_client, headers=auth_headers)
    assert response.status_code == 201
    client_id = response.json()["id"]

    response = await client.get("/api/v1/crm/clients", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1

    create_lead = {
        "name": "Lead One",
        "email": "lead@example.com",
        "phone": "555-0002",
        "source": "site",
    }
    response = await client.post("/api/v1/crm/leads", json=create_lead, headers=auth_headers)
    assert response.status_code == 201
    lead_id = response.json()["id"]

    response = await client.post(f"/api/v1/crm/leads/{lead_id}/convert", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"]

    response = await client.get(f"/api/v1/crm/clients/{client_id}", headers=auth_headers)
    assert response.status_code == 200
