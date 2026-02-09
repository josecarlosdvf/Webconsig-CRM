import pytest


@pytest.mark.asyncio
async def test_finance_core_flows(client, auth_headers):
    company_payload = {
        "name": "Company",
        "cnpj": "123",
        "trading_name": "Company Trade",
        "address": "Street 1",
    }
    response = await client.post(
        "/api/v1/finance/companies", json=company_payload, headers=auth_headers
    )
    assert response.status_code == 201
    company_id = response.json()["id"]

    account_payload = {"name": "Main", "type": "asset", "currency": "BRL"}
    response = await client.post(
        "/api/v1/finance/accounts", json=account_payload, headers=auth_headers
    )
    assert response.status_code == 201
    account_id = response.json()["id"]

    payment_payload = {
        "account_id": account_id,
        "company_id": company_id,
        "amount": 250,
        "currency": "BRL",
        "method": "pix",
    }
    response = await client.post(
        "/api/v1/finance/payments", json=payment_payload, headers=auth_headers
    )
    assert response.status_code == 201
    payment_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/finance/payments/{payment_id}/confirm", headers=auth_headers
    )
    assert response.status_code == 200

    payable_payload = {
        "company_id": company_id,
        "account_id": account_id,
        "description": "Payable",
        "amount": 120,
        "currency": "BRL",
        "due_date": "2026-01-01",
        "category": "services",
    }
    response = await client.post(
        "/api/v1/finance/payables", json=payable_payload, headers=auth_headers
    )
    assert response.status_code == 201
    payable_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/finance/payables/{payable_id}/pay", headers=auth_headers
    )
    assert response.status_code == 200

    receivable_payload = {
        "company_id": company_id,
        "account_id": account_id,
        "description": "Receivable",
        "amount": 300,
        "currency": "BRL",
        "due_date": "2026-01-10",
        "category": "sales",
        "source_domain": "crm",
        "source_id": payment_id,
    }
    response = await client.post(
        "/api/v1/finance/receivables", json=receivable_payload, headers=auth_headers
    )
    assert response.status_code == 201
    receivable_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/finance/receivables/{receivable_id}/confirm", headers=auth_headers
    )
    assert response.status_code == 200
