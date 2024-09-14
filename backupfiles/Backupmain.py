"""Application main file."""
from fastapi import FastAPI, HTTPException, status

from neomodel import DoesNotExist
from database_models import User, Person
from neomodel import config
#from api_models import PersonName, UserCreate, AlbumAPI, ArtistAPI, PlaylistAPI, SongAPI, PlaylistInput
from pydantic import BaseModel
from typing import List, Optional
from api_models import PersonName, UserCreate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
# Read the DATABASE_URL environment variable
config.DATABASE_URL = os.getenv('DATABASE_URL', 'bolt://neo4j:your_password_here@localhost:7687')

# Create app
app = FastAPI(
    title="Neomodels Test App",
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

@app.post("/person")
async def create_person1(node: PersonName):
    try:
        try:
            user = Person.nodes.get(name=node.name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Person1 already in use",
            )
        except Person.DoesNotExist:
            user = User(username=node.name).save()
            if user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="username already in use",
                )
            user = Person(
                name=node.name
        ).save()

    except Exception as exc:
        print(f"Error: {exc}")  
        raise HTTPException(status_code=500, detail="An error occurred while creating user") from exc
    return {"response": f"You have successfully created the user {node.name}"}

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(node: UserCreate):
    try:
        user = User.nodes.get(username=node.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already in use",
            )
        else:
            user = User(
                username=node.username,
                email=node.email,
                first_name=node.first_name,
                last_name=node.last_name
            ).save()
            return {"response": "User created successfully"}
    except Exception as exc:
        print(f"Error: {exc}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from exc


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
    
    