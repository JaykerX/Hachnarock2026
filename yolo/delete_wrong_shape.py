from PIL import Image
from pathlib import Path


def delete_imgs(folder: Path) -> None:
    for img_path in folder.glob('*'):
        img: Image.Image = Image.open(img_path)
        if img.size != (4284, 5712):
            print(f"Deleting {img_path} with size {img.size}")
            del img
            img_path.unlink()


if __name__ == "__main__":
    images_folder: Path = Path(r"C:\Python\Hachnarock2026\raw_photos")
    delete_imgs(images_folder) 