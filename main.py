#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one invented passport spread (1024x1024 PNG) for the fictional
Republic of Velkaria and writes it to $MAKEFUN_OUTPUT_DIR/entry.png.

Everything is drawn procedurally with Pillow: no network, no pasted
images, no randomness, so two runs are byte-identical.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette: a working document, not a poster ---------------------------
PAPER = (244, 239, 226)      # aged cream paper
PAPER_DARK = (232, 225, 205)
INK = (29, 43, 74)           # deep navy ink
INK_SOFT = (74, 88, 120)
BURGUNDY = (122, 36, 54)
TEAL = (18, 92, 96)
GOLD = (176, 141, 63)
STAMP_BLUE = (38, 84, 150)
STAMP_RED = (168, 52, 44)
STAMP_GREEN = (46, 110, 72)
RULE = (150, 142, 120)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/liberation/",
]


def _font(name, size, bold=False):
    for d in FONT_DIRS:
        for cand in (name,):
            p = os.path.join(d, cand)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def font_sans(size, bold=False):
    return _font("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size, bold)


def font_serif(size, bold=False):
    return _font("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size, bold)


def font_mono(size):
    return _font("DejaVuSansMono.ttf", size)


def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def centred(draw, cx, y, s, f, fill=INK):
    text(draw, (cx, y), s, f, fill=fill, anchor="ma")


def guilloche(draw, box, step=7, color=(203, 194, 168)):
    """Faint wavy security lines across a rectangle."""
    x0, y0, x1, y1 = box
    for x in range(x0, x1, step):
        pts = []
        for y in range(y0, y1 + 1, 6):
            import math
            pts.append((x + 3 * math.sin((y - y0) / 26.0), y))
        draw.line(pts, fill=color, width=1)


def coat_of_arms(draw, cx, cy, s):
    """Velkaria's arms: shield, three waves, one star."""
    w, h = s, int(s * 1.15)
    x0, y0 = cx - w // 2, cy - h // 2
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h // 2),
           (cx, y0 + h), (x0, y0 + h // 2)]
    draw.polygon(pts, outline=GOLD, width=3)
    draw.polygon(pts, fill=(232, 225, 205))
    # three waves
    for i, yy in enumerate((y0 + h // 3, y0 + h // 2, y0 + 2 * h // 3)):
        draw.arc([x0 + 6, yy - 6, x0 + w - 6, yy + 10], 0, 180, fill=TEAL, width=2)
    # star above the waves
    sx, sy, r = cx, y0 + h // 5, 9
    import math
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=BURGUNDY)


def portrait(draw, box):
    """Stylised portrait of the holder: drawn face, no photo."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(214, 205, 182), outline=INK, width=2)
    # backdrop: pale sky gradient bands
    for i in range(6):
        draw.rectangle([x0, y0 + i * h // 6, x1, y0 + (i + 1) * h // 6],
                       fill=(222 + i, 216 + i, 196 + i))
    cx = (x0 + x1) // 2
    # shoulders / jacket
    draw.polygon([(x0 + 8, y1), (x0 + w * 0.28, y0 + h * 0.72),
                  (cx, y0 + h * 0.66), (x0 + w * 0.72, y0 + h * 0.72),
                  (x1 - 8, y1)], fill=(58, 74, 96))
    draw.polygon([(cx - 14, y0 + h * 0.68), (cx, y0 + h * 0.78),
                  (cx + 14, y0 + h * 0.68), (cx, y0 + h * 0.66)],
                 fill=(244, 239, 226))
    # neck + head
    draw.rectangle([cx - 13, y0 + h * 0.56, cx + 13, y0 + h * 0.70],
                   fill=(198, 158, 124))
    draw.ellipse([cx - 42, y0 + h * 0.16, cx + 42, y0 + h * 0.62],
                 fill=(208, 168, 132), outline=(150, 110, 82), width=2)
    # hair: dark bob
    draw.pieslice([cx - 46, y0 + h * 0.10, cx + 46, y0 + h * 0.44],
                  180, 360, fill=(52, 40, 34))
    draw.rectangle([cx - 46, y0 + h * 0.28, cx - 34, y0 + h * 0.52],
                   fill=(52, 40, 34))
    draw.rectangle([cx + 34, y0 + h * 0.28, cx + 46, y0 + h * 0.52],
                   fill=(52, 40, 34))
    # eyes, brows, nose, mouth
    for ex in (cx - 18, cx + 18):
        draw.ellipse([ex - 6, y0 + h * 0.36, ex + 6, y0 + h * 0.40],
                     fill=(38, 32, 28))
        draw.line([ex - 9, y0 + h * 0.33, ex + 9, y0 + h * 0.325],
                  fill=(52, 40, 34), width=2)
    draw.line([cx, y0 + h * 0.40, cx - 3, y0 + h * 0.49], fill=(150, 110, 82), width=2)
    draw.line([cx - 8, y0 + h * 0.53, cx + 8, y0 + h * 0.53], fill=(128, 74, 66), width=2)
    # ghost image (security print, bottom right of the frame)
    draw.ellipse([x1 - 34, y1 - 34, x1 - 6, y1 - 6], outline=(150, 142, 120), width=1)
    text(draw, (x1 - 20, y1 - 26), "VK", font_mono(9), fill=(150, 142, 120), anchor="mm")


def field(draw, x, y, label, value, label2=None, vfont=None, lfont=None):
    lfont = lfont or font_sans(11)
    vfont = vfont or font_sans(17, bold=True)
    text(draw, (x, y), label, lfont, fill=INK_SOFT)
    if label2:
        text(draw, (x + 210, y), label2, lfont, fill=INK_SOFT)
    text(draw, (x, y + 14), value, vfont)


def stamp_oval(draw, cx, cy, rx, ry, lines, color, angle=0):
    """Round border-control stamp; text lines centred."""
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=color, width=3)
    draw.ellipse([cx - rx + 6, cy - ry + 6, cx + rx - 6, cy + ry - 6],
                 outline=color, width=1)
    f = font_sans(13, bold=True)
    fs = font_sans(10)
    for i, ln in enumerate(lines):
        yy = cy - (len(lines) - 1) * 11 + i * 22
        centred(draw, cx, yy, ln, f if i == 0 else fs, fill=color)


def stamp_rect(draw, box, lines, color):
    draw.rectangle(box, outline=color, width=3)
    draw.rectangle([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5],
                   outline=color, width=1)
    cx = (box[0] + box[2]) // 2
    cy = (box[1] + box[3]) // 2
    for i, ln in enumerate(lines):
        yy = cy - (len(lines) - 1) * 10 + i * 20
        centred(draw, cx, yy, ln, font_sans(12, bold=True) if i == 0 else font_sans(10),
                fill=color)


def draw_spread():
    img = Image.new("RGB", (W, H), (38, 44, 58))
    d = ImageDraw.Draw(img, "RGBA")

    # --- the open booklet ----------------------------------------------
    d.rectangle([28, 28, 996, 996], fill=PAPER, outline=GOLD, width=3)
    d.rectangle([36, 36, 988, 988], outline=RULE, width=1)
    # spine
    d.rectangle([508, 36, 516, 988], fill=(206, 196, 168))
    d.line([512, 36, 512, 988], fill=(150, 142, 120), width=2)

    # ================= LEFT PAGE: data page ============================
    L = 44          # left margin
    guilloche(d, (L, 52, 500, 300))
    coat_of_arms(d, 96, 104, 62)
    centred(d, 290, 62, "REPUBLIC OF VELKARIA", font_serif(23, bold=True))
    centred(d, 290, 92, "REPUBLIKA VELKARIJA  ·  PASSPORT", font_sans(12, bold=True),
            fill=BURGUNDY)
    centred(d, 290, 112, "PASSPORT  ·  TYPE P  ·  No. VK 4829137", font_sans(12))
    d.line([L, 138, 500, 138], fill=INK, width=2)
    d.line([L, 142, 500, 142], fill=INK, width=1)

    # portrait + signature strip
    portrait(d, (L, 158, 196, 348))
    text(d, (L, 356), "SIGNATURE OF HOLDER", font_sans(10), fill=INK_SOFT)
    d.line([L, 386, 196, 386], fill=INK, width=1)
    # script-like signature
    d.line([(L + 8, 378), (L + 30, 366), (L + 52, 380), (L + 78, 364),
            (L + 104, 378), (L + 132, 368), (L + 150, 376)],
           fill=INK, width=2)

    # data fields, two columns
    fx, fy = 214, 158
    field(d, fx, fy, "SURNAME / PREZIME", "KOVAC")
    field(d, fx, fy + 56, "GIVEN NAMES / IME", "MARA ILIN")
    field(d, fx, fy + 112, "NATIONALITY / DRŽAVLJANSTVO", "VELKARIAN")
    field(d, fx, fy + 168, "DATE OF BIRTH / ROĐENJE", "02 JUN 1991")
    field(d, fx, fy + 224, "PLACE OF BIRTH / MJESTO", "PORT AURELIA")
    field(d, fx, fy + 280, "SEX / SPOL", "F")
    field(d, fx, fy + 336, "DATE OF ISSUE / IZDANO", "14 MAR 2024")
    field(d, fx, fy + 392, "DATE OF EXPIRY / VRIJEDI DO", "14 MAR 2034")
    field(d, fx, fy + 448, "AUTHORITY / TIJELO", "MINISTRY OF THE INTERIOR",
          vfont=font_sans(15, bold=True))
    field(d, fx, fy + 504, "PLACE OF ISSUE", "PORT AURELIA",
          vfont=font_sans(15, bold=True))
    # extra holder details fill the lower data page, as on a real document
    field(d, fx, fy + 560, "HEIGHT / VISINA", "172 CM", vfont=font_sans(15, bold=True))
    field(d, fx + 210, fy + 560, "EYES / OČI", "BROWN", vfont=font_sans(15, bold=True))
    field(d, fx, fy + 616, "PERSONAL No. / OSOBNI BROJ", "VLK-910602-4417",
          vfont=font_sans(15, bold=True))

    # machine-readable zone
    mz_y = 872
    d.rectangle([L, mz_y - 12, 500, mz_y + 62], fill=(232, 225, 205))
    d.line([L, mz_y - 12, 500, mz_y - 12], fill=INK, width=1)
    mrz1 = "P<VLKKOVAC<<MARA<ILIN<<<<<<<<<<<<<<<<<<<<<<"
    mrz2 = "VK4829137<8VLK9106021F3403141<<<<<<<<<<<<<<04"
    text(d, (L + 4, mz_y), mrz1, font_mono(16))
    text(d, (L + 4, mz_y + 24), mrz2, font_mono(16))
    text(d, (L, mz_y + 52), "MACHINE READABLE ZONE — CHECK DIGITS VERIFIED AT ISSUE",
         font_sans(9), fill=INK_SOFT)

    # ================= RIGHT PAGE: visas & stamps ======================
    R = 524
    guilloche(d, (R, 52, 980, 180))
    centred(d, 752, 62, "VISAS", font_serif(23, bold=True))
    centred(d, 752, 92, "VIZE  ·  ENTRY AND EXIT STAMPS", font_sans(12, bold=True),
            fill=BURGUNDY)
    d.line([R, 138, 980, 138], fill=INK, width=2)
    d.line([R, 142, 980, 142], fill=INK, width=1)

    # --- visa sticker: Thalassia, the telling detail -------------------
    vx, vy, vw, vh = R + 8, 158, 440, 190
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=(226, 232, 224),
                outline=STAMP_GREEN, width=2)
    d.rectangle([vx + 6, vy + 6, vx + vw - 6, vy + vh - 6],
                outline=STAMP_GREEN, width=1)
    text(d, (vx + 16, vy + 12), "KINGDOM OF THALASSIA", font_sans(15, bold=True),
         fill=STAMP_GREEN)
    text(d, (vx + 16, vy + 34), "VISA — SINGLE ENTRY  ·  No. TH-771204",
         font_sans(12, bold=True), fill=STAMP_GREEN)
    d.line([vx + 16, vy + 56, vx + vw - 16, vy + 56], fill=STAMP_GREEN, width=1)
    visa_rows = [
        ("VALID:", "22 MAY 2024 — 19 AUG 2024  (90 DAYS)"),
        ("PURPOSE:", "TOURISM — NO EMPLOYMENT"),
        ("FEE PAID:", "40 THALERS  ·  STAMP No. 1187"),
        ("CONDITION:", "REGISTER WITH POLICE WITHIN 72 HOURS"),
    ]
    for i, (k, v) in enumerate(visa_rows):
        text(d, (vx + 16, vy + 66 + i * 24), k, font_sans(12, bold=True),
             fill=STAMP_GREEN)
        text(d, (vx + 118, vy + 66 + i * 24), v, font_sans(12), fill=INK)
    text(d, (vx + 16, vy + 166), "THALASSIA WELCOMES VISITORS WHO MIND THE HARBOUR CURFEW.",
         font_sans(10), fill=INK_SOFT)

    # --- stamps: a plausible travel history, all after issue 14 MAR 2024
    stamp_oval(d, 640, 448, 92, 62,
               ["THALASSIA", "ARRIVAL", "22 MAY 2024", "MERIDIANA"], STAMP_BLUE)
    stamp_rect(d, (752, 392, 972, 500),
               ["NORDMARK", "DEPARTURE", "03 SEP 2024", "KALDVIK APT"], STAMP_RED)
    stamp_oval(d, 640, 580, 92, 62,
               ["KESTREL ISLES", "ENTRY", "17 JAN 2025", "PORT SORELL"], STAMP_GREEN)
    stamp_rect(d, (752, 524, 972, 632),
               ["THALASSIA", "DEPARTURE", "09 FEB 2025", "MERIDIANA"], STAMP_BLUE)
    stamp_oval(d, 752, 742, 100, 66,
               ["VELKARIA", "RE-ENTRY", "28 JUN 2025", "PORT AURELIA"], BURGUNDY)

    # --- footer note on the right page ----------------------------------
    d.line([R, 838, 980, 838], fill=RULE, width=1)
    text(d, (R, 852), "NOTES / NAPOMENE", font_sans(11, bold=True), fill=INK_SOFT)
    text(d, (R, 870), "1. This passport remains the property of the Republic of Velkaria.",
         font_sans(11))
    text(d, (R, 888), "2. Loss or theft must be reported to the nearest Velkarian mission.",
         font_sans(11))
    text(d, (R, 906), "3. Holders travelling to Thalassia must carry proof of onward travel.",
         font_sans(11))
    text(d, (R, 924), "4. Pages 4–32 reserved for visas. Stamps outside the boxes are void.",
         font_sans(11))
    centred(d, 752, 952, "VK 4829137  ·  ISSUED PORT AURELIA  ·  14 MAR 2024",
            font_sans(10), fill=INK_SOFT)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = draw_spread()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    size = os.path.getsize(path)
    print(f"wrote {path}: {img.size[0]}x{img.size[1]} {size} bytes sha256={digest}")
    if size > 1_048_576:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    if img.size != (1024, 1024):
        print("ERROR: entry.png is not 1024x1024", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
