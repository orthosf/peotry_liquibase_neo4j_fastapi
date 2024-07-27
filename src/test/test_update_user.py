from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.database_models import User


client = TestClient(app=app)

def test_update_user_success():
    # First, create a user to update
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    try:
        user = User.nodes.get(username=user_data['username'])
        user.delete()
    except User.DoesNotExist:
        pass  # User does not exist, no need to delete

    user = User(username=user_data['username'], email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'])
    user.save()

    # Define the update payload
    update_data = {
        "email": "newemail@example.com",
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName"
    }

    # Send a PUT request to the /updateuser endpoint
    response = client.put(f"/updateuser/{user_data['username']}", json=update_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"response": f"User {user_data['username']} has been updated"}

    # Verify that the user was updated correctly
    updated_user = User.nodes.get(username=user_data['username'])
    assert updated_user.email == update_data['email']
    assert updated_user.first_name == update_data['first_name']
    assert updated_user.last_name == update_data['last_name']

    updated_user.delete()

def test_update_user_not_found():
    # Define the update payload
    update_data = {
        "email": "newemail@example.com",
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName"
    }

    # Send a PUT request to the /updateuser endpoint with a non-existing username
    response = client.put("/updateuser/nonexistentuser", json=update_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

#def test_update_user_exception(mocker):
    # Mock the User.nodes.get method to raise an exception
#    mocker.patch('src.database_models.User.nodes.get', side_effect=Exception("Test Exception"))

    # Define the update payload
#   update_data = {
#        "email": "newemail@example.com",
#        "first_name": "UpdatedFirstName",
#        "last_name": "UpdatedLastName"
#   }

    # Send a PUT request to the /updateuser endpoint
#    response = client.put("/updateuser/someuser", json=update_data)

#    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#    assert response.json() == {"detail": "An error occurred while updating user"}