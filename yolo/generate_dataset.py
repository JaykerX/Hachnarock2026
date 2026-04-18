import csv
import random
from PIL import Image
from pathlib import Path


TRAIN_RATIO: float = 0.8


def overlay_image_and_get_openimage_annotation(background_path: Path, object_path: Path, output_image_path: Path, label_name: str, bg_image_shape: tuple[int, int] = (96, 96)) -> dict:
    object_img: Image.Image = Image.open(object_path).convert("RGBA")
    background_img: Image.Image = Image.open(background_path).convert("RGBA")

    bg_width: int = background_img.width
    bg_height: int = background_img.height

    orig_obj_width: int = object_img.width
    orig_obj_height: int = object_img.height

    min_scale_factor: float = 1.0
    max_scale_factor: float = 6.0

    max_possible_scale_w: float = bg_width / orig_obj_width
    max_possible_scale_h: float = bg_height / orig_obj_height
    safe_max_scale: float = min(max_scale_factor, max_possible_scale_w, max_possible_scale_h)

    if safe_max_scale < min_scale_factor:
        min_scale_factor = safe_max_scale * 0.5

    scale_factor: float = random.uniform(min_scale_factor, safe_max_scale)

    new_obj_width: int = int(orig_obj_width * scale_factor)
    new_obj_height: int = int(orig_obj_height * scale_factor)
    resized_object: Image.Image = object_img.resize((new_obj_width, new_obj_height), Image.Resampling.LANCZOS)

    obj_width: int = resized_object.width
    obj_height: int = resized_object.height

    max_x: int = bg_width - obj_width
    max_y: int = bg_height - obj_height

    pos_x: int = random.randint(0, max(0, max_x))
    pos_y: int = random.randint(0, max(0, max_y))

    background_img.paste(resized_object, (pos_x, pos_y), resized_object)
    final_image: Image.Image = background_img.convert("RGB").resize(bg_image_shape)
    final_image.save(output_image_path)

    x_min: float = pos_x / bg_width
    y_min: float = pos_y / bg_height
    x_max: float = (pos_x + obj_width) / bg_width
    y_max: float = (pos_y + obj_height) / bg_height

    image_id: str = output_image_path.stem

    return {
        "ImageID": image_id,
        "LabelName": label_name,
        "XMin": round(x_min, 10),
        "XMax": round(x_max, 10),
        "YMin": round(y_min, 10),
        "YMax": round(y_max, 10),
    }


def write_annotations_csv(annotations: list[dict], output_path: Path) -> None:
    fieldnames = ["ImageID", "LabelName", "XMin", "XMax", "YMin", "YMax"]
    with open(output_path, 'w', newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(annotations)


def write_class_descriptions_csv(label_names: list[str], output_path: Path) -> None:
    with open(output_path, 'w', newline="") as f:
        writer = csv.writer(f)
        for label in label_names:
            writer.writerow([label, label])


if __name__ == "__main__":
    LABEL_NAME: str = "Rocket"
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

    object_dir: Path = PROJECT_ROOT / "rocket"
    bg_input_dir: Path = PROJECT_ROOT / "raw_photos"
    output_dir: Path = PROJECT_ROOT / "model_dataset"

    test_dir: Path = output_dir / "testing"
    train_dir: Path = output_dir / "training"
    test_dir.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)

    object_images: list[Path] = list(object_dir.glob('*'))
    all_bg_images: list[Path] = list(bg_input_dir.glob('*'))
    
    bg_amount: int = len(all_bg_images)
    label_names: list[str] = [LABEL_NAME]
    
    test_annotations: list[dict] = []
    train_annotations: list[dict] = []

    for object_img in object_images:
        print(f"Processing object: {object_img.name}...")
        
        random.shuffle(all_bg_images)
        split_idx: int = int(bg_amount * TRAIN_RATIO)
        test_bgs: list[Path] = all_bg_images[split_idx:]
        train_bgs: list[Path] = all_bg_images[:split_idx]

        for i, bg_image in enumerate(train_bgs):
            print(f"\t[train] {i + 1}/{len(train_bgs)}", end='\r', flush=True)
            out_filename: str = f"{bg_image.stem}_overlay_{object_img.stem}.jpg"
            
            output_image_path: Path = train_dir / out_filename
            annotation = overlay_image_and_get_openimage_annotation(bg_image, object_img, output_image_path, LABEL_NAME)
            train_annotations.append(annotation)
        print()

        for i, bg_image in enumerate(test_bgs):
            print(f"\t[test]  {i + 1}/{len(test_bgs)}", end='\r', flush=True)
            out_filename = f"{bg_image.stem}_overlay_{object_img.stem}.jpg"
            output_image_path = test_dir / out_filename
            annotation = overlay_image_and_get_openimage_annotation(bg_image, object_img, output_image_path, LABEL_NAME)
            test_annotations.append(annotation)
        print()


    write_annotations_csv(test_annotations, test_dir / "_annotations.csv")
    write_annotations_csv(train_annotations, train_dir / "_annotations.csv")
    write_class_descriptions_csv(label_names, output_dir / "class-descriptions.csv")

    print(f"\nDone.")
    print(f"  Training images : {len(train_annotations)}  -> {train_dir}")
    print(f"  Testing images  : {len(test_annotations)}   -> {test_dir}")
    print(f"  Annotations CSV : {train_dir / '_annotations.csv'}")
    print(f"                    {test_dir / '_annotations.csv'}")
    print(f"  Class desc.     : {output_dir / 'class-descriptions.csv'}")
