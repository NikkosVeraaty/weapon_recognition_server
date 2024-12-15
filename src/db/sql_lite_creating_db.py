import sqlite3

# Создаем подключение к базе данных (создаст файл базы данных, если он еще не существует)
conn = sqlite3.connect('../../data/db/weapon_rec_database.db')
c = conn.cursor()

# Создание таблицы Пользователь
c.execute('''CREATE TABLE IF NOT EXISTS Пользователь (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Имя TEXT(100),
    Фамилия TEXT(100),
    Отчество TEXT(100) NULL,
    Дата_рождения DATETIME,
    Пол TEXT,
    Телефон TEXT(10) NULL,
    Почта TEXT(100) NULL,
    Логин TEXT(100) UNIQUE,
    Пароль TEXT(100),
    Токен TEXT UNIQUE,
    Роль INTEGER,
    FOREIGN KEY (Роль) REFERENCES Роль(id)
)''')

# Создание таблицы Роль
c.execute('''CREATE TABLE IF NOT EXISTS Роль (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Роль TEXT(5) ,
    CHECK (Роль IN ('admin', 'user'))
)''')

# Создание таблицы Кадры_с_детекцией
c.execute('''CREATE TABLE IF NOT EXISTS Кадры_с_детекцией (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Название_файла TEXT(100) UNIQUE,
    Картинка BLOB UNIQUE,
    Дата_загрузки DATETIME,
    Источник INTEGER,
    Активный_пользователь INTEGER,
    FOREIGN KEY (Источник) REFERENCES Камера(id),
    FOREIGN KEY (Активный_пользователь) REFERENCES Пользователь(id)
)''')

# Создание таблицы Авторизация
c.execute('''CREATE TABLE IF NOT EXISTS Авторизация (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Дата_входа INTEGER,
    Оператор INTEGER,
    Дата_выхода INTEGER NULL,
    FOREIGN KEY (Оператор) REFERENCES Пользователь(id)
)''')

# Создание таблицы Оружие
c.execute('''CREATE TABLE IF NOT EXISTS Оружие (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Название TEXT,
    Тип INTEGER,
    Модель TEXT,
    Производитель TEXT,
    Год_производства DATETIME,
    Калибр TEXT(100),
    Дата_загрузки DATETIME,
    Дата_последнего_обновления_записи DATETIME,
    FOREIGN KEY (Тип) REFERENCES Тип_оружия(id)
)''')

# Создание таблицы Оповещение
c.execute('''CREATE TABLE IF NOT EXISTS Оповещение (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Дата_обнаружения DATETIME,
    Местоположение TEXT,
    Тип_оружия INTEGER,
    Источник_данных INTEGER,
    Статус TEXT,
    FOREIGN KEY (Тип_оружия) REFERENCES Тип_оружия(id),
    FOREIGN KEY (Источник_данных) REFERENCES Камера(id)
)''')

# Создание таблицы Тип_оружия
c.execute('''CREATE TABLE IF NOT EXISTS Тип_оружия (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Тип TEXT(50) UNIQUE
)''')

# Создание таблицы Камера
c.execute('''CREATE TABLE IF NOT EXISTS Камера (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Местоположение TEXT NULL,
    Тип_камеры INTEGER NULL,
    Направление_обзора TEXT NULL,
    Угол_обзора INTEGER,
    Разрешение INTEGER,
    Статус TEXT,
    Дата_установки DATETIME NULL,
    CHECK ((Угол_обзора <= 360) AND (Угол_обзора > 0)),
    FOREIGN KEY (Тип_камеры) REFERENCES Тип_камеры(id)
)''')

# Создание таблицы Тип_камеры
c.execute('''CREATE TABLE IF NOT EXISTS Тип_камеры (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Тип TEXT(50) UNIQUE
)''')

# Создание таблицы Сеанс_работы_камер
c.execute('''CREATE TABLE IF NOT EXISTS Сеанс_работы_камер (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Камера INTEGER,
    Дата_начала_сеанса DATETIME,
    Дата_завершения_сеанса DATETIME NULL,
    CHECK (Дата_начала_сеанса < Дата_завершения_сеанса),
    FOREIGN KEY (Камера) REFERENCES Камера(id)
)''')

# Создание таблицы Логи_работы_нейросети
c.execute('''CREATE TABLE IF NOT EXISTS Логи_работы_нейросети (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Время_обработки INTEGER,
    Факт_распознавания INTEGER(1) DEFAULT 0,
    Классификация INTEGER,
    Вероятность_угрозы REAL,
    Картинка INTEGER,
    CHECK ((Факт_распознавания == 0) OR (Факт_распознавания == 1)),
    CHECK (Время_обработки > 0),
    CHECK ((Вероятность_угрозы >= 0) AND (Вероятность_угрозы <= 100)),
    FOREIGN KEY (Картинка) REFERENCES Кадры_с_детекцией(id)
)''')

# Создание таблицы Записи
c.execute('''CREATE TABLE IF NOT EXISTS Записи (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Камера INTEGER,
    Путь_до_записи TEXT UNIQUE,
    Начало_записи DATETIME,
    Завершение_записи DATETIME,
    Длительность INTEGER,
    Частота_кадров REAL,
    Размер_записи INTEGER,
    CHECK (Частота_кадров > 0),
    CHECK (Размер_записи > 0),
    CHECK (Длительность > 0),
    CHECK (Начало_записи < Завершение_записи),
    FOREIGN KEY (Камера) REFERENCES Камера(id)
)''')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
