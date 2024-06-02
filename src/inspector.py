import logging
import sqlite3


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
