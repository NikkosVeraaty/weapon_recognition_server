from fastapi import FastAPI, WebSocket, Header, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import UserBase, UserCreate, UserEdit
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
    logging.info(f"[{user.login}] Get user auth data")

    with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
        cur = conn.cursor()

        cur.execute("SELECT EXISTS(SELECT 1 FROM Пользователь WHERE Логин = ?)", (user.login,))

        if cur.fetchone()[0] == 1:
            logging.info(f"[{user.login}] User has an account")

            cur.execute("SELECT Пароль FROM Пользователь WHERE Логин = ?", (user.login,))
            if str(user.password) == str(cur.fetchone()[0]):
                logging.info(f"[{user.login}] Password was entered correctly")
                logging.info(f"[{user.login}] Returning the authorization token to the user")

                cur.execute("SELECT Токен FROM Пользователь WHERE Логин = ?", (user.login,))
                token = cur.fetchone()[0]

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


@app.get("/api/admin/users/get")
async def get_all_users(token: Annotated[str, Header()]):  # Проверка на токен в будущем
    logging.info(f"Get all users")

    res = check_role_from_db(token)

    if res:
        logging.info(f"Find information [DB]")
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            cur = conn.cursor()

            cur.execute("""SELECT Пользователь.id, Пользователь.Логин, Пользователь.Телефон, Пользователь.Почта, 
                        Пользователь.Пароль, Роль.Роль
                        FROM Пользователь JOIN Роль ON Пользователь.Роль = Роль.id
                        """)
            result = cur.fetchall()

            new_res = []
            for i in result:
                new_res.append({"id": i[0],
                                "login": i[1],
                                "phone": i[2],
                                "email": i[3],
                                "password": i[4],
                                "role": i[5]})

            return JSONResponse(content=new_res, status_code=200)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.post("/api/admin/users/edit")
async def edit_user(user: UserEdit, token: Annotated[str, Header()]):
    logging.info(f"[{user.login}] Edit user data")

    res = check_role_from_db(token)
    if res:
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            cur = conn.cursor()

            role = 2 if user.role == "admin" else 1

            try:
                logging.info(f"[{user.login}] Recording data: {user}")
                cur.execute("UPDATE Пользователь SET Логин = ?, Пароль = ?, Роль = ?, Почта = ?, Телефон = ? "
                            "WHERE id == ?",
                            (user.login, user.password, role, user.email, user.phone, user.id))

                logging.info(f"[{user.login}] Successful edit user data")
                return Response(status_code=200)
            except sqlite3.DatabaseError as e:
                logging.error(f"[{user.login}] Database exception: {e}")
                return Response(status_code=502)

    else:
        return Response("Don't have enough rights", status_code=403)


@app.post("/api/reg/", status_code=200)
async def add_account(user: UserCreate, token: Annotated[str, Header()]):
    logging.info(f"Create new user")

    res = check_role_from_db(token)
    if res:

        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            cur = conn.cursor()

            logging.info(f"Generate new token")
            token = secrets.token_urlsafe(45)
            logging.info(f"Successful generate new token")

            role = 2 if user.role == "admin" else 1

            try:
                logging.info(f"Adding new user to DB")
                cur.execute("""INSERT INTO Пользователь (Дата_рождения, Имя, Логин, Отчество, Пароль, Пол, Почта, Роль, 
                            Телефон, Токен, Фамилия) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (user.birthdate, user.name, user.login, user.patronymic, user.password,
                                  user.sex, user.email, role, user.phone, token, user.lastname))
                logging.info(f"Successful adding new user to DB")
                return Response("The user has been successfully created", status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                return Response("Database server error", status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


def check_role_from_db(token):
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
            return False
