"""Draw assets/icon.ico (space background, planet, stars and a ½ fraction). Needs Pillow (dev only)."""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"


def draw(size: int = 256) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=(18, 22, 60, 255))
    rnd = random.Random(7)
    for _ in range(40):
        x, y, r = rnd.randrange(size), rnd.randrange(size), rnd.choice([1, 1, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randrange(120, 255)))
    d.ellipse([size * 0.52, size * 0.52, size * 0.95, size * 0.95], fill=(255, 140, 50, 255))
    d.arc([size * 0.40, size * 0.66, size * 1.07, size * 0.82], 160, 380, fill=(255, 220, 120, 255), width=6)
    try:
        font = ImageFont.truetype("arialbd.ttf", int(size * 0.30))
    except OSError:
        font = ImageFont.load_default()
    for text, y in (("1", 0.06), ("2", 0.40)):
        d.text((size * 0.16, size * y), text, font=font, fill=(120, 230, 255, 255))
    d.line([size * 0.10, size * 0.40, size * 0.42, size * 0.40], fill=(120, 230, 255, 255), width=10)
    return img


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    draw().save(OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    draw().save(OUT.with_suffix(".png"))
    print(f"wrote {OUT}")
