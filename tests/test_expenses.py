import pytest
from backend.app.app import app
from backend.app.utils.cache import cache_service

async def test_add_expense_success(auth_client, auth_user):
    payload = {
        "tag_name": "Groceries",
        "amount": 45.50,
        "description": "Weekly grocery shopping",
        "payment_type": "CARD",
        "expense_date": "2026-06-22"
    }
    response = await auth_client.post("/expenses/add_expenses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tag_name"] == "groceries" # tag name gets normalized to lowercase
    assert float(data["amount"]) == 45.50
    assert data["description"] == "Weekly grocery shopping"
    assert data["payment_type"] == "CARD"
    assert "id" in data
    
    # Assert notification email was sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["recipients"] == [auth_user.email]
    assert sent[0]["subject"] == "Your Expense Added Succesfully"
    assert float(sent[0]["context_data"]["amount"]) == 45.50

async def test_view_expenses_success(auth_client, auth_user):
    # Empty expenses returns 404
    empty_resp = await auth_client.get("/expenses/view_expenses")
    assert empty_resp.status_code == 404

    # Add an expense
    payload = {
        "tag_name": "Rent",
        "amount": 1000.00,
        "description": "Monthly rent payment",
        "payment_type": "UPI",
        "expense_date": "2026-06-01"
    }
    add_resp = await auth_client.post("/expenses/add_expenses", json=payload)
    assert add_resp.status_code == 200
    
    # View expenses should fetch from DB and populate cache
    response = await auth_client.get("/expenses/view_expenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tag_name"] == "rent"
    assert float(data[0]["amount"]) == 1000.00
    
    # Verify cached data exists in our mock cache
    cache_key = f"user:{auth_user.id}:expenses"
    cached = cache_service.get(cache_key)
    assert cached is not None
    assert len(cached) == 1
    assert cached[0]["tag_name"] == "rent"

async def test_delete_expense_success(auth_client, auth_user):
    # Add an expense
    payload = {
        "tag_name": "Coffee",
        "amount": 4.50,
        "description": "Morning coffee",
        "payment_type": "CASH",
        "expense_date": "2026-06-22"
    }
    add_resp = await auth_client.post("/expenses/add_expenses", json=payload)
    assert add_resp.status_code == 200
    expense_id = add_resp.json()["id"]
    
    # Check cache has been invalidated (set to None on add_expenses)
    cache_key = f"user:{auth_user.id}:expenses"
    assert cache_service.get(cache_key) is None
    
    # Populating cache by viewing expenses
    await auth_client.get("/expenses/view_expenses")
    assert cache_service.get(cache_key) is not None
    
    # Clear email list before deletion to count emails cleanly
    app.state.sent_emails.clear()

    # Delete the expense
    del_resp = await auth_client.delete(f"/expenses/delete_expense?expenseId={expense_id}")
    assert del_resp.status_code == 200
    assert "Deleted" in del_resp.json()
    
    # Verify cache is invalidated on deletion
    assert cache_service.get(cache_key) is None
    
    # Verify deletion email sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["subject"] == "Your Expense Deleted Succesfully"
    assert sent[0]["context_data"]["id"] == expense_id
    
    # Verify it is no longer in database (view returns 404 since it was the only expense)
    view_resp = await auth_client.get("/expenses/view_expenses")
    assert view_resp.status_code == 404

async def test_delete_expense_not_found(auth_client):
    response = await auth_client.delete("/expenses/delete_expense?expenseId=99999")
    assert response.status_code == 404
