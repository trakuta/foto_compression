from PIL import Image
from pathlib import Path
import shutil

# Настройки
INBOX = Path("inbox")
OUTBOX = Path("outbox")
QUALITY = 50  # качество JPEG (1-100), чем меньше — тем сильнее сжатие

# Расширения, которые обрабатываем
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def process_image(src: Path, dst: Path) -> None:
    """Уменьшает качество изображения и сохраняет по новому пути."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as img:
        # Конвертируем в RGB, если нужно (например, для PNG с прозрачностью -> JPEG)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # Для JPEG сохраняем с заданным качеством
        if dst.suffix.lower() in {".jpg", ".jpeg"}:
            img.save(dst, "JPEG", quality=QUALITY, optimize=True)
        elif dst.suffix.lower() == ".webp":
            img.save(dst, "WEBP", quality=QUALITY)
        elif dst.suffix.lower() == ".png":
            # Для PNG используем compress_level (0-9)
            img.save(dst, "PNG", optimize=True, compress_level=9)
        else:
            # Для остальных форматов сохраняем как JPEG с новым расширением
            dst = dst.with_suffix(".jpg")
            img.save(dst, "JPEG", quality=QUALITY, optimize=True)


def main() -> None:
    if not INBOX.exists():
        print(f"Папка {INBOX} не найдена")
        return

    for src in INBOX.rglob("*"):
        if not src.is_file():
            continue

        if src.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        # Сохраняем относительный путь (дерево каталогов)
        rel_path = src.relative_to(INBOX)
        dst = OUTBOX / rel_path

        # Для не-JPEG форматов меняем расширение на .jpg (кроме png/webp)
        if src.suffix.lower() in {".png", ".webp"}:
            dst = dst.with_suffix(src.suffix.lower())
        elif src.suffix.lower() not in {".jpg", ".jpeg"}:
            dst = dst.with_suffix(".jpg")

        try:
            process_image(src, dst)
            print(f"OK: {src} -> {dst}")
        except Exception as e:
            print(f"Ошибка при обработке {src}: {e}")


if __name__ == "__main__":
    main()
