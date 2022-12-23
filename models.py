from typing import Optional
from sqlmodel import Field, SQLModel, Session, create_engine, select
from datetime import datetime

class Car(SQLModel, table=True ):
    registration: str =  Field(default=None, primary_key=True)
    make: str
    model: str
    year: int
    user_id: int = Field(default=None, foreign_key="user.id")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str


class Logs(SQLModel, table=True):
    logid: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    carRegistration: Optional[str]
    date: str = Field(default=datetime.now())
    odometer: int
    distance : float
    litersPurchase: float
    garage : str
    totalcost: float





