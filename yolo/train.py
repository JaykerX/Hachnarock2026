import torch
from pathlib import Path
from ultralytics import YOLO  # type: ignore

from args import ArgumentHandler
        

def main() -> None:
    args = ArgumentHandler()
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    
    project_dir: Path = PROJECT_ROOT / "runs"
    project_dir.mkdir(parents=True, exist_ok=True)

    device: str = "cuda" if torch.cuda.is_available() else "cpu"

    print("Training Configuration for YOLO")
    print(f"Dataset YAML: {args.yaml_path}")
    print(f"Base model:   {args.model_name}")
    print(f"Epochs:       {args.epochs}")
    print(f"Image size:   {args.img_size}")
    print(f"Batch size:   {args.batch_size}")
    print(f"Patience:     {args.patience}")
    print(f"Output dir:   {project_dir / args.run_name}")
    print(f"Device:       {device}")
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    if not args.yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {args.yaml_path}")

    model = YOLO(str(args.model_name))

    model.train(
        data=str(args.yaml_path),
        epochs=args.epochs,
        imgsz=args.img_size,
        batch=args.batch_size,
        patience=args.patience,
        project=str(project_dir),
        name=args.run_name,
        device=device,
    )

    best_path = project_dir / args.run_name / "weights" / "best.pt"
    print("\nYOLO training finished.")
    print(f"Best model saved in: {best_path}")


if __name__ == "__main__":
    main()