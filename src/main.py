from fastapi import FastAPI, Header, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.schemas import UserBase, User
from src.routers.cameras import router
from typing import Annotated
import secrets
from src.logger import Logger
from src.websockets import cameras
import logging
import sqlite3

logger = Logger()
app = FastAPI()
app.include_router(cameras.router)
app.include_router(router)

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

    if res == "admin":
        logging.info(f"Find information [DB]")
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            cur = conn.cursor()

            cur.execute("""SELECT Пользователь.id, Пользователь.Имя, Пользователь.Фамилия, Пользователь.Отчество, 
                        Пользователь.Дата_рождения, Пользователь.Пол,
                        Пользователь.Логин, Пользователь.Телефон, Пользователь.Почта, Пользователь.Пароль, Роль.Роль
                        FROM Пользователь JOIN Роль ON Пользователь.Роль = Роль.id
                        """)
            result = cur.fetchall()

            new_res = []
            for i in result:
                new_res.append({"id": i[0],
                                "name": i[1],
                                "lastname": i[2],
                                "patronymic": i[3],
                                "birthdate": i[4],
                                "sex": i[5],
                                "login": i[6],
                                "phone": i[7],
                                "email": i[8],
                                "password": i[9],
                                "role": i[10]})

            cur.close()
            conn.commit()
            return JSONResponse(content=new_res, status_code=200)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.post("/api/admin/users/edit")
async def edit_user(user: User, token: Annotated[str, Header()]):
    logging.info(f"[{user.login}] Edit user data")

    res = check_role_from_db(token)
    if res == "admin":
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            cur = conn.cursor()

            role = 2 if user.role == "admin" else 1

            try:
                logging.info(f"[{user.login}] Recording data: {user}")
                cur.execute("UPDATE Пользователь SET Логин = ?, Пароль = ?, Роль = ?, Почта = ?, Телефон = ?, "
                            "Имя = ?, Фамилия = ?, Отчество = ?, Дата_рождения = ?, Пол = ?"
                            "WHERE id == ?", (user.login, user.password, role, user.email, user.phone, user.name,
                                              user.lastname, user.patronymic, user.birthdate, user.sex, user.id))

                logging.info(f"[{user.login}] Successful edit user data")
                cur.close()
                conn.commit()
                return Response(status_code=200)
            except sqlite3.DatabaseError as e:
                logging.error(f"[{user.login}] Database exception: {e}")
                cur.close()
                conn.commit()
                return Response(status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.post("/api/admin/users/create", status_code=200)
async def add_account(user: User, token: Annotated[str, Header()]):
    logging.info(f"Create new user")

    res = check_role_from_db(token)
    if res == "admin":

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
                cur.close()
                conn.commit()
                return Response("The user has been successfully created", status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                cur.close()
                conn.commit()
                return Response("Database server error", status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.get("/api/admin/users/create/check_login")
async def check_login_exist(login: str, token: Annotated[str, Header()]):
    logging.info(f"Checking the existence of a login")

    res = check_role_from_db(token)
    if res == 'admin':
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            logging.info(f"Successful connection to the database")
            cur = conn.cursor()

            try:
                cur.execute("SELECT Логин FROM Пользователь")
                result = cur.fetchall()
                logging.info(f"Successfully get all logins")

                if any([login in i for i in result]):
                    cur.close()
                    conn.commit()
                    return Response("false", status_code=200)
                else:
                    cur.close()
                    conn.commit()
                    return Response("true", status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                cur.close()
                conn.commit()
                return Response(status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.get("/api/records/get_all")
async def get_all_records_metadata(token: Annotated[str, Header()]):
    logging.info(f"Get all records metadata")

    res = check_role_from_db(token)
    if res == 'admin':
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            logging.info(f"Successful connection to the database")
            cur = conn.cursor()

            try:
                cur.execute("""SELECT id, Завершение_записи, Камера FROM Записи 
                            WHERE Начало_записи >= date('now', '-1 month')""")
                result = cur.fetchall()
                logging.info(f"Successfully get all records")

                response = []
                for row in result:
                    response.append({'id': row[0], 'date': row[1], 'camera_id': row[2]})

                cur.close()
                conn.commit()
                return JSONResponse(content=response, status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                cur.close()
                conn.commit()
                return Response(status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.get("/api/records/get")
async def get_record_by_id(record_id: int, token: Annotated[str, Header()]):
    logging.info(f"Get record by id")

    res = check_role_from_db(token)

    if res == 'admin':
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            logging.info(f"Successful connection to the database")
            cur = conn.cursor()

            try:
                cur.execute("SELECT Путь_до_записи FROM Записи WHERE id == ?", (record_id,))
                result = cur.fetchall()
                logging.info(f"Successfully get record")

                cur.close()
                conn.commit()
                return FileResponse(path=result[0][0], status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                cur.close()
                conn.commit()
                return Response(status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@app.delete('/api/records/delete')
async def delete_record(record_id: int, token: Annotated[str, Header()]):
    logging.info(f"Delete record by id start")

    res = check_role_from_db(token)

    if res == 'admin':
        with sqlite3.connect('data/db/weapon_rec_database.db') as conn:
            logging.info(f"Successful connection to the database")
            cur = conn.cursor()

            try:
                cur.execute("DELETE FROM Записи WHERE id = ?", (record_id,))
                logging.info(f"Successfully delete record")

                cur.close()
                conn.commit()
                return Response(status_code=200)

            except sqlite3.DatabaseError as e:
                logging.error(f"Database exception: {e}")
                cur.close()
                conn.commit()
                return Response(status_code=502)
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
