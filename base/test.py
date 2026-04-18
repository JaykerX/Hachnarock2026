import cv2
import serial
import time
import numpy as np

# ===== CONFIG =====
PORT = "COM5"          # change to /dev/ttyUSB0 on Linux
BAUD = 921600          # must match board UART speed
WIDTH = 96
HEIGHT = 96

# ===== SERIAL =====
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # allow board reset

# ===== CAMERA =====
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

print("Streaming to device... Press Q to stop")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # ===== Resize to 96x96 =====
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    # OpenCV uses BGR → convert to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Flatten to raw bytes
    img_bytes = frame.astype(np.uint8).tobytes()

    # ===== Send frame =====
    packet = b"\xAA\x55" + img_bytes
    ser.write(packet)

    # Optional: limit FPS (~10–20 FPS safe for most MCUs)
    time.sleep(0.03)

    # Optional preview
    cv2.imshow("preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===== CLEANUP =====
cap.release()
ser.close()
cv2.destroyAllWindows()