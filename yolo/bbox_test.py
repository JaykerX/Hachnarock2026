import csv
from pathlib import Path
from PIL import Image, ImageDraw


def bbox_test(split_dir: Path, image_stem: str) -> None:
    annotations_path: Path = split_dir / "_annotations.csv"
    image_path: Path = next(split_dir.glob(f"{image_stem}.*"), None) # type: ignore

    img: Image.Image = Image.open(image_path).convert("RGB")
    
    img_width: int = img.width
    img_height: int = img.height
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)

    rows_found: int = 0
    with open(annotations_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ImageID"] != image_stem:
                continue

            x_min: float = float(row["XMin"]) * img_width
            x_max: float = float(row["XMax"]) * img_width
            y_min: float = float(row["YMin"]) * img_height
            y_max: float = float(row["YMax"]) * img_height

            draw.rectangle([(x_min, y_min), (x_max, y_max)], outline="blue")
            draw.text((x_min, max(0, y_min - 12)), row["LabelName"], fill="blue")
            rows_found += 1

    if rows_found == 0:
        print(f"Warning: No annotations found for ImageID='{image_stem}'")
    else:
        print(f"Drew {rows_found} bbox(es) for '{image_stem}'")

    img.show()


if __name__ == "__main__":
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    output_dir: Path = PROJECT_ROOT / "model_dataset"

    split_dir: Path = output_dir / "training"
    image_stem: str = "IMG_8476_overlay_1"

    bbox_test(split_dir, image_stem)