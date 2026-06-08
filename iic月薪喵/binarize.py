"""
Threshold BMP images to pure black & white (binary, 0/255).
Output to ./binary/ subdirectory, originals untouched.
"""

import os
import sys

# Force UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SRC_DIR, "binary")
THRESHOLD = int(os.environ.get("THRESHOLD", 128))

os.makedirs(OUT_DIR, exist_ok=True)

bmp_files = sorted(
    f for f in os.listdir(SRC_DIR)
    if f.lower().endswith(".bmp")
)

if not bmp_files:
    print("No BMP files found.")
    exit(1)

print(f"Threshold: {THRESHOLD}")
print(f"Found {len(bmp_files)} BMP files")
print(f"Output: {OUT_DIR}\n")

for fname in bmp_files:
    path = os.path.join(SRC_DIR, fname)
    img = Image.open(path)

    # Grayscale -> binary threshold (pure black & white)
    gray = img.convert("L")
    bw = gray.point(lambda x: 255 if x >= THRESHOLD else 0, mode="1")

    out_path = os.path.join(OUT_DIR, fname)
    bw.save(out_path)
    print(f"OK {fname}")

print(f"\nDone! {len(bmp_files)} images -> {OUT_DIR}")
