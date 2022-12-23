from typing import Optional
from fastapi import FastAPI, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import *
from utils import *
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
#add lan to orgins
origins = [
    "http://localhost",
    "http://0.0.0.0:8080",
    "http://localhost:19006",
    "http://0.0.0.0:8000",
    

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///testDB.db", echo=True)

# session


def get_session():
    with Session(engine) as session:
        yield session

# get requests


@app.get("/users")
def get_users(session: Session = Depends(get_session)):
    statement = select(User)
    return session.exec(statement).all()

# get user by id


@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


# login


#get cars from user id
@app.get("/cars/{user_id}")
def get_cars(user_id: int, session: Session = Depends(get_session)):
    statement = select(Car).where(Car.user_id == user_id)
    cars = session.exec(statement).all()
    if cars:
        return cars
    else:
        return {"message": "No cars found"}


#get all logs
@app.get("/logs/{user_id}/{car_registration}")
def get_logs(user_id: int, car_registration: str, session: Session = Depends(get_session)):
    statement = select(Logs).where(Logs.user_id == user_id).where(Logs.carRegistration == car_registration)
    logs = session.exec(statement).all()
    if logs:
        return logs
    else:
        return {"message": "No logs found"}


# post requests
# login
@app.post("/login")
def login(user: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    result = session.exec(statement).first()
    if result:
        if verify_password(user.password, result.password):
            return result
        else:
            return {"message": "Invalid username or password"}
    else:
        return {"message": "Invalid username or password"}

# add user


@app.post("/adduser")
def add_user(user: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    result = session.exec(statement).first()
    if result:
        return {"message": "User already exists"}
    else:
        # hash password
        user.password = get_hashed_password(user.password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user



# add car
@app.post("/addcar")
def add_car(car: Car, session: Session = Depends(get_session)):
    statement = select(Car).where(Car.registration == car.registration)
    result = session.exec(statement).first()
    if result:
        return {"message": "Car already exists"}
    else:
        session.add(car)
        session.commit()
        session.refresh(car)
        return car

# add log
@app.post("/addlog")
def add_log(log: Logs, session: Session = Depends(get_session)):
    statement = select(Logs).where(Logs.odometer == log.odometer)
    result = session.exec(statement).first()
    if result:
        return {"message": "Log already exists"}
    else:
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

# delete user


@app.delete("/deleteuser/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message": "User deleted"}
    else:
        return {"message": "User not found"}

# delete car


@app.delete("/deletecar/{carRegistration}")
def delete_car(carRegistration: str, session: Session = Depends(get_session)):
    statement = select(Car).where(Car.registration == carRegistration)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message": "Car deleted"}
    else:
        return {"message": "Car not found"}

# delete log
@app.delete("/deletelog/{odometer}")
def delete_log(odometer: int, session: Session = Depends(get_session)):
    statement = select(Logs).where(Logs.odometer == odometer)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message": "Log deleted"}
    else:
        return {"message": "Log not found"}


if __name__ == '__main__':
    app.run()
