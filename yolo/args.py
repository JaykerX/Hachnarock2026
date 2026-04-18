import argparse
from pathlib import Path


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