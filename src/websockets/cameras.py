import json
import yaml
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ultralytics import YOLO
import numpy as np
import cv2
import asyncio


router = APIRouter()


class ConnectionManager:
    model = YOLO('data/neural_models/model_medium.pt')
    detections = []

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

        with open('data/config_nn.yaml') as file:
            data = yaml.safe_load(file)
            params = data['parameters']
            classes = np.array([4, 5, 0, 2, 1, 3])[list(data['parameters']['classes'].values())]

        frame_counter = 0
        while cap.isOpened():  # Для бесперерывной передачи (запускает заново)

            ret, frame = cap.read()

            if not ret:
                break

            frame_counter += 1

            if frame_counter % 3 != 0:
                # await asyncio.sleep(0.04)
                continue

            results = manager.model.track(source=frame,
                                          conf=params['conf'],
                                          iou=params['iou'],
                                          max_det=params['max_detection'],
                                          save_crop=params['save_crop'],
                                          classes=classes,
                                          device=params['device'])

            annotated_frame = results[0].plot(show=False,
                                              line_width=params['line_width'],
                                              filename='data/annotated_imgs')

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
