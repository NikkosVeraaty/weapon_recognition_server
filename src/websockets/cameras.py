from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import asyncio

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/1")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        while True:  # Для бесперерывной передачи (запускает заново)
            # while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/2")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        while True:  # Для бесперерывной передачи (запускает заново)
            # while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/3")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/4")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/5")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/6")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/7")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/8")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/9")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        cap = cv2.VideoCapture('video/video1.mp4')
        frame_counter = 0
        # while True: - для бесперерывной передачи (запускает заново)
        while cap.isOpened():

            await asyncio.sleep(0.02)
            ret, frame = cap.read()

            if frame_counter == cap.get(cv2.CAP_PROP_POS_FRAMES):
                frame_counter = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if not ret:
                break

            resize_frame = cv2.resize(frame, (390, 210), cv2.INTER_LINEAR)
            ret, buffer = cv2.imencode('.jpg', resize_frame)

            await websocket.send_bytes(buffer.tobytes())
            frame_counter += 1

    except WebSocketDisconnect:
        manager.disconnect(websocket)
