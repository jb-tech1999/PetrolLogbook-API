from fastapi import FastAPI, Depends, HTTPException
import auth
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models import *
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost",
    "http://0.0.0.0:8080",
    "http://localhost:19006",
    "http://0.0.0.0:8000",
    "http://0.0.0.0:19000",
    "http://192.168.0.114:19000",
    "http://188.168.1.6:60988"
    

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_handler = auth.AuthHandler()
engine = create_engine("sqlite:///testDB.db", echo=True)

# session


def get_session():
    with Session(engine) as session:
        yield session

users = []



@app.post("/register", status_code=201)
def register(authdetails: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == authdetails.username)
    user = session.exec(statement).first()

    if authdetails.username == user.username:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth_handler.get_password_hash(user.password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

    
@app.post("/login")
def login(authdetails: User, session: Session = Depends(get_session)):
    user = None
    statement = select(User).where(User.username == authdetails.username)
    user = session.exec(statement).first()
    print(user)

    if (user is None) or (not auth_handler.verify_password(authdetails.password, user.password)):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = auth_handler.encode_token(user.id)

    return {"token": token}


#get all users if token is provided
@app.get("/users")
def get_users(session: Session = Depends(get_session), id=Depends(auth_handler.auth_wrapper)):
    statement = select(User).where(User.id == id)
    return session.exec(statement).all()



@app.get("/cars")
def get_cars(user_id=Depends(auth_handler.auth_wrapper), session: Session = Depends(get_session)):
    statement = select(Car).where(Car.user_id == user_id)
    cars = session.exec(statement).all()
    if cars:
        return cars
    else:
        return {"message": "No cars found"}

#get all logs
@app.get("/logs/{car_registration}")
def get_logs(car_registration: str, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_wrapper)):
    statement = select(Logs).where(Logs.user_id == user_id).where(Logs.carRegistration == car_registration)
    logs = session.exec(statement).all()
    if logs:
        return logs
    else:
        return {"message": "No logs found"}

@app.post("/addcar")
def add_car(car: Car, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_wrapper)):
    statement = select(Car).where(Car.user_id == user_id).where(Car.registration == car.registration)
    result = session.exec(statement).first()
    if result:
        raise HTTPException(status_code=400, detail="Car already registered")
    else:
        car.user_id = user_id
        session.add(car)
        session.commit()
        session.refresh(car)
        return car

@app.post("/addlog")
def add_log(log: Logs, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_wrapper)):
    statement = select(Logs).where(Logs.odometer == log.odometer).where(Logs.carRegistration == log.carRegistration)
    result = session.exec(statement).first()
    if result:
        raise HTTPException(status_code=400, detail="Log already registered")
    else:
        log.user_id = user_id
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

@app.delete("/deletecar/{car_registration}")
def delete_car(car_registration: str, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_wrapper)):
    statement = select(Car).where(Car.user_id == user_id).where(Car.registration == car_registration)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message": "Car deleted"}
    else:
        raise HTTPException(status_code=400, detail="Car not found")

@app.delete("/deletelog/{car_registration}/{odometer}")
def delete_log(car_registration: str, odometer: int, session: Session = Depends(get_session), user_id=Depends(auth_handler.auth_wrapper)):
    statement = select(Logs).where(Logs.user_id == user_id).where(Logs.carRegistration == car_registration).where(Logs.odometer == odometer)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message": "Log deleted"}
    else:
        raise HTTPException(status_code=400, detail="Log not found")


@app.get("/")
def read_root():
    return {"Hello": "World"}