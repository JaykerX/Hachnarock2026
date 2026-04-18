import torch
import argparse
from pathlib import Path
from ultralytics import YOLO  # type: ignore


class ArgumentHandler:
    __slots__ = ("_parser", "_parsed_args")
    
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._define_arguments()
        self._parsed_args = vars(self._parser.parse_args())
        
        
    def _define_arguments(self) -> None:
        self._parser.add_argument("--data", type=Path, required=True, help="Path to dataset YAML file")
        self._parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model name or path")
        self._parser.add_argument("--epochs", type=int, default=150, help="Number of training epochs")
        self._parser.add_argument("--imgsz", type=int, default=640, help="Image size for training")
        self._parser.add_argument("--batch", type=int, default=4, help="Batch size for training")
        self._parser.add_argument("--patience", type=int, default=15, help="Early stopping patience")
        self._parser.add_argument("--run_name", type=str, default="YOLO_run", help="Name for the training run")
        
    @property
    def yaml_path(self) -> Path:
        return self._parsed_args["data"]
    
    @property
    def model_name(self) -> str:
        return self._parsed_args["model"]
    
    @property
    def epochs(self) -> int:    
        return self._parsed_args["epochs"]
    
    @property
    def img_size(self) -> int:
        return self._parsed_args["imgsz"]
    
    @property
    def batch_size(self) -> int:
        return self._parsed_args["batch"]
    
    @property
    def patience(self) -> int:  
        return self._parsed_args["patience"]
    
    @property
    def run_name(self) -> str:
        return self._parsed_args["run_name"]
        

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
        workers=2
    )

    best_path = project_dir / args.run_name / "weights" / "best.pt"
    print("\nYOLO training finished.")
    print(f"Best model saved in: {best_path}")


if __name__ == "__main__":
    main()