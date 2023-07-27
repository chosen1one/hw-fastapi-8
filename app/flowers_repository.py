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
    
    def update_flower(self, db: Session, flower_id: int, flower: FlowerCreate) -> Flower:
        db_flower = self.get_flower(db, flower_id)
        for key, value in flower.dict().items():
            if value:
                setattr(db_flower, key, value)
        db.commit()
        return db_flower
    
    def delete_flower(self, db: Session, flower_id: int):
        db_flower = self.get_flower(db, flower_id)
        if db_flower is None:
            return None
        db.delete(db_flower)
        db.commit()
        return True
    
    def create_flower(self, db: Session, flower: FlowerCreate) -> Flower:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        db.add(db_flower)
        db.commit()
        db.refresh(db_flower)
        return db_flower