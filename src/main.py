from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import secrets
import yaml
from src.logger import Logger
import logging


class User(BaseModel):
    username: str
    password: str
    role: str | None = None
    token: str | None = None


logger = Logger()
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")


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


@app.get("/api/admin/users/get")
async def get_all_users():  # Проверка на токен в будущем
    with open("data/users_auth_data.yaml") as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)
        return read_data['users']


@app.post("/api/admin/users/edit")
async def edit_user(user: User):
    logging.info(f"Edit user/admin data")

    logging.info(f"Reading user/admin data from file")
    with open("data/users_auth_data.yaml", "r+") as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)
        logging.info(f"Successful reading user/admin data from file")

        if user.role not in read_data['roles']:
            logging.error(f"Error in the selected role status_code #400")
            return JSONResponse(content={"message": "Error in the selected role"}, status_code=400)
        elif any(user.username in el.keys() and
                 user.token != list(el.values())[0]['token'] for el in read_data['users']):
            logging.error(f"Login already exists status_code #409")
            return JSONResponse(content={"message": "Login already exists"}, status_code=409)

        users = read_data["users"]
        updated_users = []
        logging.info(f"Redact user data")
        for i in users:
            if user.token == list(i.values())[0]['token']:
                new_user = {user.username: {
                    "password": user.password,
                    "role": user.role,
                    "token": user.token
                }}
                updated_users.append(new_user)
                continue
            else:
                updated_users.append(i)

        read_data['users'] = updated_users

        logging.info(f"Save updated user data to file")
        file.seek(0)
        yaml.dump(read_data, file)
        file.truncate()
        logging.info(f"Successful save user data to file")

        return JSONResponse(content={"message": "User's data has been successfully changed"}, status_code=200)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/video")
async def get_video():
    video_path = "video/video.mp4"
    return FileResponse(video_path)
