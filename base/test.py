import sys
import argparse
from pathlib import Path
import time

import cv2
import torch
from ultralytics import YOLO
import serial
import serial.tools.list_ports


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YOLO webcam + send confidence over UART",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--device", type=str, default=None)

    parser.add_argument("--port", type=str, default=None, help="COM port (e.g. COM3). If not set → auto-detect")
    parser.add_argument("--baud", type=int, default=115200)

    return parser.parse_args()


def resolve_device(requested: str | None) -> str:
    if requested:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def find_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "CDC" in p.description:
            return p.device
    return None


def open_serial(port, baud):
    if port is None:
        port = find_port()

    if port is None:
        print("[ERROR] No COM port found", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Using port: {port}")
    ser = serial.Serial(port, baud, timeout=1)

    time.sleep(2)
    return ser


def get_confidence(results) -> float:
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return 0.0

    confs = boxes.conf.cpu().numpy()

    return float(confs.max())


def run_inference(args: argparse.Namespace) -> None:
    device = resolve_device(args.device)

    print(f"[INFO] Model   : {args.model}")
    print(f"[INFO] Device  : {device}")

    model = YOLO(str(args.model))
    model.to(device)

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

            msg = f"{confidence:.3f}\n"
            ser.write(msg.encode())

            print(f"Sent: {msg.strip()}")

            annotated = results[0].plot()

            label = f"conf: {confidence:.3f}"
            cv2.putText(
                annotated, label,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("YOLO → UART", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        ser.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_inference(parse_args())