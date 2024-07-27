from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.database_models import User


client = TestClient(app=app)


def test_create_user():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    # Ensure the user does not exist before the test
    try:
        user = User.nodes.get(username=user_data['username'])
        user.delete()
    except User.DoesNotExist:
        pass  # User does not exist, no need to delete

    # Send a POST request to the /signup endpoint
    response = client.post("/signup", json=user_data)

    # Assert the status code and response content
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"response": f"You have successfully created the user {user_data['username']}"}
    
    # Additional assertions
    user = User.nodes.get(username=user_data['username'])
    assert user.email == user_data['email']
    assert user.first_name == user_data['first_name']
    assert user.last_name == user_data['last_name']

    # Cleanup code
    user.delete()

def test_create_user_conflict():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    # Ensure the user does not exist before the test
    try:
        user = User.nodes.get(username=user_data['username'])
        user.delete()
    except User.DoesNotExist:
        pass  # User does not exist, no need to delete

    # Create the user first
    response = client.post("/signup", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Try to create the same user again
    response = client.post("/signup", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Username already in use"}

    # Cleanup code
    user = User.nodes.get(username=user_data['username'])
    user.delete()