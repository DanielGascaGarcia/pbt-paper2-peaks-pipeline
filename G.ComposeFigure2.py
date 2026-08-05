#Code: G.ComposeFigure2.py
#Description: Compose panels A and B into a single Figure 2.
#             Reads the two PNGs already written to path3 by
#             4.PeaksDetection.py, trims the white border matplotlib
#             leaves around the axes, scales them to a common width and
#             stacks them vertically with the panel letter to the left.
#Author: mbaxdg6

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import globals

path3 = globals.path3;

PANELS = ['Figure2a.png', 'Figure2b.png'];
LABELS = ['A', 'B'];
GAP = 40;          # px between panels
MARGIN = 30;       # px around the composite
LABEL_SIZE = 90;   # px, panel letter height
LABEL_GAP = 30;    # px between the letter column and the panels


def crop_white(img, tol=250):
    """Trim the uniform white border around the plotted area."""
    a = np.asarray(img.convert('RGB'));
    mask = (a < tol).any(axis=2);
    rows = np.where(mask.any(axis=1))[0];
    cols = np.where(mask.any(axis=0))[0];
    if len(rows) == 0 or len(cols) == 0:
        return img;
    return img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1));


missing = [p for p in PANELS if not os.path.isfile(os.path.join(path3, p))];
if missing:
    for p in missing:
        print("MISSING:", os.path.join(path3, p));
    print("\nBoth panels must exist before composing. They are written by");
    print("4.PeaksDetection.py when the participant is globals.idG and the");
    print("day index is globals.FIG2_DAY (currently " + str(globals.FIG2_DAY) + ").");
    if globals.DEMO:
        print("In demo mode only globals.DEMO_DAYS days are generated, so");
        print("FIG2_DAY must be lower than that.");
    sys.exit(1);

imgs = [crop_white(Image.open(os.path.join(path3, p))) for p in PANELS];

# Scale every panel to a common width so the two stacked plots match.
w = min(im.width for im in imgs);
imgs = [im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        for im in imgs];

total_w = MARGIN + LABEL_SIZE + LABEL_GAP + w + MARGIN;
total_h = (sum(im.height for im in imgs)
           + GAP * (len(imgs) - 1) + 2 * MARGIN);

canvas = Image.new('RGB', (total_w, total_h), 'white');
draw = ImageDraw.Draw(canvas);
# matplotlib ships the DejaVu fonts, so resolve the file through it
# rather than relying on the name being on the system font path.
# load_default() returns a bitmap font, and textbbox rejects those.
from matplotlib import font_manager
font = ImageFont.truetype(font_manager.findfont('DejaVu Sans:bold'), LABEL_SIZE);

x = MARGIN + LABEL_SIZE + LABEL_GAP;
y = MARGIN;
for im, label in zip(imgs, LABELS):
    canvas.paste(im, (x, y));
    # Centre the letter vertically against its own panel.
    bbox = draw.textbbox((0, 0), label, font=font);
    th = bbox[3] - bbox[1];
    draw.text((MARGIN, y + (im.height - th) // 2 - bbox[1]),
              label, fill='black', font=font);
    y += im.height + GAP;

out = os.path.join(path3, 'Figure2.png');
canvas.save(out, dpi=(300, 300));
print("Saved:", os.path.abspath(out));
print("Composite size:", canvas.size);
