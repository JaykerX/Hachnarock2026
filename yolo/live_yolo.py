import sys
import argparse
from pathlib import Path
import random
import math

import cv2
import numpy as np
import torch
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLO inference on a live webcam feed.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--device", type=str, default=None)
    return parser.parse_args()


def resolve_device(requested: str | None) -> str:
    if requested is not None:
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


# ---------------------------------------------------------------------------
# Explosion particle system
# ---------------------------------------------------------------------------

class Particle:
    def __init__(self, x: float, y: float, radius: int):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, radius * 0.18)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.5, 1.0)
        self.decay = random.uniform(0.03, 0.07)
        self.size = random.randint(2, max(3, radius // 8))
        self.color_hot = (
            random.randint(200, 255),  # B
            random.randint(80, 180),   # G
            random.randint(0, 60),     # R
        )

    @property
    def alive(self) -> bool:
        return self.life > 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.vx *= 0.97
        self.life -= self.decay

    def draw(self, frame: np.ndarray):
        alpha = max(0.0, self.life)
        color = (
            min(255, int(self.color_hot[0] * alpha)),
            min(255, int(self.color_hot[1] * alpha)),
            min(255, int(self.color_hot[2] + (255 - self.color_hot[2]) * (1 - alpha))),
        )
        cv2.circle(frame, (int(self.x), int(self.y)), max(1, int(self.size * alpha)), color, -1)


class Explosion:
    N_PARTICLES = 120

    def __init__(self, cx: int, cy: int, radius: int):
        self.particles = [Particle(cx, cy, radius) for _ in range(self.N_PARTICLES)]
        self.center = (cx, cy)
        self.ring_r = 0.0
        self.ring_max = radius * 1.4
        self.ring_grow = radius * 0.07
        self.flash = 3

    @property
    def alive(self) -> bool:
        return any(p.alive for p in self.particles)

    def update_and_draw(self, frame: np.ndarray):
        # flash
        if self.flash > 0:
            overlay = frame.copy()
            intensity = int(180 * self.flash / 3)
            overlay[:] = (intensity, intensity, intensity)
            cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
            self.flash -= 1

        # shockwave ring
        if self.ring_r < self.ring_max:
            self.ring_r += self.ring_grow
            alpha_ring = max(0.0, 1.0 - self.ring_r / self.ring_max)
            cv2.circle(
                frame, self.center, int(self.ring_r),
                (int(100 * alpha_ring), int(200 * alpha_ring), int(255 * alpha_ring)),
                max(1, int(4 * alpha_ring)),
            )

        # particles
        for p in self.particles:
            if p.alive:
                p.update()
                p.draw(frame)


class ExplosionManager:
    def __init__(self):
        self._explosions: list[Explosion] = []

    def trigger(self, box: tuple[int, int, int, int]):
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        radius = max((x2 - x1), (y2 - y1)) // 2
        self._explosions.append(Explosion(cx, cy, radius))

    def update_and_draw(self, frame: np.ndarray):
        self._explosions = [e for e in self._explosions if e.alive]
        for e in self._explosions:
            e.update_and_draw(frame)


def get_boxes(results) -> list[tuple[int, int, int, int]]:
    """Return all bounding boxes (x1,y1,x2,y2) from the first result."""
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return []
    return [tuple(b.astype(int)) for b in boxes.xyxy.cpu().numpy()]


# ---------------------------------------------------------------------------

def run_inference(args: argparse.Namespace) -> None:
    model_path = args.model
    if not Path(model_path).exists() and not str(model_path).endswith(".pt"):
        print(f"[ERROR] Model file not found: {model_path}", file=sys.stderr)
        return

    device = resolve_device(args.device)
    print(f"[INFO] Loading model : {model_path}")
    print(f"[INFO] Device        : {device}")
    print(f"[INFO] Confidence    : {args.conf}")
    print(f"[INFO] IoU threshold : {args.iou}")
    print(f"[INFO] Image size    : {args.img_size}")
    print(f"[INFO] Camera index  : {args.camera}")
    print("[INFO] Press 'q' to quit  |  Press 'e' to trigger explosion on all detections.")

    model = YOLO(str(model_path))
    model.to(device)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera index {args.camera}.", file=sys.stderr)
        return

    explosions = ExplosionManager()
    last_boxes: list[tuple[int, int, int, int]] = []

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

            last_boxes = get_boxes(results)

            annotated = results[0].plot()

            # draw explosions on top of YOLO annotations
            explosions.update_and_draw(annotated)

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

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("e"):
                # manual trigger — explode every detected object
                for box in last_boxes:
                    explosions.trigger(box)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Stream closed.")


if __name__ == "__main__":
    run_inference(parse_args())