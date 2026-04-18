import random
from PIL import Image
from pathlib import Path


def overlay_image_and_get_yolo_labels(background_path: Path, object_path: Path, output_image_path: Path, output_label_path: Path, class_id: int = 0) -> None:
    object_img: Image.Image = Image.open(object_path).convert("RGBA")
    background_img: Image.Image = Image.open(background_path).convert("RGBA")

    bg_width: int = background_img.width
    bg_height: int = background_img.height
    
    orig_obj_width: int = object_img.width
    orig_obj_height: int = object_img.height

    min_scale_factor: float = 3.0
    max_scale_factor: float = 7.0

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

    pos_x: int = random.randint(0, max_x)
    pos_y: int = random.randint(0, max_y)
    
    background_img.paste(resized_object, (pos_x, pos_y), resized_object)
    
    final_image: Image.Image = background_img.convert("RGB")
    final_image.save(output_image_path)

    x_center_raw: float = pos_x + (obj_width / 2.0)
    y_center_raw: float = pos_y + (obj_height / 2.0)

    x_center: float = x_center_raw / bg_width
    y_center: float = y_center_raw / bg_height
    norm_width: float = obj_width / bg_width
    norm_height: float = obj_height / bg_height
    
    yolo_annotation: str = f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n"

    with open(output_label_path, 'w') as label_file:
        label_file.write(yolo_annotation)


if __name__ == "__main__":
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

    object_dir: Path = PROJECT_ROOT / "rocket"
    bg_input_dir: Path = PROJECT_ROOT / "raw_photos"
    output_dir: Path = PROJECT_ROOT / "object_overlays"
    
    out_img_dir: Path = output_dir / "img"
    out_label_dir: Path = output_dir / "labels"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_label_dir.mkdir(parents=True, exist_ok=True)
    
    bg_amount: int = len(list(bg_input_dir.glob("*.jpg")))
    for object_img in object_dir.glob("*.png"):
        print(f"Processing object image: {object_img.name}...")
        for i, bg_image in enumerate(bg_input_dir.glob("*.jpg")):
            print(f"\tProcessing background image {i + 1} / {bg_amount}", end='\r', flush=True)
            
            output_image_path: Path = out_img_dir / f"{bg_image.stem}_overlay{object_img.name}.jpg"
            output_label_path: Path = out_label_dir / f"{bg_image.stem}_overlay{object_img.name}.txt"
            overlay_image_and_get_yolo_labels(bg_image, object_img, output_image_path, output_label_path)
        
        print()