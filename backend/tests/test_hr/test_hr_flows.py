import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_hr_core_flows(client, auth_headers):
    employee_payload = {
        "name": "Employee",
        "email": "emp@example.com",
        "phone": "555-1111",
        "document": "321",
        "department": "IT",
        "role": "Dev",
        "company_id": str(uuid4()),
        "hired_at": "2026-01-01",
    }
    response = await client.post(
        "/api/v1/hr/employees", json=employee_payload, headers=auth_headers
    )
    assert response.status_code == 201
    employee_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/hr/employees/{employee_id}/terminate",
        json={"reason": "end"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    recruitment_payload = {
        "position": "Analyst",
        "department": "IT",
        "description": "Role",
        "vacancies": 1,
    }
    response = await client.post(
        "/api/v1/hr/recruitments", json=recruitment_payload, headers=auth_headers
    )
    assert response.status_code == 201
    recruitment_id = response.json()["id"]

    candidate_payload = {
        "recruitment_id": recruitment_id,
        "name": "Candidate",
        "email": "cand@example.com",
        "phone": "555-2222",
        "resume_url": None,
    }
    response = await client.post(
        "/api/v1/hr/candidates", json=candidate_payload, headers=auth_headers
    )
    assert response.status_code == 201
    candidate_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/hr/candidates/{candidate_id}/advance",
        json={"stage": "interview"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    absence_payload = {"employee_id": employee_id, "date": "2026-01-02", "reason": "sick"}
    response = await client.post(
        "/api/v1/hr/absences", json=absence_payload, headers=auth_headers
    )
    assert response.status_code == 201

    time_entry_payload = {
        "employee_id": employee_id,
        "date": "2026-01-03",
        "type": "late",
        "minutes": 10,
        "description": "late",
    }
    response = await client.post(
        "/api/v1/hr/time-entries", json=time_entry_payload, headers=auth_headers
    )
    assert response.status_code == 201
    time_entry_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/hr/time-entries/{time_entry_id}/approve", headers=auth_headers
    )
    assert response.status_code == 200

    leave_payload = {
        "employee_id": employee_id,
        "start_date": "2026-01-10",
        "end_date": "2026-01-15",
        "type": "vacation",
        "reason": "rest",
    }
    response = await client.post(
        "/api/v1/hr/leave-requests", json=leave_payload, headers=auth_headers
    )
    assert response.status_code == 201
    leave_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/hr/leave-requests/{leave_id}/approve", headers=auth_headers
    )
    assert response.status_code == 200

    document_payload = {
        "employee_id": employee_id,
        "type": "medical_certificate",
        "description": "doc",
        "file_url": "https://example.com/doc.pdf",
    }
    response = await client.post(
        "/api/v1/hr/documents", json=document_payload, headers=auth_headers
    )
    assert response.status_code == 201

    contract_payload = {
        "employee_id": employee_id,
        "company_id": str(uuid4()),
        "type": "clt",
        "start_date": "2026-01-01",
        "end_date": None,
        "salary": 1000,
        "currency": "BRL",
    }
    response = await client.post(
        "/api/v1/hr/contracts", json=contract_payload, headers=auth_headers
    )
    assert response.status_code == 201

    benefit_payload = {"type": "vr", "description": "meal", "value": 50, "currency": "BRL"}
    response = await client.post(
        "/api/v1/hr/benefits", json=benefit_payload, headers=auth_headers
    )
    assert response.status_code == 201
    benefit_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/hr/benefits/{benefit_id}/assign",
        json={"employee_id": employee_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
