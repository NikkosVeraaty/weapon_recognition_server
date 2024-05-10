import logging
import datetime
from threading import Lock


class Singleton(type):
    __instance = None
    __lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__call__(*args, **kwargs)

        return cls.__instance


class Logger(metaclass=Singleton):
    """
    Простой класс для логирования сообщений в файл и на консоль.
    """

    def __init__(self):
        # Настройка логирования
        file_handler = logging.FileHandler(f'logs/{self.__log_name_generate()}')
        console_handler = logging.StreamHandler()
        logging.basicConfig(handlers=(file_handler, console_handler),
                            level=logging.INFO,
                            encoding='UTF-8',
                            format="%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")

    @staticmethod
    def __log_name_generate():
        """
        Генерация имени лог-файла на основе текущей даты.

        Returns:
            str: Имя лог-файла в формате 'log_год-месяц-день.log'.
        """

        now = datetime.datetime.now()
        name = f"log_{now.year}-{'%02d' % now.month}-{'%02d' % now.day}.log"
        return name
