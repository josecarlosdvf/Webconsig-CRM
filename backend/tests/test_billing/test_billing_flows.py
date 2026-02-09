import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_billing_invoice_flow(client, auth_headers):
    payload = {
        "client_id": str(uuid4()),
        "company_id": str(uuid4()),
        "total": 500,
        "currency": "BRL",
        "due_date": "2026-01-05",
    }
    response = await client.post("/api/v1/billing/invoices", json=payload, headers=auth_headers)
    assert response.status_code == 201
    invoice_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/billing/invoices/{invoice_id}/mark-paid", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"
