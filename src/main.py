"""Application main file."""
from fastapi import FastAPI, HTTPException, status

"""Application main file."""
from fastapi import FastAPI, HTTPException, status
from neomodel import DoesNotExist, config
from .database_models import User, Person
from .api_models import PersonName, UserCreate, UserUpdate
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the DATABASE_URL environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'bolt://neo4j:your_password_here@localhost:7687')
config.DATABASE_URL = DATABASE_URL

# Create app
app = FastAPI(
    title="Poetry Neomodels Fastapi Test App",
    description="Test App using neo4j neomodel database",
    version="0.1",
)

@app.get("/")
def home():
    return {"response": "You are in Home root"}

@app.get("/usercount")
async def user_count():
    users = User.nodes.all()
    return {"# of Users": len(users)}

@app.post("/createperson")
async def create_person(node: PersonName):
    try:
        # Check if user exists
        try:
            user = Person.nodes.get(name=node.name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Person already exist",
            )
        except Person.DoesNotExist:
            user = Person(name=node.name).save()
            return {"response": "Person created successfully"}
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while creating user") from exc
    return {"response": f"You have successfully created the user {node.name}"}
#app.post("/signup", status_code=status.HTTP_201_CREATED, response_model=User)
@app.post("/signup", status_code=status.HTTP_201_CREATED)
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

@app.get("/allusers", status_code=status.HTTP_200_OK)
async def get_all_users():
    try:
        users = User.nodes.all()
        if not users:
            return {"response": "No users found in the database"}
        return [{"username": user.username} for user in users]
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching users") 

@app.put("/updateuser/{username}", status_code=status.HTTP_201_CREATED)
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
@app.get("/persons", status_code=status.HTTP_200_OK)
async def get_all_persons():
    try:
        persons = Person.nodes.all()
        if not persons:
            return {"response": "No persons found in the database"}
        return [{"name": person.name} for person in persons]
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching persons") 
       
@app.post("/userCharlieandOliver", status_code=status.HTTP_201_CREATED)
async def create_user_Charlie_and_Oliver():
    try:
        # Create nodes
        charlie = Person(name='Charlie Sheen').save()
        charlie.add_label('Actor')

        oliver = Person(name='Oliver Stone').save()
        oliver.add_label('Director')
        
        return {"response": "You have successfully created nodes Charlie Sheen and Oliver Stone"}
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while creating nodes") from exc
    
    