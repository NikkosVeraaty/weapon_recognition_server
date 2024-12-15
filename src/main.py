from fastapi import FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import UserBase
from src.routers.cameras import router
from src.routers.admin import admin
from src.inspector import check_role_from_db
from src.db.session import conn
from typing import Annotated
from src.logger import Logger
from src.websockets import cameras
import logging

logger = Logger()
app = FastAPI()
app.include_router(cameras.router)
app.include_router(router)
app.include_router(admin)

# noinspection PyTypeChecker
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.get("/", tags=['Common'])
async def home():
    return "Hello"


@app.post("/api/auth/", responses={409: {"description": "Incorrect data"}}, tags=['Common'])
async def auth(user: UserBase):
    logging.info(f"[{user.login}] Get user auth data")

    cur = conn.cursor()

    cur.execute("SELECT EXISTS(SELECT 1 FROM Пользователь WHERE Логин = ?)", (user.login,))

    if cur.fetchone()[0] == 1:
        logging.info(f"[{user.login}] User has an account")

        cur.execute("SELECT Пароль FROM Пользователь WHERE Логин = ?", (user.login,))
        if str(user.password) == str(cur.fetchone()[0]):
            logging.info(f"[{user.login}] Password was entered correctly")
            logging.info(f"[{user.login}] Returning the authorization token to the user")

            cur.execute("SELECT Токен, id FROM Пользователь WHERE Логин = ?", (user.login,))
            token, user_id = cur.fetchone()

            cur.close()
            conn.commit()
            return token
        else:
            logging.info(f"[{user.login}] Password was entered incorrectly")
            cur.close()
            conn.commit()
            return Response("Password was entered incorrectly", status_code=409)
    else:
        logging.info(f"[{user.login}] User is not registered")
        cur.close()
        conn.commit()
        return Response("User is not registered", status_code=409)


@app.get("/api/check-role", tags=['Common'])
async def check_role(token: Annotated[str, Header()]):
    logging.info(f"[{token}] Check role by token")

    result = check_role_from_db(token=token)

    if result:
        return result
    else:
        return "The token does not exist in the system"
