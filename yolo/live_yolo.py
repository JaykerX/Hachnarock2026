import sys
import argparse
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLO inference on a live webcam feed.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument("--model", type=Path, required=True, help="Path to a YOLO weights file (.pt) or a model name (e.g. yolov8n.pt).")
    parser.add_argument("--conf", type=float, default=0.25, help="Minimum confidence threshold for detections (0.0-1.0).")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold used in NMS.")
    parser.add_argument("--img-size", type=int, default=640, help="Inference image size (pixels, square).")
    parser.add_argument("--camera", type=int, default=0, help="OpenCV camera index (0 = built-in laptop webcam).")
    parser.add_argument("--device", type=str, default=None, help="Inference device: 'cpu', 'cuda', 'mps', or a CUDA device index. Defaults to CUDA if available, otherwise CPU.")
    return parser.parse_args()


def resolve_device(requested: str | None) -> str:
    if requested is not None:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def run_inference(args: argparse.Namespace) -> None:
    model_path = args.model
    if not Path(model_path).exists():
        if not str(model_path).endswith(".pt"):
            print(f"[ERROR] Model file not found: {model_path}", file=sys.stderr)
            return

    device = resolve_device(args.device)
    print(f"[INFO] Loading model : {model_path}")
    print(f"[INFO] Device        : {device}")
    print(f"[INFO] Confidence    : {args.conf}")
    print(f"[INFO] IoU threshold : {args.iou}")
    print(f"[INFO] Image size    : {args.img_size}")
    print(f"[INFO] Camera index  : {args.camera}")
    print("[INFO] Press 'q' to quit.")

    model = YOLO(str(model_path))
    model.to(device)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera index {args.camera}.", file=sys.stderr)
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Failed to grab frame - retrying …")
                continue

            results = model.predict(
                source=frame,
                conf=args.conf,
                iou=args.iou,
                imgsz=args.img_size,
                device=device,
                verbose=False,
            )

            annotated = results[0].plot()
            label = f"Model: {Path(model_path).stem}  |  conf >= {args.conf}"
            
            cv2.putText(
                annotated, label,
                org=(10, 28),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.65,
                color=(0, 255, 0),
                thickness=2,
                lineType=cv2.LINE_AA,
            )

            cv2.imshow("YOLO - live inference  (press q to quit)", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Stream closed.")
        

if __name__ == "__main__":
    run_inference(parse_args())