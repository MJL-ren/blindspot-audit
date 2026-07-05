#!/usr/bin/env python3
"""Rename photos in a folder to their EXIF timestamp."""

import os
import sys
from datetime import datetime

from PIL import Image  # pillow


def exif_time(path):
    with Image.open(path) as img:
        raw = (img._getexif() or {}).get(36867)  # DateTimeOriginal
    if raw:
        return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    return None


def main(folder):
    for name in os.listdir(folder):
        if not name.lower().endswith((".jpg", ".jpeg")):
            continue
        src = os.path.join(folder, name)
        ts = exif_time(src)
        if ts is None:
            continue
        dst = os.path.join(folder, ts.strftime("%Y-%m-%d_%H%M%S") + ".jpg")
        os.rename(src, dst)
        print(f"{name} -> {os.path.basename(dst)}")


if __name__ == "__main__":
    main(sys.argv[1])
