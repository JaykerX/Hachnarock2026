import sys
import argparse
from pathlib import Path
import time
import cv2
import torch
from ultralytics import YOLO
import serial
import serial.tools.list_ports
import simpleaudio as sa


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--port", type=str, default=None)
    parser.add_argument("--baud", type=int, default=115200)
    return parser.parse_args()


def resolve_device(req):
    return req if req else ("cuda" if torch.cuda.is_available() else "cpu")


def find_port():
    for p in serial.tools.list_ports.comports():
        if "USB" in p.description or "CDC" in p.description:
            return p.device
    return None


def open_serial(port, baud):
    if port is None:
        port = find_port()
    if port is None:
        print("[ERROR] No COM port found")
        sys.exit(1)

    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(2)
    return ser


def play_sound():
    try:
        wave = sa.WaveObject.from_wave_file("dragon.wav")
        wave.play()
    except Exception as e:
        print(f"[AUDIO ERROR] {e}")


def get_confidence(results):
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return 0.0
    return float(boxes.conf.cpu().numpy().max())


def run(args):
    device = resolve_device(args.device)

    model = YOLO(str(args.model)).to(device)
    ser = open_serial(args.port, args.baud)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("[ERROR] Camera not available")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model.predict(
                source=frame,
                conf=args.conf,
                iou=args.iou,
                imgsz=args.img_size,
                device=device,
                verbose=False,
            )

            confidence = get_confidence(results)
            ser.write(f"{confidence:.3f}\n".encode())

            while ser.in_waiting > 0:
                line = ser.readline().decode(errors="ignore").strip()

                if "DANGER" in line:
                    print("[ALERT] DANGER received")
                    play_sound()

            frame_out = results[0].plot()
            cv2.putText(frame_out, f"conf: {confidence:.3f}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2)

            cv2.imshow("YOLO → UART", frame_out)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        ser.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run(parse_args())