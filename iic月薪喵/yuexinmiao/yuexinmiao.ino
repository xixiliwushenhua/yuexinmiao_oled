/*
 * ESP32 + SSD1306 OLED (I2C 0x3C) — 64x64 frame animation
 *
 * Wiring:
 *   ESP32       SSD1306
 *   GPIO21      SDA
 *   GPIO22      SCL
 *   3.3V        VCC
 *   GND         GND
 *
 * Zero external dependencies — only Wire.h (built-in).
 */

#include <Wire.h>
#include "frames.h"

#define OLED_ADDR     0x3C
#define X_OFFSET      ((128 - FRAME_WIDTH) / 2)   // 32, center on 128-wide
#define FRAME_DELAY_MS 60

// ============================================================
// Low-level I2C helpers
// ============================================================
static void oled_cmd(uint8_t cmd) {
  Wire.beginTransmission(OLED_ADDR);
  Wire.write(0x00);   // Co=0, D/C#=0 -> command
  Wire.write(cmd);
  Wire.endTransmission();
}

static void oled_cmd3(uint8_t a, uint8_t b, uint8_t c) {
  Wire.beginTransmission(OLED_ADDR);
  Wire.write(0x00);
  Wire.write(a);
  Wire.write(b);
  Wire.write(c);
  Wire.endTransmission();
}

static void oled_data(const uint8_t* data, size_t len) {
  Wire.beginTransmission(OLED_ADDR);
  Wire.write(0x40);   // Co=0, D/C#=1 -> data
  Wire.write(data, len);
  Wire.endTransmission();
}

// ============================================================
// SSD1306 init sequence
// ============================================================
static void oled_init() {
  delay(10);

  oled_cmd(0xAE); // display off

  oled_cmd(0xD5); oled_cmd(0x80); // osc clock
  oled_cmd(0xA8); oled_cmd(0x3F); // mux ratio = 64
  oled_cmd(0xD3); oled_cmd(0x00); // display offset = 0
  oled_cmd(0x40);                 // start line = 0
  oled_cmd(0x8D); oled_cmd(0x14); // charge pump on
  oled_cmd(0x20); oled_cmd(0x00); // memory addressing: horizontal
  oled_cmd(0xA1);                 // segment remap
  oled_cmd(0xC8);                 // COM scan direction
  oled_cmd(0xDA); oled_cmd(0x12); // COM pins
  oled_cmd(0x81); oled_cmd(0xCF); // contrast
  oled_cmd(0xD9); oled_cmd(0xF1); // precharge
  oled_cmd(0xDB); oled_cmd(0x40); // VCOMH deselect
  oled_cmd(0xA4);                 // resume to RAM content
  oled_cmd(0xA6);                 // normal (non-inverted)

  oled_cmd(0x2E); // stop scroll
  oled_cmd(0xAF); // display on
}

// ============================================================
void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);   // ESP32 I2C: SDA=21, SCL=22

  oled_init();
  Serial.println(F("SSD1306 ready."));
}

// ============================================================
void loop() {
  for (int i = 0; i < FRAME_COUNT; i++) {
    drawFrame(i);
    delay(FRAME_DELAY_MS);
  }
}

// ============================================================
// Write one frame to SSD1306 GDDRAM (page addressing mode).
// Layout: 8 pages x 64 cols = 512 bytes
// Each byte = 8 vertical pixels in one column, bit0 = top.
// ============================================================
void drawFrame(int idx) {
  uint8_t* ptr;
  memcpy_P(&ptr, &frames[idx], sizeof(ptr));

  uint8_t buf[FRAME_BYTES];
  memcpy_P(buf, ptr, FRAME_BYTES);

  for (int page = 0; page < 8; page++) {
    oled_cmd3(0xB0 | page,                     // set page
              0x00 | (X_OFFSET & 0x0F),        // lower column
              0x10 | ((X_OFFSET >> 4) & 0x0F)); // higher column

    oled_data(&buf[page * FRAME_WIDTH], FRAME_WIDTH);
  }
}
