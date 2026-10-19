"""Regenerates the HafzVault icon, adaptive icon and splash emblem. Needs: pip install pillow
Run from mobile/:  python tools/make_icons.py
"""
from PIL import Image, ImageDraw

FOREST = (20, 83, 45, 255)
GOLD = (201, 162, 39, 255)
WHITE = (255, 255, 255, 255)
SS = 2  # supersampling factor
SIZE = 1024


def emblem(scale=1.0):
    """Gold disc with a white receipt and a check mark, on a transparent 1024px canvas."""
    s = SIZE * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(x, y):  # transform a 1024-space point around the centre
        c = SIZE / 2
        return ((c + (x - c) * scale) * SS, (c + (y - c) * scale) * SS)

    def box(x0, y0, x1, y1):
        return [*P(x0, y0), *P(x1, y1)]

    d.ellipse(box(112, 112, 912, 912), fill=GOLD)
    pts = [P(352, 262), P(672, 262)]
    for i in range(9):  # zig-zag bottom edge
        pts.append(P(672 - 40 * i, 742 if i % 2 == 0 else 700))
    d.polygon(pts, fill=WHITE)
    for y, x1 in [(340, 624), (410, 590), (480, 624)]:
        d.rounded_rectangle(box(400, y, x1, y + 28), radius=14 * scale * SS, fill=FOREST)
    w = int(38 * scale * SS)
    a, b, c = P(430, 610), P(492, 668), P(610, 548)
    d.line([a, b, c], fill=GOLD, width=w, joint="curve")
    for p in (a, c):
        r = w / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=GOLD)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def on_forest(em):
    bg = Image.new("RGBA", (SIZE, SIZE), FOREST)
    bg.alpha_composite(em)
    return bg.convert("RGB")  # store icons must not have transparency


if __name__ == "__main__":
    on_forest(emblem(1.0)).save("assets/icon.png")
    emblem(0.82).save("assets/adaptive-icon.png")  # inside Android's safe zone
    emblem(1.0).save("assets/splash-icon.png")
    print("wrote assets/icon.png, adaptive-icon.png, splash-icon.png")
