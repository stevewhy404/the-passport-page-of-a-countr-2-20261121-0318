#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws an invented passport spread for the Republic of Velmoria:
a data page (portrait, fields, MRZ with real ICAO check digits) and
a visa/stamp page whose stamps tell one coherent trip.

Country: Republic of Velmoria (does not exist)
Capital / place of issue: Tarnwick
Neighbours (also invented): Dravnia, Caldoria
Holder: Mara Elin Ilsen, born 12 FEB 1991 in Tarnwick
Passport issued 14 MAR 2024, expires 14 MAR 2034
Trip: Tarnwick -> Dravnia (03 JUN 2024) -> Caldoria (19 JUN 2024)
       -> home to Tarnwick (02 JUL 2024). Every stamp is after issue.

Deterministic: fixed seed, fixed fonts, no network, no clock.
Writes /output/entry.png (1024x1024, PNG).
"""

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FONT_DIR}/dejavu/DejaVuSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/dejavu/DejaVuSerif.ttf"
SERIF_I = f"{FONT_DIR}/liberation/LiberationSerif-Italic.ttf"
SANS = f"{FONT_DIR}/dejavu/DejaVuSans.ttf"
SANS_B = f"{FONT_DIR}/dejavu/DejaVuSans-Bold.ttf"
MONO = f"{FONT_DIR}/dejavu/DejaVuSansMono.ttf"
MONO_B = f"{FONT_DIR}/dejavu/DejaVuSansMono-Bold.ttf"

PAPER = (247, 243, 232)
PAPER_DARK = (233, 226, 205)
INK = (34, 32, 28)
GREEN = (29, 77, 56)
GREEN_SOFT = (74, 116, 96)
GREY = (110, 105, 92)
RULE = (180, 170, 145)

rng = random.Random(20261121)


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- MRZ ----
def mrz_check(text):
    """ICAO 9303 check digit: weights 7,3,1; A=10..Z=35, '<'=0."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(text):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - 55
        total += v * weights[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<VLMILSEN<<MARA<ELIN<<<<<<<<<<<<<<<<<<<<"
    line1 = line1[:44].ljust(44, "<")
    doc = "VL4839201"
    doc_c = mrz_check(doc)
    nat = "VLM"
    dob = "910212"
    dob_c = mrz_check(dob)
    sex = "F"
    exp = "340314"
    exp_c = mrz_check(exp)
    opt = "<" * 15  # ICAO TD3: optional data occupies positions 29-43
    core = doc + doc_c + nat + dob + dob_c + sex + exp + exp_c + opt
    line2 = core + mrz_check(core)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# -------------------------------------------------------------- helpers ----
def stamp_layer(w, h, color, lines, rotation, border=3):
    """One ink stamp: rounded border + centred lines, rotated, alpha ink."""
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = 20, 20, 20 + w, 20 + h
    d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                        outline=color + (215,), width=border)
    d.rounded_rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], radius=7,
                        outline=color + (150,), width=1)
    cy = y0 + 12
    for text, size, bold in lines:
        f = font(SANS_B if bold else SANS, size)
        d.text(((x0 + x1) // 2, cy), text, font=f, fill=color + (225,),
               anchor="ma")
        cy += size + 5
    return layer.rotate(rotation, resample=Image.BICUBIC, expand=False)


def draw_wrapped(d, box, text, f, fill, leading=None):
    """Centred wrapped text inside box (x0, y0, x1, y1); returns bottom y."""
    x0, y0, x1, _ = box
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= x1 - x0:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    leading = leading or int(f.size * 1.35)
    y = y0
    for line in lines:
        d.text(((x0 + x1) // 2, y), line, font=f, fill=fill, anchor="ma")
        y += leading
    return y


def draw_portrait(d, box):
    """Stylised ID-photo portrait, drawn procedurally (flat vector style)."""
    x0, y0, x1, y1 = box
    # photo background: soft blue-grey gradient
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, y1 - y0)
        c = tuple(int(168 + (120 - 168) * t) for _ in range(3))
        c = (c[0], c[1] + 8, c[2] + 18)
        d.line([(x0, yy), (x1, yy)], fill=c)
    cx = (x0 + x1) // 2
    # shoulders / jacket
    d.pieslice([cx - 78, y1 - 118, cx + 78, y1 + 60], 180, 360,
               fill=(44, 74, 66))
    d.polygon([(cx - 78, y1), (cx - 30, y1 - 96), (cx + 30, y1 - 96),
               (cx + 78, y1)], fill=(44, 74, 66))
    # shirt V + collar
    d.polygon([(cx - 16, y1 - 92), (cx, y1 - 52), (cx + 16, y1 - 92)],
              fill=(238, 234, 222))
    # neck
    d.rectangle([cx - 15, y1 - 128, cx + 15, y1 - 88], fill=(198, 158, 122))
    # head
    d.ellipse([cx - 42, y1 - 196, cx + 42, y1 - 96], fill=(214, 176, 140))
    # hair: shoulder-length, frames the face
    d.pieslice([cx - 48, y1 - 204, cx + 48, y1 - 108], 180, 360,
               fill=(58, 40, 28))
    d.ellipse([cx - 48, y1 - 200, cx - 18, y1 - 120], fill=(58, 40, 28))
    d.ellipse([cx + 18, y1 - 200, cx + 48, y1 - 120], fill=(58, 40, 28))
    d.rectangle([cx - 48, y1 - 150, cx - 38, y1 - 92], fill=(58, 40, 28))
    d.rectangle([cx + 38, y1 - 150, cx + 48, y1 - 92], fill=(58, 40, 28))
    # face hints: brows, eyes, nose, mouth
    for sx in (-1, 1):
        ex = cx + sx * 17
        d.line([(ex - 9, y1 - 152), (ex + 9, y1 - 154)],
               fill=(58, 40, 28), width=2)
        d.ellipse([ex - 5, y1 - 146, ex + 5, y1 - 138], fill=(40, 30, 24))
    d.line([(cx, y1 - 140), (cx - 2, y1 - 124)], fill=(186, 146, 112), width=2)
    d.arc([cx - 10, y1 - 118, cx + 10, y1 - 106], 15, 165,
          fill=(150, 96, 78), width=2)


def crest(d, cx, cy, r):
    """Velmoria crest: ring, mountain, wave, star."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=3)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              outline=GREEN_SOFT, width=1)
    d.polygon([(cx - r + 8, cy + 8), (cx - 4, cy - r + 12),
               (cx + 6, cy + 2), (cx + 12, cy - r + 16),
               (cx + r - 8, cy + 8)], fill=GREEN)
    d.arc([cx - r + 9, cy + 2, cx + r - 9, cy + r - 2], 0, 180,
          fill=GREEN_SOFT, width=2)
    d.arc([cx - r + 12, cy + 8, cx + r - 12, cy + r + 2], 0, 180,
          fill=GREEN_SOFT, width=2)


# ----------------------------------------------------------------- main ----
def build():
    img = Image.new("RGB", (W, H), (226, 218, 196))
    d = ImageDraw.Draw(img, "RGBA")

    # paper texture: faint deterministic speckle
    for _ in range(2600):
        x, y = rng.randrange(W), rng.randrange(H)
        v = rng.choice([(235, 230, 214), (242, 238, 226)])
        d.point((x, y), fill=v)

    # two pages
    d.rectangle([28, 28, 500, 996], fill=PAPER, outline=RULE, width=2)
    d.rectangle([524, 28, 996, 996], fill=PAPER, outline=RULE, width=2)
    # spine shadow
    for i in range(14):
        d.line([(500 - i, 30), (500 - i, 994)], fill=(0, 0, 0, 10 - i // 2))
        d.line([(524 + i, 30), (524 + i, 994)], fill=(0, 0, 0, 10 - i // 2))

    # ---- faint watermark on the data page ----
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wf = font(SERIF_B, 44)
    for yy in range(180, 960, 150):
        wd.text((264, yy), "VELMORIA", font=wf, fill=(29, 77, 56, 14),
                anchor="mm")
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================================================= LEFT: DATA PAGE ====
    crest(d, 76, 76, 26)
    d.text((112, 52), "REPUBLIC OF VELMORIA", font=font(SERIF_B, 25),
           fill=GREEN)
    d.text((112, 84), "P A S S P O R T", font=font(SANS_B, 13), fill=INK)
    d.text((300, 84), "PASSEPORT", font=font(SANS, 12), fill=GREY)
    d.line([(48, 118), (480, 118)], fill=GREEN, width=2)
    d.line([(48, 122), (480, 122)], fill=RULE, width=1)

    # portrait
    d.rectangle([48, 140, 198, 330], outline=INK, width=2)
    draw_portrait(d, (50, 142, 196, 328))
    d.text((123, 336), "PHOTO 35 x 45 mm", font=font(SANS, 9), fill=GREY,
           anchor="ma")

    # fields beside the portrait
    fields = [
        ("SURNAME", "ILSEN"),
        ("GIVEN NAMES", "MARA ELIN"),
        ("NATIONALITY", "VELMORIAN"),
        ("DATE OF BIRTH", "12 FEB 1991"),
        ("PLACE OF BIRTH", "TARNWICK"),
        ("SEX", "F"),
    ]
    y = 142
    for label, value in fields:
        d.text((214, y), label, font=font(SANS, 10), fill=GREY)
        d.text((214, y + 13), value, font=font(SANS_B, 16), fill=INK)
        y += 33

    # second block of fields
    d.line([(48, 372), (480, 372)], fill=RULE, width=1)
    block = [
        ("DATE OF ISSUE", "14 MAR 2024", "DATE OF EXPIRY", "14 MAR 2034"),
        ("AUTHORITY", "MINISTRY OF PASSAGE", "DOCUMENT NO.", "VL 4839201"),
    ]
    y = 388
    for l1, v1, l2, v2 in block:
        d.text((48, y), l1, font=font(SANS, 10), fill=GREY)
        d.text((48, y + 13), v1, font=font(SANS_B, 15), fill=INK)
        d.text((268, y), l2, font=font(SANS, 10), fill=GREY)
        d.text((268, y + 13), v2, font=font(SANS_B, 15), fill=INK)
        y += 44
    d.text((48, y + 2), "PLACE OF ISSUE  —  TARNWICK, VELMORIA",
           font=font(SANS, 10), fill=GREY)
    d.line([(48, y + 30), (480, y + 30)], fill=RULE, width=1)

    # language column: the paperwork detail on the data page
    d.text((48, 520), "HOLDER'S NOTE — READ IN VELMORIAN AND ENGLISH",
           font=font(SANS_B, 11), fill=GREEN)
    note = ("This passport remains the property of the Republic of "
            "Velmoria. If found, return it to the nearest "
            "harbourmaster or to the Ministry of Passage, Tarnwick.")
    draw_wrapped(d, (48, 542, 480, 620), note, font(SERIF, 13), INK)

    # MRZ
    d.rectangle([40, 880, 488, 962], fill=PAPER_DARK)
    line1, line2 = build_mrz()
    mf = font(MONO, 15)
    d.text((48, 892), line1, font=mf, fill=INK)
    d.text((48, 922), line2, font=mf, fill=INK)
    d.text((48, 968), "1", font=font(SANS, 10), fill=GREY)

    # ============================================ RIGHT: STAMP PAGE ======
    d.text((548, 52), "VISAS", font=font(SERIF_B, 25), fill=GREEN)
    d.text((548, 84), "ARRIVALS  ·  DEPARTURES", font=font(SANS, 12),
           fill=GREY)
    d.line([(548, 118), (972, 118)], fill=GREEN, width=2)
    d.line([(548, 122), (972, 122)], fill=RULE, width=1)

    BLUE = (31, 78, 121)
    ST_GREEN = (46, 107, 52)
    PURPLE = (91, 58, 122)
    RED = (160, 36, 34)

    stamps = [
        ("DEPARTURE", "VELMORIA", "TARNWICK AIRPORT", "02 JUN 2024",
         BLUE, -8, (548, 140)),
        ("ARRIVAL", "DRAVNIA", "VOSTOK BORDER", "03 JUN 2024",
         ST_GREEN, 6, (760, 140)),
        ("DEPARTURE", "DRAVNIA", "VOSTOK BORDER", "18 JUN 2024",
         ST_GREEN, -5, (548, 268)),
        ("ARRIVAL", "CALDORIA", "PORT MERIDIAN", "19 JUN 2024",
         PURPLE, 7, (760, 268)),
        ("DEPARTURE", "CALDORIA", "PORT MERIDIAN", "02 JUL 2024",
         PURPLE, -6, (548, 396)),
        ("ARRIVAL", "VELMORIA", "TARNWICK", "02 JUL 2024",
         BLUE, 4, (760, 396)),
    ]
    for kind, country, place, date, color, rot, (sx, sy) in stamps:
        layer = stamp_layer(196, 96, color, [
            (kind, 13, True),
            (country, 15, True),
            (place, 10, False),
            (date, 14, True),
        ], rot)
        base = img.convert("RGBA")
        stamp_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        stamp_img.paste(layer, (sx - 20, sy - 20))
        img = Image.alpha_composite(base, stamp_img).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")

    # telling detail: the visa-condition stamp
    cond = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cond)
    cx0, cy0, cx1, cy1 = 548, 540, 972, 690
    cd.rounded_rectangle([cx0, cy0, cx1, cy1], radius=8,
                         outline=RED + (230,), width=3)
    cd.rounded_rectangle([cx0 + 6, cy0 + 6, cx1 - 6, cy1 - 6], radius=5,
                         outline=RED + (150,), width=1)
    cd.text(((cx0 + cx1) // 2, cy0 + 14), "VISA CONDITION 7",
            font=font(SANS_B, 17), fill=RED + (235,), anchor="ma")
    draw_wrapped(cd, (cx0 + 18, cy0 + 44, cx1 - 18, cy1 - 30),
                 "NO CROSSING OF THE GREY PASS AFTER DUSK.",
                 font(SANS_B, 14), RED + (235,))
    cd.text(((cx0 + cx1) // 2, cy1 - 34),
            "— BORDER WARDEN, TARNWICK —",
            font=font(SANS, 12), fill=RED + (225,), anchor="ma")
    cond = cond.rotate(-3, resample=Image.BICUBIC, center=(760, 615))
    img = Image.alpha_composite(img.convert("RGBA"), cond).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # handwritten note from the road
    d.text((760, 730), "Seen at the Grey Pass — 02 JUL 2024",
           font=font(SERIF_I, 17), fill=(52, 62, 110), anchor="ma")
    d.text((760, 756), "M. Ilsen crossed on foot, before dusk.",
           font=font(SERIF_I, 14), fill=(52, 62, 110), anchor="ma")
    d.text((972, 968), "2", font=font(SANS, 10), fill=GREY, anchor="ra")

    return img


def main():
    img = build()
    out_dir = Path("/output")
    if not out_dir.is_dir():
        out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    img.save(out, format="PNG")
    print(f"wrote {out} {img.size} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
