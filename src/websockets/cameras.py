import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ultralytics import YOLO
import cv2
import asyncio


router = APIRouter()


class ConnectionManager:
    model = YOLO('data/neural_models/model_medium.pt')

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.number_connections = 0
        self.fps_sending = [3, 3, 4, 4, 3, 3, 3, 3, 3]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.number_connections += 1

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.number_connections -= 1

    def get_number_cameras(self):
        return self.number_connections


manager = ConnectionManager()


@router.websocket("/ws1/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await asyncio.sleep(camera_id/100)
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture(camera_id)

        frame_counter = 0
        while cap.isOpened():  # Для бесперерывной передачи (запускает заново)

            ret, frame = cap.read()

            if not ret:
                break

            frame_counter += 1

            if frame_counter % 3 != 0:
                # await asyncio.sleep(0.04)
                continue

            results = manager.model.predict(frame, conf=0.5, device='cpu')

            annotated_frame = results[0].plot(show=False)

            if len(results[0]) > 0:
                print(len(results))
                marks = []
                for el in results:
                    el_json = json.loads(str(el.tojson()))

                    marks.append({'name': el_json[0]['name'],
                                  'count': 1,
                                  'camera_id': camera_id + 1})
                await websocket.send_json(marks)

            ret, buffer = cv2.imencode('.jpg', annotated_frame)

            await websocket.send_bytes(buffer.tobytes())

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ret, buffer = cv2.imencode('.jpg', frame)


@router.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await asyncio.sleep(camera_id/100)
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')

        # print(os.getpid())
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_counter = 0
        while True:  # Для бесперерывной передачи (запускает заново)
            # while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                if frame_counter == total_frames:
                    frame_counter = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break

            frame_counter += 1

            if frame_counter % 3 != 0:
                await asyncio.sleep(0.04)
                continue

            # resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', frame)

            await websocket.send_bytes(buffer.tobytes())

    except WebSocketDisconnect:
        manager.disconnect(websocket)
