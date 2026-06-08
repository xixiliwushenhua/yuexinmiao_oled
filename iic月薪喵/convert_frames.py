"""
Convert binary BMP frames to SSD1306-compatible C byte arrays.
SSD1306 stores data in vertical-byte, column-major format:
  Each byte = 8 vertical pixels in one column.
  For 64x64: 8 pages × 64 columns = 512 bytes/frame.

Output: frames.h with all frame data as PROGMEM arrays.
"""

import os
import sys
import struct
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

SRC_DIR = r"C:\Users\13905\Desktop\月薪喵\binary"
OUT_H = os.path.join(SRC_DIR, "..", "frames.h")

bmp_files = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".bmp"))

if not bmp_files:
    print("No BMP files found in binary/")
    exit(1)

all_frame_data = []  # list of (name, bytearray)

for fname in bmp_files:
    path = os.path.join(SRC_DIR, fname)
    img = Image.open(path)

    w, h = img.size
    assert w == 64 and h == 64, f"Expected 64x64, got {w}x{h} for {fname}"

    # Get raw pixel data: 0=black, 1=white (mode "1")
    # BMP mode "1": 0=black, 255=white (PIL normalizes to 0/255 in getdata)
    # In BMP raw, 1=white, 0=black. We'll use 1=white=LED ON for SSD1306.
    pixels = list(img.getdata())  # list of 0 or 255

    # Convert to SSD1306 vertical-byte format
    # 8 pages (64/8), 64 columns
    n_pages = h // 8
    frame_bytes = bytearray(n_pages * w)  # 8 * 64 = 512 bytes

    for col in range(w):
        for page in range(n_pages):
            byte_val = 0
            for bit in range(8):
                y = page * 8 + bit
                pixel_idx = y * w + col
                # pixel value: 255 = white = LED ON = bit 1
                #              0   = black = LED OFF = bit 0
                if pixels[pixel_idx] == 255:
                    byte_val |= (1 << bit)
            frame_bytes[page * w + col] = byte_val

    all_frame_data.append((fname, frame_bytes))
    print(f"Converted {fname}: {len(frame_bytes)} bytes")

# Write C header
var_names = []
with open(OUT_H, "w", encoding="utf-8") as f:
    f.write("// Auto-generated frame data for SSD1306 64x64\n")
    f.write(f"// {len(all_frame_data)} frames, {len(all_frame_data[0][1])} bytes each\n")
    f.write("#pragma once\n")
    f.write("#include <pgmspace.h>\n\n")
    f.write(f"#define FRAME_COUNT {len(all_frame_data)}\n")
    f.write(f"#define FRAME_WIDTH 64\n")
    f.write(f"#define FRAME_HEIGHT 64\n")
    f.write(f"#define FRAME_BYTES {len(all_frame_data[0][1])}\n\n")

    for i, (fname, data) in enumerate(all_frame_data):
        var_name = f"frame_{i:02d}"
        var_names.append(var_name)
        f.write(f"// {fname}\n")
        f.write(f"static const uint8_t {var_name}[{len(data)}] PROGMEM = {{\n  ")
        hex_bytes = [f"0x{b:02X}" for b in data]
        # 16 bytes per line
        lines = [", ".join(hex_bytes[j:j+16]) for j in range(0, len(hex_bytes), 16)]
        f.write(",\n  ".join(lines))
        f.write("\n};\n\n")

    # Frame array pointing to all frames
    f.write(f"// Array of pointers to all frames\n")
    f.write(f"static const uint8_t* const frames[FRAME_COUNT] PROGMEM = {{\n  ")
    f.write(",\n  ".join(var_names))
    f.write("\n};\n")

print(f"\nDone! Written to: {OUT_H}")
print(f"Total: {len(all_frame_data)} frames, {len(all_frame_data[0][1])} bytes each")
