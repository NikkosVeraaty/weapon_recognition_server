import sqlite3
import json


def insert_roles(cur):
    with open("../../data/db/roles.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        roles = [(i['Роль'],) for i in data]

    cur.executemany('''
            INSERT INTO Роль (Роль)
            VALUES (?)
        ''', roles)


def insert_users(cur):
    with open("../../data/db/users.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        users = [(i['Дата_рождения'],
                  i['Имя'],
                  i['Логин'],
                  i['Отчество'],
                  i['Пароль'],
                  i['Пол'],
                  i['Почта'],
                  int(i['Роль']),
                  i['Телефон'],
                  i['Токен'],
                  i['Фамилия'],) for i in data]

    cur.executemany('''
            INSERT INTO Пользователь (Дата_рождения, Имя, Логин, Отчество, Пароль, Пол, Почта, Роль, Телефон, Токен, Фамилия)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', users)


def main():
    conn = sqlite3.connect('../../data/db/weapon_rec_database.db')
    cur = conn.cursor()

    insert_users(cur)

    cur.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
