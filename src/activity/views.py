from fastapi import APIRouter, Depends, HTTPException, status
from neomodel import DoesNotExist, db
from neomodel.exceptions import DoesNotExist
from ..auth.models import User
from .schemas import  UserFollow
from ..auth.schemas import UserCreate, UserUpdate, UserResponse, UserCreateBatch
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("/usercount")
async def user_count():
    users = User.nodes.all()
    return {"# of Users": len(users)}

#app.post("/signup", status_code=status.HTTP_201_CREATED, response_model=User)
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(node: UserCreate):
    try:
        # Check if user exists
        try:
            user = User.nodes.get(username=node.username)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already in use",
            )
        except User.DoesNotExist:
            user = User(
                username=node.username,
                email=node.email,
                first_name=node.first_name,
                last_name=node.last_name
            ).save()
    except HTTPException as http_exc:
        raise http_exc  # Re-raise the HTTP exception for conflicts
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while creating user") from exc
    return {"response": f"You have successfully created the user {node.username}"}

@router.post("/create-multiple-users", response_model=List[UserResponse])
async def create_multiple_users(users_batch: UserCreateBatch):
    successful_users = []
    failed_users = []

    for user_data in users_batch.users:
        try:
            user = User.nodes.get(username=user_data.username)
            failed_users.append(UserResponse(
                username=user_data.username,
                status="conflict",
                detail=f"Username {user_data.username} already in use"
            ))
        except User.DoesNotExist:
            try:
                user = User(
                    username=user_data.username,
                    email=user_data.email,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name
                ).save()
                successful_users.append(UserResponse(
                    username=user_data.username,
                    status="created"
                ))
            except Exception as exc:
                failed_users.append(UserResponse(
                    username=user_data.username,
                    status="failed",
                    detail=str(exc)
                ))

    return successful_users + failed_users

@router.get("/allusers", status_code=status.HTTP_200_OK)
async def get_all_users():
    try:
        users = User.nodes.all()
        if not users:
            return {"response": "No users found in the database"}
        return [{"username": user.username} for user in users]
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching users") 

@router.get("/nplus1problem", status_code=status.HTTP_200_OK)
async def nplus1problem():
    try:
        users = User.nodes.all()
        if not users:
            return {"response": "No users found in the database"}
        return [{"username": user.username,"followers": [f.username for f in user.followers.all()]} for user in users]
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching users") 
    
@router.get("/nplus1solution", status_code=status.HTTP_200_OK)
async def nplus1solution():
    try:
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)<-[:FOLLOWING]-(f:User)
        RETURN u.username as username, collect(f.username) as followers
        """
        results, _ = db.cypher_query(query)
        users = [{"username": row[0], "followers": row[1]} for row in results]
        
        if not users:
            return {"response": "No users found in the database"}
        return users
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching users")
    
@router.put("/updateuser/{username}", status_code=status.HTTP_201_CREATED)
async def update_user(username: str, update: UserUpdate):
    print(f"Received payload: {update}")
    try:
        user = User.nodes.get(username=username)
        print(f"User found: {user}")
        if update.email:
            user.email = update.email
        if update.first_name:
            user.first_name = update.first_name
        if update.last_name:
            user.last_name = update.last_name
        user.save()
        return {"response": f"User {username} has been updated"}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while updating user") from exc
    #return [{"response": f"You have successfully updated the user {user.username}"} for user in users]
    #return {"response": f"You have successfully updated the user {user.username}"}


@router.post("/follow/{username}", status_code=status.HTTP_201_CREATED)
async def follow_user(username: str, follow: UserFollow):
    try:
        # Retrieve the user who wants to follow
        try:
            user = User.nodes.get(username=username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve the target user to be followed
        try:
            target_user = User.nodes.get(username=follow.target_username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Target user not found")

        # Establish the "following" relationship
        user.following.connect(target_user)

        return {"message": f"{username} is now following {follow.target_username}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/followerneomodels/{username}", status_code=status.HTTP_200_OK)
async def get_following(username: str):
    try:
        # Retrieve the user who is following others
        try:
            user = User.nodes.get(username=username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve all users that the user is following
        followers_users = user.followers.all()  # This uses the following relationship defined in User
        followers_usernames = [f.username for f in followers_users]

        return {"following": followers_usernames}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/followers/{username}", status_code=status.HTTP_200_OK)
async def get_followers(username: str):
    try:
        # Check if the target user exists
        try:
            target_user = User.nodes.get(username=username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve all users who follow the target user using a Cypher query
        query = """
        MATCH (u:User)-[:FOLLOWING]->(target:User {username: $username})
        RETURN u
        """
        results, _ = db.cypher_query(query, {'username': username})

        # Inflate the results to User objects
        followers = [User.inflate(row[0]) for row in results]
        followers_usernames = [f.username for f in followers]

        return {"followers": followers_usernames}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/following/{username}", status_code=status.HTTP_200_OK)
async def get_following(username: str):
    try:
        # Retrieve the user who is following others
        try:
            user = User.nodes.get(username=username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve all users that the user is following
        following_users = user.following.all()  # This uses the following relationship defined in User
        following_usernames = [f.username for f in following_users]

        return {"following": following_usernames}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/unfollow/{username}", status_code=status.HTTP_200_OK)
async def unfollow_user(username: str, target_username: str):
    try:
        # Retrieve the user who wants to unfollow
        try:
            user = User.nodes.get(username=username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        # Retrieve the target user to be unfollowed
        try:
            target_user = User.nodes.get(username=target_username)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Target user not found")

        # Check if the relationship exists and disconnect it
        if user.following.is_connected(target_user):
            user.following.disconnect(target_user)
            return {"message": f"{username} has unfollowed {target_username}"}
        else:
            raise HTTPException(status_code=404, detail="User is not following the target user")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    