from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "message": "Kara Medical Analytical API is running. Access /docs for interactive documentation."}

def test_top_products_invalid_params():
    # Test that the API handles bad input (limit too high)
    response = client.get("/api/reports/top-products?limit=1000")
    assert response.status_code == 422 # Validation Error