from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from src.logger import Logger
import logging


class User(BaseModel):
    username: str
    password: str


logger = Logger()
app = FastAPI()


@app.get("/")
async def home():
    return "Hello"


@app.post("/auth/")
async def auth(user: User):
    logging.info(f"[{user.username}] Get user auth data")
    with open("data/users_auth_data.yaml") as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)
        logging.info(f"[{user.username}] Successful get user data")

        if user.username in read_data['users']:
            logging.info(f"[{user.username}] User has an account")

            auth_user = read_data['users'][user.username]
            if user.password == str(auth_user['password']):
                logging.info(f"[{user.username}] Password was entered correctly")
                logging.info(f"[{user.username}] Returning the authorization token to the user")
                return auth_user['token']
            else:
                logging.info(f"[{user.username}] Password was entered incorrectly")
        else:
            logging.info(f"[{user.username}] User is not registered")
    return user
