import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["service"] == "fastapi-development-template"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["service"] == "fastapi-development-template"


class TestItemsCRUD:
    def test_create_item(self):
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 100.0,
            "tax": 10.0,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] == item_data["description"]
        assert data["price"] == item_data["price"]
        assert data["tax"] == item_data["tax"]
        assert data["total_price"] == 110.0
        assert "id" in data

    def test_create_item_without_tax(self):
        item_data = {
            "name": "Test Item Without Tax",
            "description": "A test item without tax",
            "price": 50.0,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 200
        data = response.json()
        assert data["total_price"] == 50.0
        assert data["tax"] is None

    def test_get_item(self):
        item_data = {"name": "Get Test Item", "price": 75.0}
        create_response = client.post("/items", json=item_data)
        item_id = create_response.json()["id"]

        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["price"] == item_data["price"]

    def test_get_nonexistent_item(self):
        response = client.get("/items/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"

    def test_list_items(self):
        response = client.get("/items")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_item(self):
        item_data = {"name": "Delete Test Item", "price": 25.0}
        create_response = client.post("/items", json=item_data)
        item_id = create_response.json()["id"]

        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Item deleted successfully"

        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_item(self):
        response = client.delete("/items/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_lifespan_context():
    from app.main import lifespan

    messages = []

    class MockApp:
        pass

    mock_app = MockApp()

    async with lifespan(mock_app):
        pass