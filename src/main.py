from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import secrets
import yaml
from src.logger import Logger
import logging


class User(BaseModel):
    username: str
    password: str
    role: str | None


logger = Logger()
app = FastAPI()


@app.get("/")
async def home():
    return "Hello"


@app.post("/api/auth/", status_code=200)
async def auth(user: User):
    logging.info(f"[{user.username}] Get user auth data")

    with open("data/users_auth_data.yaml") as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)
        logging.info(f"[{user.username}] Successful get users data")

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


@app.post("/api/reg/", status_code=200)
async def add_account(user: User):
    logging.info(f"Create new user/admin")
    with open("data/users_auth_data.yaml", 'r+') as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)

        if user.role not in read_data['roles']:
            return JSONResponse(content={"message": "Error in the selected role"}, status_code=400)
        elif any(user.username in el.keys() for el in read_data['users']):
            return JSONResponse(content={"message": "Login already exists"}, status_code=409)

        logging.info(f"Generate new token")
        token = secrets.token_urlsafe(32)
        logging.info(f"Successful generate new token")

        acc = {
            user.username: {
                'password': user.password,
                'token': token,
                'role': user.role
            }}

        logging.info(f"Save user data to file")
        read_data['users'].append(acc)
        file.seek(0)
        yaml.dump(read_data, file)
        file.truncate()
        logging.info(f"Successful save user data to file")

    return JSONResponse(content={"message": "The user has been successfully added"}, status_code=200)


@app.get("/api/admin/all_users")
async def get_all_users():  # Проверка на токен в будущем
    with open("data/users_auth_data.yaml") as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)
        return read_data['users']
