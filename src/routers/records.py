from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse, Response
from src.inspector import check_role_from_db
from src.db.session import conn
from typing import Annotated
import logging
import cv2
import sqlite3


records = APIRouter(prefix='/records')


@records.get("/get_all")
async def get_all_records_metadata(token: Annotated[str, Header()]):
    logging.info(f"Get all records metadata")

    res = check_role_from_db(token)
    if res == 'admin':
        logging.info(f"Successful connection to the database")
        cur = conn.cursor()

        try:
            cur.execute("""SELECT id, Завершение_записи, Камера, Путь_до_записи FROM Записи 
                        WHERE Начало_записи >= date('now', '-1 month')""")
            result = cur.fetchall()
            logging.info(f"Successfully get all records")

            response = []
            for row in result:
                cap = cv2.VideoCapture(row[3])
                ret, frame = cap.read()
                if ret:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    response.append({
                        'id': row[0],
                        'date': row[1],
                        'preview': str(buffer.tobytes()),
                        'camera_id': row[2]})
                else:
                    response.append({
                        'id': row[0],
                        'date': row[1],
                        'preview': None,
                        'camera_id': row[2]})

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


@records.get("/get")
async def get_record_by_id(record_id: int, token: Annotated[str, Header()]):
    logging.info(f"Get record by id")

    res = check_role_from_db(token)

    if res == 'admin':
        logging.info(f"Successful connection to the database")
        cur = conn.cursor()

        try:
            cur.execute("SELECT Путь_до_записи FROM Записи WHERE id = ?", (record_id,))
            result = cur.fetchall()
            logging.info(f"Successfully get record")

            with open(result[0][0], "rb") as video_file:
                video_bytes = video_file.read()

            cur.close()
            conn.commit()
            # return FileResponse(path=result[0][0], status_code=200)
            return Response(content=str(video_bytes))

        except sqlite3.DatabaseError as e:
            logging.error(f"Database exception: {e}")
            cur.close()
            conn.commit()
            return Response(status_code=502)
    else:
        return Response("Don't have enough rights", status_code=403)


@records.delete('/delete')
async def delete_record(record_id: int, token: Annotated[str, Header()]):
    logging.info(f"Delete record by id start")

    res = check_role_from_db(token)

    if res == 'admin':
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
