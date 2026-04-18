from pathlib import Path
from PIL import Image, ImageDraw


def bbox_test(in_img: Path, in_txt: Path) -> None:
    with open(in_txt, 'r') as f:
        line: str = f.readline().strip()
        if not line:
            print("Error: Empty annotation file.")
            return
        
        parts: list[str] = line.split()
        class_id: str = parts[0]
        x_center_norm: float = float(parts[1])
        y_center_norm: float = float(parts[2])
        width_norm: float = float(parts[3])
        height_norm: float = float(parts[4])
    
    img: Image.Image = Image.open(in_img)
    img_width: int = img.width
    img_height: int = img.height
    
    x_center: float = x_center_norm * img_width
    y_center: float = y_center_norm * img_height
    box_width: float = width_norm * img_width
    box_height: float = height_norm * img_height
    
    left: float = x_center - (box_width / 2.0)
    top: float = y_center - (box_height / 2.0)
    right: float = x_center + (box_width / 2.0)
    bottom: float = y_center + (box_height / 2.0)
    
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    draw.rectangle([(left, top), (right, bottom)], outline="red", width=3)
    
    draw.text((left, top - 10), f"Class: {class_id}", fill="red")
    img.show()

if __name__ == "__main__":
    image_path: Path = Path(r"C:\Python\Hachnarock2026\object_overlays\img/584126743_1276132124649427_568969889666505086_n_overlay1.png.jpg")
    label_path: Path = Path(r"C:\Python\Hachnarock2026\object_overlays\labels/584126743_1276132124649427_568969889666505086_n_overlay1.png.txt")
    
    bbox_test(image_path, label_path)