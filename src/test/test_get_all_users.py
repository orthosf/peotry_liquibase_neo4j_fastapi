from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.database_models import User


client = TestClient(app=app)

def test_get_all_users_empty():
    # Ensure no users exist before the test
    users = User.nodes.all()
    for user in users:
        user.delete()

    response = client.get("/allusers")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"response": "No users found in the database"}

def test_get_all_users_non_empty():
    # Ensure no users exist before the test
    users = User.nodes.all()
    for user in users:
        user.delete()

    # Create test users
    user_data1 = {"username": "testuser1", "email": "testuser1@example.com", "first_name": "Test1", "last_name": "User1"}
    user_data2 = {"username": "testuser2", "email": "testuser2@example.com", "first_name": "Test2", "last_name": "User2"}

    user1 = User(username=user_data1['username'], email=user_data1['email'], first_name=user_data1['first_name'], last_name=user_data1['last_name'])
    user2 = User(username=user_data2['username'], email=user_data2['email'], first_name=user_data2['first_name'], last_name=user_data2['last_name'])

    user1.save()
    user2.save()

    response = client.get("/allusers")

    assert response.status_code == status.HTTP_200_OK
    response_data = sorted(response.json(), key=lambda x: x['username'])
    expected_data = sorted([
        {"username": "testuser1"},
        {"username": "testuser2"}
    ], key=lambda x: x['username'])

    assert response_data == expected_data

    # Cleanup code
    user1.delete()
    user2.delete()

#def test_get_all_users_exception(mocker):
    # Mock the User.nodes.all method to raise an exception
    #mocker.patch('src.main.User.nodes.all', side_effect=Exception("Test Exception"))

    #response = client.get("/allusers")

    #assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    #assert response.json() == {"detail": "An error occurred while fetching users"}

