import yaml
import shutil
import random
from pathlib import Path

TRAIN_RATIO: float = 0.8


def generate_dataset_yaml(classes: list, output_file: Path):
    data_config: dict = {
        'path': str(output_file.parent.absolute()),
        'train': "train/images",
        'val': "val/images",
        'nc': len(classes),
        'names': classes
    }

    try:
        with open(output_file, 'w') as file:
            yaml.dump(data_config, file, default_flow_style=False, sort_keys=False)
        print(f"SUCCESS yaml file generated: {output_file}")
    except Exception as e:
        print(f"ERROR writing YAML: {e}")


def prepare_dataset():
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    input_dir: Path = PROJECT_ROOT / "object_overlays"
    target_dir: Path = PROJECT_ROOT / "yolo_dataset"

    print(f"Input directory: {input_dir}")
    
    img_input_dir: Path = input_dir / "img"
    label_input_dir: Path = input_dir / "labels"

    for split in ["train", "val"]:
        (target_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (target_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    images: list = list(img_input_dir.glob("*"))
    random.shuffle(images)
    
    empty_file_counter: int = 0
    total_count: int = len(images)

    train_count: int = int(total_count * TRAIN_RATIO)

    print(f"Processing {total_count} files (Train: {train_count}, Val: {total_count - train_count})...")

    for i, img_path in enumerate(images):
        split_dir: str = "train" if i < train_count else "val"
        dest_img_path: Path = target_dir / split_dir / "images" / img_path.name
        dest_label_path: Path = target_dir / split_dir / "labels" / f"{img_path.stem}.txt"
        source_label_path: Path = label_input_dir / f"{img_path.stem}.txt"

        shutil.copy(img_path, dest_img_path)
        if source_label_path.exists():
            shutil.copy(source_label_path, dest_label_path)
        else:
            open(dest_label_path, 'a').close()
            empty_file_counter += 1

    class_names: list = ["Rocket"]
    print(f"Dataset preparation completed. Empty label files created: {empty_file_counter}")
    generate_dataset_yaml(class_names, target_dir / "dataset.yaml")


if __name__ == "__main__":
    prepare_dataset()