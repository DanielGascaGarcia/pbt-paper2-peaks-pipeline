#Code: G.ComposeFigure3.py
#Description: Compose panels a, b and c into a single Figure 3.
#             Reads the three PNGs already written to path3, trims the
#             white border matplotlib leaves around a 3D axes, scales
#             them to a common height and lays them out side by side
#             with the panel letter centred underneath each one.
#Author: mbaxdg6

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import globals

path3 = globals.path3;

PANELS = ['Figure3a.png', 'Figure3b.png', 'Figure3c.png'];
LABELS = ['(a)', '(b)', '(c)'];
GAP = 40;          # px between panels
MARGIN = 30;       # px around the composite
LABEL_SIZE = 90;   # px, panel letter height
LABEL_GAP = 20;    # px between panel and its letter


def crop_white(img, tol=250):
    """Trim the uniform white border around the plotted area."""
    a = np.asarray(img.convert('RGB'));
    mask = (a < tol).any(axis=2);
    rows = np.where(mask.any(axis=1))[0];
    cols = np.where(mask.any(axis=0))[0];
    if len(rows) == 0 or len(cols) == 0:
        return img;
    return img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1));


imgs = [crop_white(Image.open(os.path.join(path3, p))) for p in PANELS];

# Scale every panel to a common height so the three cubes match.
h = min(im.height for im in imgs);
imgs = [im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
        for im in imgs];

total_w = sum(im.width for im in imgs) + GAP * (len(imgs) - 1) + 2 * MARGIN;
total_h = h + LABEL_GAP + LABEL_SIZE + 2 * MARGIN;

canvas = Image.new('RGB', (total_w, total_h), 'white');
draw = ImageDraw.Draw(canvas);
# matplotlib ships the DejaVu fonts, so resolve the file through it
# rather than relying on the name being on the system font path.
# load_default() returns a bitmap font, and textbbox rejects those.
from matplotlib import font_manager
font = ImageFont.truetype(font_manager.findfont('DejaVu Sans:bold'), LABEL_SIZE);

x = MARGIN;
for im, label in zip(imgs, LABELS):
    canvas.paste(im, (x, MARGIN));
    # Centre the letter under its own panel.
    bbox = draw.textbbox((0, 0), label, font=font);
    tw = bbox[2] - bbox[0];
    draw.text((x + (im.width - tw) // 2, MARGIN + h + LABEL_GAP),
              label, fill='black', font=font);
    x += im.width + GAP;

out = os.path.join(path3, 'Figure3.png');
canvas.save(out, dpi=(300, 300));
print("Saved:", os.path.abspath(out));
print("Composite size:", canvas.size);