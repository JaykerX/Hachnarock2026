from PIL import Image
from pathlib import Path


def adjust_rocket_size(folder: Path) -> None:
    target_size: tuple[int, int] = (120, 120)
    
    for img_path in folder.glob('*'):
        img: Image.Image = Image.open(img_path)
        resized_img: Image.Image = img.resize(target_size)
        resized_img.save(img_path)
                
        print(f"Processed: {img_path.name}")

#jestem tu - Ola
if __name__ == "__main__":
    images_folder: Path = Path(r"C:\Python\Hachnarock2026\rocket")
    adjust_rocket_size(images_folder)