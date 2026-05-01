#!/usr/bin/env python3
"""Render typographic hero image for multi-model-redteam README.

Design philosophy: Schematic Editorial — but distilled to a single
typographic statement. Big editorial display setting up a 2-second
read; one violet word as the focal accent. No diagram, no info
density — that lives in docs/methodology.md.

Output: assets/hero.png at 1760x1080 (≈1.63:1).
"""
import os
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# CONFIG
# =====================================================================

W, H = 1760, 1080

BG          = (251, 249, 244)
INK         = (24, 22, 20)
INK_SOFT    = (90, 86, 80)
INK_MUTE    = (132, 128, 122)
RULE        = (208, 202, 192)
DOT         = (212, 205, 192)

# Color stripe (4 territories from chapter 02 / methodology diagram)
ORANGE  = (200, 92, 56)
EMERALD = (62, 122, 84)
SKY     = (60, 96, 152)
VIOLET  = (108, 60, 172)

# =====================================================================
# FONTS
# =====================================================================

FONT_DIR = r'C:\Users\permoon\.claude\skills\canvas-design\canvas-fonts'
def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

f_punch         = F('BigShoulders-Bold.ttf', 168)
f_setup         = F('BigShoulders-Bold.ttf', 100)
f_italic_lg     = F('InstrumentSerif-Italic.ttf', 34)
f_italic_md     = F('InstrumentSerif-Italic.ttf', 26)
f_mono_micro    = F('GeistMono-Regular.ttf', 14)
f_mono_micro_b  = F('GeistMono-Bold.ttf', 14)
f_mono_small    = F('GeistMono-Regular.ttf', 18)

# =====================================================================
# CANVAS
# =====================================================================

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

# Subtle dot lattice
GRID = 32
for y in range(96, H - 96, GRID):
    for x in range(120, W - 120, GRID):
        d.point((x, y), fill=DOT)
        d.point((x + 1, y), fill=DOT)

# Helpers
def hairline(y, color=RULE, width=2):
    d.line((120, y, W - 120, y), fill=color, width=width)

def measure(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]

# =====================================================================
# TOP STRIP
# =====================================================================
hairline(96)
d.text((120, 116), '§  MULTI-MODEL DESIGN RED TEAM',
       font=f_mono_micro_b, fill=INK_SOFT)
d.text((W - 120, 116), 'EDITION 01 — 2026',
       font=f_mono_micro_b, fill=INK_SOFT, anchor='rt')

# =====================================================================
# TYPOGRAPHIC STATEMENT
# =====================================================================
text_x = 120

# Setup line — INK_SOFT, smaller weight, sets the problem
setup_y = 200
d.text((text_x, setup_y), 'ONE MODEL MISSES.',
       font=f_setup, fill=INK_SOFT)

# Punch line 1 — full INK, big
punch1_y = 360
d.text((text_x, punch1_y), 'THE OTHER TWO',
       font=f_punch, fill=INK)

# Punch line 2 — split: "OFTEN " in INK, "CATCH." in VIOLET
punch2_y = 540
seg_a = 'OFTEN '
seg_b = 'CATCH.'
w_a = measure(seg_a, f_punch)
d.text((text_x, punch2_y), seg_a, font=f_punch, fill=INK)
d.text((text_x + w_a, punch2_y), seg_b, font=f_punch, fill=VIOLET)

# =====================================================================
# SUPPORTING LINE
# =====================================================================
support_y = 760
support_text = 'a multi-LLM design red team — paste ~30 lines into your CLAUDE.md and you’re set.'
d.text((text_x, support_y), support_text,
       font=f_italic_lg, fill=INK_SOFT)

# =====================================================================
# AMBIENT VISUAL: 4 colored hairline segments
# (subtle nod to the 3 models + 1 unique-finding accent)
# =====================================================================
stripe_y = 880
seg_w = 80
seg_gap = 14
total_w = 4 * seg_w + 3 * seg_gap
stripe_x_start = W - 120 - total_w

for i, color in enumerate((ORANGE, EMERALD, SKY, VIOLET)):
    x1 = stripe_x_start + i * (seg_w + seg_gap)
    d.rectangle((x1, stripe_y, x1 + seg_w, stripe_y + 6), fill=color)

# Small caption above stripe
d.text((stripe_x_start, stripe_y - 28),
       'CLAUDE   ·   CODEX   ·   GEMINI   ·   UNIQUE',
       font=f_mono_micro_b, fill=INK_SOFT)

# =====================================================================
# FOOTER
# =====================================================================
hr_bot_y = 940
hairline(hr_bot_y)

d.text((120, hr_bot_y + 22),
       'no install · no plugin · no marketplace',
       font=f_italic_md, fill=INK)
d.text((W - 120, hr_bot_y + 30),
       'github.com/permoon/multi-model-redteam',
       font=f_mono_small, fill=INK_SOFT, anchor='rt')

# =====================================================================
# SAVE
# =====================================================================
out_path = r'D:\AI_Structure\multi-model-redteam\assets\hero.png'
img.save(out_path, optimize=True)
print(f'Saved: {out_path}')
print(f'Dimensions: {W}x{H}, size: {os.path.getsize(out_path)} bytes')
