import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_sales_opportunity_flow(client, auth_headers):
    payload = {
        "title": "Opportunity",
        "client_id": str(uuid4()),
        "value": 1000,
        "currency": "BRL",
    }
    response = await client.post(
        "/api/v1/sales/opportunities", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    opportunity_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/sales/opportunities/{opportunity_id}/stage",
        json={"stage": "proposal"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["stage"] == "proposal"
