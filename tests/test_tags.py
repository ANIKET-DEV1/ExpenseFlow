import pytest

async def test_view_tags_empty_404(auth_client):
    response = await auth_client.get("/tags/view_tags")
    assert response.status_code == 404
    assert response.json()["detail"] == "No tags available in your account."

async def test_add_tag_success(auth_client):
    payload = {"tag_name": "Food"}
    response = await auth_client.post("/tags/add_tags", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["Message"] == "Succesfully Added"
    assert data["tag"]["tag_name"] == "food" # tag name gets lowercased
    assert "id" in data["tag"]

async def test_view_tags_success(auth_client):
    # Add a tag
    await auth_client.post("/tags/add_tags", json={"tag_name": "travel"})
    
    # View tags
    response = await auth_client.get("/tags/view_tags")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tag_name"] == "travel"

async def test_delete_tag_success(auth_client):
    # Add a tag
    await auth_client.post("/tags/add_tags", json={"tag_name": "entertainment"})
    
    # Delete the tag
    response = await auth_client.delete("/tags/delete_tag?tag=entertainment")
    assert response.status_code == 200
    assert response.json()["Message"] == "Deleted"
    
    # Verify it is deleted
    view_resp = await auth_client.get("/tags/view_tags")
    assert view_resp.status_code == 404

async def test_delete_tag_not_found(auth_client):
    response = await auth_client.delete("/tags/delete_tag?tag=nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "No data found"
