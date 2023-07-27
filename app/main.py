from fastapi import FastAPI, Depends, HTTPException, Response, Form, Cookie, Request
from fastapi.security import OAuth2PasswordBearer

import json
from jose import jwt

from sqlalchemy.orm import Session

from pydantic import BaseModel
from typing import List

from .database import SessionLocal, Base, engine 
from .users_repository import User, UsersRepository, UserCreate
from .flowers_repository import Flower, FlowersRepository, FlowerCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()
users_repository = UsersRepository()
flowers_repository = FlowersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def encode_jwt(user_id: int) -> str:
    payload = { "user_id": user_id }
    token = jwt.encode(payload, "chosenone")
    return token

def decode_jwt(token: str) -> int:
    payload = jwt.decode(token, "chosenone")
    return payload["user_id"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserReadResponse(BaseModel):
    id: int
    email: str
    is_active: bool

class UserCreateRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
def post_users(user: UserCreateRequest, db: Session = Depends(get_db)):
    users_repository.create_user(db, UserCreate(email=user.email, password=user.password))
    return Response(status_code=200)

@app.post("/login")
def post_login(username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = users_repository.get_user_by_email(db, username)
    if not user or user.password != password:
        return HTTPException(status_code=404, detail="Wrong username or password!")
    token=encode_jwt(user.id)
    return {"access_token": token, "type": "bearer"}

@app.get("/profile", response_model=UserReadResponse)
def get_profile(token: str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repository.get_user(db, user_id)
    return user


class FlowerRequestResponse(BaseModel):
    name: str
    count: int
    cost: int

@app.post("/flowers")
def post_flowers(flower: FlowerRequestResponse, db: Session = Depends(get_db)):
    flowers_repository.create_flower(db, FlowerCreate(name=flower.name, count=flower.count, cost=flower.cost))
    return Response(status_code=200)

@app.get("/flowers", response_model=List[FlowerRequestResponse])
def get_flowers(db: Session = Depends(get_db)):
    flowers = flowers_repository.get_flowers(db)
    return flowers

@app.patch("/flowers/{flower_id}")
def patch_flower(flower_id: int, flower: FlowerRequestResponse, db: Session = Depends(get_db)):
    db_flower = flowers_repository.update_flower(db, flower_id, flower)
    if db_flower is None:
        raise HTTPException(status_code=404, detail="Flower not found")
    return Response(status_code=200)

@app.delete("/flowers/{flower_id}")
def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    db_flower = flowers_repository.delete_flower(db, flower_id)
    if db_flower is None:
        raise HTTPException(status_code=404, detail="Flower not found")
    return Response(status_code=200) 

@app.get("/cart/items")
def get_items(
    request: Request,
    cart_items: str = Cookie(default="[]"),
    db: Session = Depends(get_db)
):
    cart_items = json.loads(cart_items)
    flowers = [flowers_repository.get_flower(db, id) for id in cart_items]
    total = sum(flower.cost for flower in flowers)
    return {
        "flowers": [{"name": flower.name, "cost": flower.cost, "count": flower.count} for flower in flowers],
        "Total Price": total
    }