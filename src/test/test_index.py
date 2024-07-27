from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.database_models import User


client = TestClient(app=app)

def test_index_returns():
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"response": "You are in Home root"}
