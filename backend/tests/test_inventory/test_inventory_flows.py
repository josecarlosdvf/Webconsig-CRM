import pytest


@pytest.mark.asyncio
async def test_inventory_flow(client, auth_headers):
    payload = {"sku": "SKU-1", "name": "Item", "unit": "unit"}
    response = await client.post("/api/v1/inventory/items", json=payload, headers=auth_headers)
    assert response.status_code == 201
    item_id = response.json()["id"]

    response = await client.patch(
        f"/api/v1/inventory/items/{item_id}",
        json={"status": "inactive"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    adjustment = {"item_id": item_id, "delta": 10, "reason": "init"}
    response = await client.post(
        "/api/v1/inventory/stock-adjustments", json=adjustment, headers=auth_headers
    )
    assert response.status_code == 204
