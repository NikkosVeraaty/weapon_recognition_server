from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import os
import asyncio

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, camera_id):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


manager = ConnectionManager()


@router.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await asyncio.sleep(camera_id/100)
    await websocket.accept()
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        print(os.getpid())
        frame_counter = 0
        while True:  # Для бесперерывной передачи (запускает заново)
            # while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                    frame_counter = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break

            frame_counter += 1

            if frame_counter % 3 != 0:
                await asyncio.sleep(0.03)
                continue

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())

    except WebSocketDisconnect:
        manager.disconnect(websocket)
