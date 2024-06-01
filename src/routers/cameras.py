from fastapi import APIRouter
import cv2
from cv2_enumerate_cameras import enumerate_cameras


router = APIRouter(prefix='/api/cameras')


@router.get('/number')
async def get_num_cameras():
    num_cameras = len(enumerate_cameras(cv2.CAP_MSMF))
    return num_cameras
