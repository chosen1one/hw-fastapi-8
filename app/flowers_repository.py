from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from attrs import define

from .database import Base

class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)
    cost = Column(Integer)


@define
class FlowerCreate:
    name: str
    count: int
    cost: int

class FlowersRepository:
    def get_flower(self, db: Session, flower_id: int) -> Flower:
        return db.query(Flower).filter(Flower.id == flower_id).first()

    def get_flowers(self, db: Session, skip: int = 0, limit: int = 100) -> list[Flower]:
        return db.query(Flower).offset(skip).limit(limit).all()
    
    def create_flower(self, db: Session, flower: FlowerCreate) -> Flower:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        db.add(db_flower)
        db.commit()
        db.refresh(db_flower)
        return db_flower