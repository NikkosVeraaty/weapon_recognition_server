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


def insert_authorization(cur):
    with open("../../data/db/authorization.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        auth = [(i['Дата_входа'],
                 i['Оператор'],
                 i['Дата_выхода'],) for i in data]

    cur.executemany('''
            INSERT INTO Авторизация (Дата_входа, Оператор, Дата_выхода)
            VALUES (?, ?, ?)
        ''', auth)


def insert_weapon_type(cur):
    with open("../../data/db/weapon_type.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        weapon_type = [(i['Тип'],) for i in data]

    cur.executemany('''
            INSERT INTO Тип_оружия (Тип)
            VALUES (?)
        ''', weapon_type)


def insert_weapons(cur):
    with open("../../data/db/weapons.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        weapons = [(i['Название'],
                    i['Тип'],
                    i['Модель'],
                    i['Производитель'],
                    i['Год_производства'],
                    i['Калибр'],
                    i['Дата_загрузки'],
                    i['Дата_последнего_обновления_записи']) for i in data]

    cur.executemany('''
            INSERT INTO Оружие (Название, Тип, Модель, Производитель, Год_производства, Калибр, 
            Дата_загрузки, Дата_последнего_обновления_записи)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', weapons)


def insert_cameras_types(cur):
    with open("../../data/db/camera_types.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        camera_type = [(i['Тип'],) for i in data]

    cur.executemany('''
            INSERT INTO Тип_камеры (Тип)
            VALUES (?)
        ''', camera_type)


def insert_cameras(cur):
    with open("../../data/db/cameras.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        cameras = [(i['Местоположение'],
                        i['Тип_камеры'],
                        i['Направление_обзора'],
                        i['Угол_обзора'],
                        i['Разрешение'],
                        i['Статус'],
                        i['Дата_установки'],) for i in data]

    cur.executemany('''
            INSERT INTO Камера (Местоположение, Тип_камеры, 
            Направление_обзора, Угол_обзора, Разрешение, Статус, Дата_установки)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', cameras)


def insert_records(cur):
    with open("../../data/db/records.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        records = [(i['Камера'],
                    i['Путь_до_записи'],
                    i['Начало_записи'],
                    i['Завершение_записи'],
                    i['Длительность'],
                    i['Частота_кадров'],
                    i['Размер_записи'],) for i in data]

    cur.executemany('''
            INSERT INTO Записи (Камера, Путь_до_записи, Начало_записи, Завершение_записи, 
            Длительность, Частота_кадров, Размер_записи)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', records)


def insert_cameras_session(cur):
    with open("../../data/db/cameras_seans.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        sessions = [(i['Камера'],
                     i['Дата_начала_сеанса'],
                     i['Дата_завершения_сеанса']) for i in data]

    cur.executemany('''
            INSERT INTO Сеанс_работы_камер (Камера, Дата_начала_сеанса, Дата_завершения_сеанса)
            VALUES (?, ?, ?)
            ''', sessions)


def insert_notification(cur):
    with open("../../data/db/notifications.json", encoding='utf-8') as f:
        data = json.loads(f.read())
        notification = [(i['Дата_обнаружения'],
                         i['Местоположение'],
                         i['Тип_оружия'],
                         i['Источник_данных'],
                         i['Статус']) for i in data]

    cur.executemany('''
            INSERT INTO Оповещение (Дата_обнаружения, Местоположение, 
            Тип_оружия, Источник_данных, Статус)
            VALUES (?, ?, ?, ?, ?)
            ''', notification)


def main():
    conn = sqlite3.connect('../../data/db/weapon_rec_database.db')
    cur = conn.cursor()

    insert_notification(cur)

    cur.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
