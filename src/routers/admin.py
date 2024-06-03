from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse, Response
from src.schemas import User
from src.routers.records import records
from src.inspector import check_role_from_db
from src.db.session import conn
from typing import Annotated
import logging
import secrets
import sqlite3


admin = APIRouter(prefix='/api/admin', tags=['Admin'])
admin.include_router(records)


@admin.get("/users/get")
async def get_all_users(token: Annotated[str, Header()]):
    logging.info(f"Get all users")

    res = check_role_from_db(token)

    if res == "admin":
        logging.info(f"Find information [DB]")

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


@admin.post("/users/edit")
async def edit_user(user: User, token: Annotated[str, Header()]):
    logging.info(f"[{user.login}] Edit user data")

    res = check_role_from_db(token)
    if res == "admin":

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


@admin.post("/users/create", status_code=200)
async def add_account(user: User, token: Annotated[str, Header()]):
    logging.info(f"Create new user")

    res = check_role_from_db(token)
    if res == "admin":

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


@admin.get("/users/create/check_login")
async def check_login_exist(login: str, token: Annotated[str, Header()]):
    logging.info(f"Checking the existence of a login")

    res = check_role_from_db(token)
    if res == 'admin':
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
