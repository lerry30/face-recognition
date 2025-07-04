import os
os.environ["OPENCV_LOG_LEVEL"] = "ERROR" # suppress warnings

import cv2

def list_available_cameras(rng):
    available_cameras = []

    for i in range(rng):
        if os.name == 'posix' and not os.path.exists(f"/dev/video{i}"):
            continue
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()

    return available_cameras
