import pytest
from decimal import Decimal
from backend.app.app import app
from backend.app.utils.cache import cache_service

async def test_add_settlement_success(auth_client, auth_user):
    payload = {
        "person_name": "Alice",
        "amount": "50.00",
        "debt_date": "2026-06-22",
        "debt_type": "lent",
        "debt_status": "pending"
    }
    response = await auth_client.post("/settlements/Add_debt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["person_name"] == "Alice"
    assert float(data["amount"]) == 50.00
    assert data["debt_type"] == "lent"
    assert data["debt_status"] == "pending"
    assert "id" in data
    
    # Assert notification email was sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["recipients"] == [auth_user.email]
    assert sent[0]["subject"] == "Your Data Added Succesfully."
    assert sent[0]["context_data"]["person"] == "Alice"

async def test_view_settlements_success(auth_client, auth_user):
    # Empty settlements returns 404
    empty_resp = await auth_client.get("/settlements/View_debt")
    assert empty_resp.status_code == 404

    # Add a debt
    payload = {
        "person_name": "Bob",
        "amount": "120.50",
        "debt_date": "2026-06-20",
        "debt_type": "borrowed",
        "debt_status": "pending"
    }
    await auth_client.post("/settlements/Add_debt", json=payload)
    
    # View debt
    response = await auth_client.get("/settlements/View_debt")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["person_name"] == "Bob"
    assert float(data[0]["amount"]) == 120.50
    
    # Verify cached data exists in mock cache
    cache_key = f"user:{auth_user.id}:settlement"
    cached = cache_service.get(cache_key)
    assert cached is not None
    assert len(cached) == 1
    assert cached[0]["person_name"] == "Bob"

async def test_update_settlement_success(auth_client, auth_user):
    # Add a debt
    payload = {
        "person_name": "Charlie",
        "amount": "80.00",
        "debt_date": "2026-06-22",
        "debt_type": "lent",
        "debt_status": "pending"
    }
    add_resp = await auth_client.post("/settlements/Add_debt", json=payload)
    assert add_resp.status_code == 200
    debt_id = add_resp.json()["id"]
    
    # Update the debt
    update_payload = {
        "person_name": "Charlie",
        "amount": "85.00",
        "debt_type": "lent",
        "debt_status": "paid"
    }
    app.state.sent_emails.clear()
    
    response = await auth_client.put(f"/settlements/update_debt?int_id={debt_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert float(data["amount"]) == 85.00
    assert data["debt_status"] == "paid"
    
    # Verify update email sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["subject"] == "Your Settlement Update Succesfully."
    assert float(sent[0]["context_data"]["amount"]) == 85.00
    assert sent[0]["context_data"]["Status"] == "paid"

async def test_delete_settlement_success(auth_client, auth_user):
    # Add a debt
    payload = {
        "person_name": "David",
        "amount": "200.00",
        "debt_date": "2026-06-22",
        "debt_type": "borrowed",
        "debt_status": "pending"
    }
    add_resp = await auth_client.post("/settlements/Add_debt", json=payload)
    debt_id = add_resp.json()["id"]
    
    # Populate cache by viewing
    await auth_client.get("/settlements/View_debt")
    cache_key = f"user:{auth_user.id}:settlement"
    assert cache_service.get(cache_key) is not None
    
    app.state.sent_emails.clear()

    # Delete the debt
    del_resp = await auth_client.delete(f"/settlements/delete_debt?del_id={debt_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True
    assert del_resp.json()["id"] == debt_id
    
    # Verify cache is invalidated on deletion
    assert cache_service.get(cache_key) is None
    
    # Verify deletion email sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["subject"] == "Your Settlement Update Succesfully."
    assert sent[0]["context_data"]["person"] == "David"
    
    # Verify view returns 404
    view_resp = await auth_client.get("/settlements/View_debt")
    assert view_resp.status_code == 404
