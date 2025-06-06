import cv2
import numpy as np
from onvif import ONVIFCamera
import time

# pip install opencv-python onvif-zeep numpy

# === CAMERA CONFIGURATION ===
CAMERA_IP = '192.168.1.64'
PORT = 80
USERNAME = 'admin'
PASSWORD = 'your_password'
RTSP_URL = f'rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}/Streaming/Channels/101'

# === CONNECT TO PTZ CAMERA VIA ONVIF ===
print("[INFO] Connecting to ONVIF PTZ camera...")
camera = ONVIFCamera(CAMERA_IP, PORT, USERNAME, PASSWORD)
media = camera.create_media_service()
ptz = camera.create_ptz_service()
profile = media.GetProfiles()[0]
token = profile.token

# Prepare AbsoluteMove request
request = ptz.create_type('AbsoluteMove')
request.ProfileToken = token

# === FIXED ZOOM LEVEL ===
FIXED_ZOOM = 0.4

# === PRESET POSITION (PanTilt + Zoom when idle) ===
PRESET_PAN = 0.5  # Center
PRESET_TILT = 0.5  # Center
PRESET_ZOOM = 0.2  # Wider view

# Ball loss timeout in seconds
BALL_LOST_TIMEOUT = 5
last_ball_seen_time = time.time()
preset_moved = False

# === VIDEO STREAM ===
cap = cv2.VideoCapture(RTSP_URL)
print("[INFO] Tracking white ball with fixed zoom. Will return to preset if not seen.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to read frame")
        break

    height, width = frame.shape[:2]

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # White color mask
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ball_detected = False

    if contours:
        largest = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest)

        if radius > 10:
            ball_detected = True
            last_ball_seen_time = time.time()
            preset_moved = False

            # Draw ball
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)

            # Normalize to PTZ range
            pan = round(x / width, 4)
            tilt = round(y / height, 4)
            pan = min(max(pan, 0.01), 0.99)
            tilt = min(max(tilt, 0.01), 0.99)

            # Move to ball with fixed zoom
            request.Position = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': FIXED_ZOOM}
            }
            ptz.AbsoluteMove(request)

    # If ball not seen for BALL_LOST_TIMEOUT seconds, return to preset
    elif time.time() - last_ball_seen_time > BALL_LOST_TIMEOUT and not preset_moved:
        print("[INFO] Ball not detected, moving to preset position.")
        request.Position = {
            'PanTilt': {'x': PRESET_PAN, 'y': PRESET_TILT},
            'Zoom': {'x': PRESET_ZOOM}
        }
        ptz.AbsoluteMove(request)
        preset_moved = True

    cv2.imshow("Ball Tracker", frame)
    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
