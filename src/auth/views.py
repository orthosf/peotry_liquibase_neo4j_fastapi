from fastapi import APIRouter, Depends, HTTPException, status
from neomodel import DoesNotExist, db
from neomodel.exceptions import DoesNotExist
from .models import User
from .schemas import UserCreate, UserUpdate, UserResponse, UserCreateBatch
from typing import List, Optional

router = APIRouter(prefix="/auth", tags=["auth"])

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

    