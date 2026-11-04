#!/usr/bin/env python3
"""Cut a character drawn on plain white out of its background.

The background is the light, unsaturated area connected to the image border (white plus the
soft lavender ground shadow). White areas enclosed by the ink outline (eyes, shoes, mittens)
are not connected to the border, so they stay. Edge pixels between the background and the
ink outline get an alpha from their darkness, so the outline keeps its antialiasing.

    python3 art/cast/cutout.py art/cast/raw/learn.webp art/cast/out/learn.png
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

INK = np.array([20, 20, 30], dtype=np.float32)


def cutout(src, dst, light=188, sat=48):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    lum = a.mean(axis=2)
    spread = a.max(axis=2) - a.min(axis=2)
    cand = ((lum > light) & (spread < sat)).astype(np.uint8) * 255
    mask = Image.fromarray(cand, "L").copy()  # fromarray can share a read-only buffer
    w, h = mask.size
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    border += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for p in border:
        if mask.getpixel(p) == 255:
            ImageDraw.floodfill(mask, p, 128)
    bg = np.asarray(mask) == 128

    alpha = np.where(bg, 0, 255).astype(np.float32)
    # Feather a 2 px band of foreground next to the background by darkness.
    near = np.asarray(Image.fromarray((bg * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    band = near & ~bg
    k = np.clip((255 - lum) / (255 - 40), 0, 1)
    alpha[band] = np.minimum(alpha[band], k[band] * 255)
    rgb = a.astype(np.float32)
    # Un-mix white from the band so a dark ground shows no halo.
    kk = np.clip(k[band], 0.05, 1)[:, None]
    rgb[band] = np.clip((rgb[band] - (1 - kk) * 255) / kk, 0, 255)
    out = np.dstack([rgb, alpha]).astype(np.uint8)
    res = Image.fromarray(out, "RGBA")
    res = res.crop(res.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    res.save(dst)
    return res.size


if __name__ == "__main__":
    print(cutout(sys.argv[1], sys.argv[2]))
