from fastapi import FastAPI, WebSocket, Header, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import UserBase, UserCreate
from typing import Annotated
import secrets
import yaml
from src.logger import Logger
from src.websockets import cameras
import logging
import sqlite3


logger = Logger()
app = FastAPI()
app.include_router(cameras.router)

# noinspection PyTypeChecker
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.get("/")
async def home():
    return "Hello"


@app.post("/api/auth/", responses={409: {"description": "Incorrect data"}})
async def auth(user: UserBase):
    logging.info(f"[{user.username}] Get user auth data")

    with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
        cur = conn.cursor()

        cur.execute("SELECT EXISTS(SELECT 1 FROM Пользователь WHERE Логин = ?)", (user.username,))

        if cur.fetchone()[0] == 1:
            logging.info(f"[{user.username}] User has an account")

            cur.execute("SELECT Пароль FROM Пользователь WHERE Логин = ?", (user.username,))
            if str(user.password) == str(cur.fetchone()[0]):
                logging.info(f"[{user.username}] Password was entered correctly")
                logging.info(f"[{user.username}] Returning the authorization token to the user")

                cur.execute("SELECT Токен FROM Пользователь WHERE Логин = ?", (user.username,))
                token = cur.fetchone()[0]

                cur.close()
                conn.commit()
                return token
            else:
                logging.info(f"[{user.username}] Password was entered incorrectly")
                cur.close()
                conn.commit()
                return Response("Password was entered incorrectly", status_code=409)
        else:
            logging.info(f"[{user.username}] User is not registered")
            cur.close()
            conn.commit()
            return Response("User is not registered", status_code=409)


@app.get("/api/check-role")
async def check_role(token: Annotated[str, Header()]):
    logging.info(f"[{token}] Check role by token")

    with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
        cur = conn.cursor()

        logging.info(f"Checking all users")

        cur.execute("SELECT Пользователь.Логин, Роль.Роль FROM Роль JOIN Пользователь ON Пользователь.Роль = Роль.id "
                    "WHERE Пользователь.Токен = ?", (token,))
        result = cur.fetchone()
        if result:
            logging.info(f"[{result[0]}] User has been found. Role - {result[1]}")  # [0] - login, [1] - role
            cur.close()
            conn.commit()
            return result[1]
        else:
            logging.info(f"The token does not exist in the system")
            cur.close()
            conn.commit()
            return "The token does not exist in the system"


@app.post("/api/reg/", status_code=200)
async def add_account(user: UserCreate):
    logging.info(f"Create new user/admin")
    with open("data/users_auth_data.yaml", 'r+') as file:
        read_data = yaml.load(file, Loader=yaml.FullLoader)

        if user.role not in read_data['roles']:
            return JSONResponse(content={"message": "Error in the selected role"}, status_code=400)
        elif any(user.username in el.keys() for el in read_data['users']):
            return JSONResponse(content={"message": "Login already exists"}, status_code=409)

        logging.info(f"Generate new token")
        token = secrets.token_urlsafe(45)
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
async def edit_user(user: UserBase):
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


@app.get("/video")
async def get_video():
    video_path = "video/video.mp4"
    return FileResponse(video_path)

# if __name__ == "__main__":
#     uvicorn.run("src.main:app", port=5000, log_level="info")
