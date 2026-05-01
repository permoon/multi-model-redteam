#!/usr/bin/env python3
"""Render hero architecture diagram for multi-model-redteam README.

Design philosophy: Schematic Editorial — information graphic as
editorial typographic composition. Restrained palette, hairline
weights, asymmetric tension in header, symmetric flow in body.

Output: assets/architecture.png at 1760x1320 (≈1.33:1).
"""
import os
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# CONFIG
# =====================================================================

W, H = 1760, 1360

# Warm paper-stock palette
BG          = (251, 249, 244)
INK         = (24, 22, 20)
INK_SOFT    = (74, 70, 64)
INK_MUTE    = (120, 116, 110)
RULE        = (208, 202, 192)
DOT         = (212, 205, 192)

# Per-model territories (low-saturation editorial palette)
CLAUDE = dict(fill=(254, 240, 230), border=(172, 80, 48),
              ink=(110, 42, 16),    accent=(200, 92, 56))
CODEX  = dict(fill=(231, 240, 233), border=(44, 92, 60),
              ink=(24, 60, 38),     accent=(62, 122, 84))
GEMINI = dict(fill=(227, 234, 245), border=(40, 70, 116),
              ink=(20, 46, 84),     accent=(60, 96, 152))

VIOLET = dict(fill=(236, 228, 247), border=(88, 50, 144),
              ink=(54, 28, 96),     solid=(108, 60, 172))

# =====================================================================
# FONTS
# =====================================================================

FONT_DIR = r'C:\Users\permoon\.claude\skills\canvas-design\canvas-fonts'
def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

f_display       = F('BigShoulders-Bold.ttf', 116)
f_section_lbl   = F('InstrumentSans-Bold.ttf', 18)
f_section_num   = F('GeistMono-Bold.ttf', 22)
f_label         = F('InstrumentSans-Bold.ttf', 28)
f_body          = F('InstrumentSans-Regular.ttf', 21)
f_italic_lg     = F('InstrumentSerif-Italic.ttf', 30)
f_italic_sm     = F('InstrumentSerif-Italic.ttf', 22)
f_mono_micro    = F('GeistMono-Regular.ttf', 14)
f_mono_micro_b  = F('GeistMono-Bold.ttf', 14)
f_mono_small    = F('GeistMono-Regular.ttf', 18)
f_mono_med      = F('GeistMono-Regular.ttf', 22)

# =====================================================================
# CANVAS
# =====================================================================

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

# ---------- Subtle dot lattice (visual paper grain) ----------
GRID = 28
for y in range(96, H - 96, GRID):
    for x in range(120, W - 120, GRID):
        d.point((x, y), fill=DOT)
        d.point((x + 1, y), fill=DOT)  # 2-px dot for visibility

# Helpers ----------------------------------------------------------
def hairline(y, color=RULE, width=2):
    d.line((120, y, W - 120, y), fill=color, width=width)

def box(xy, fill, border, radius=12, width=2):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=border, width=width)

def arrow_down(x, y, color, size=9):
    d.polygon([(x - size, y), (x + size, y), (x, y + size + 2)], fill=color)

def arrow_right(x, y, color, size=8):
    d.polygon([(x, y - size), (x, y + size), (x + size + 2, y)], fill=color)

def accent_swatch(x, y, color, w=14, h=14):
    """Small rectangular color accent — replaces glyph diamond."""
    d.rectangle((x, y, x + w, y + h), fill=color)

# =====================================================================
# HEADER STRIP (top)
# =====================================================================
hairline(96)
d.text((120, 116), '§  A METHOD', font=f_mono_micro_b, fill=INK_SOFT)
d.text((W - 120, 116), 'EDITION 01 — 2026', font=f_mono_micro_b, fill=INK_SOFT, anchor='rt')

# Display title — left-aligned, two-line stack
title_x = 120
title_y = 150
d.text((title_x, title_y), 'MULTI – MODEL', font=f_display, fill=INK)
d.text((title_x, title_y + 95), 'DESIGN RED TEAM', font=f_display, fill=INK)

# Editorial italic subtitle
sub_y = title_y + 215
d.text((title_x, sub_y), 'three LLMs review the same plan in parallel —',
       font=f_italic_lg, fill=INK_SOFT)
d.text((title_x, sub_y + 36),
       'whatever one misses, the other two often catch.',
       font=f_italic_lg, fill=INK_SOFT)

# Right-side metadata column (asymmetric balance)
meta_x = W - 120
meta_y = title_y + 4
d.text((meta_x, meta_y),       'METHOD',     font=f_mono_micro_b, fill=INK_SOFT, anchor='rt')
d.text((meta_x, meta_y + 22),  '5-failure-dimension frame', font=f_mono_small, fill=INK, anchor='rt')

d.text((meta_x, meta_y + 70),  'OUTPUT',     font=f_mono_micro_b, fill=INK_SOFT, anchor='rt')
d.text((meta_x, meta_y + 92),  'severity-ranked findings', font=f_mono_small, fill=INK, anchor='rt')

d.text((meta_x, meta_y + 140), 'INSTALL',    font=f_mono_micro_b, fill=INK_SOFT, anchor='rt')
d.text((meta_x, meta_y + 162), 'paste ~30 lines into your CLAUDE.md', font=f_mono_small, fill=INK, anchor='rt')

# Hairline rule under header
hr1_y = sub_y + 90
hairline(hr1_y)

# =====================================================================
# DIAGRAM
# =====================================================================

# ----- Section 01 — INPUT -----
sec_y = hr1_y + 36
d.text((title_x, sec_y), '01', font=f_section_num, fill=INK)
d.text((title_x + 44, sec_y + 4), 'INPUT', font=f_section_lbl, fill=INK)

plan_w, plan_h = 320, 68
plan_cx = W // 2
plan_x1 = plan_cx - plan_w // 2
plan_y1 = sec_y + 28
box((plan_x1, plan_y1, plan_x1 + plan_w, plan_y1 + plan_h),
    fill=BG, border=INK, radius=10, width=2)
d.text((plan_cx, plan_y1 + 20), 'plan.md / spec / RFC',
       font=f_mono_med, fill=INK, anchor='mm')
d.text((plan_cx, plan_y1 + 48), 'your design under review',
       font=f_italic_sm, fill=INK_SOFT, anchor='mm')

# Card geometry
card_w, card_h = 380, 192
card_gap = 80
card_total = 3 * card_w + 2 * card_gap
cards_y1 = sec_y + 168
cards_x_start = (W - card_total) // 2
claude_cx = cards_x_start + card_w // 2
codex_cx  = cards_x_start + card_w + card_gap + card_w // 2
gemini_cx = cards_x_start + 2 * (card_w + card_gap) + card_w // 2

# Fan-out lines
fan_top_y = plan_y1 + plan_h
fan_bottom_y = cards_y1
for tx in (claude_cx, codex_cx, gemini_cx):
    d.line((plan_cx, fan_top_y, tx, fan_bottom_y), fill=INK_MUTE, width=2)
    arrow_down(tx, fan_bottom_y - 4, INK_MUTE, size=8)

# Marginalia between fan-out
margin_y = (fan_top_y + fan_bottom_y) // 2 - 12
d.text((plan_cx, margin_y),
       'same prompt · in parallel · no cross-talk',
       font=f_italic_sm, fill=INK_MUTE, anchor='mm')

# ----- Section 02 — PARALLEL REVIEW -----
sec2_y = cards_y1 - 26
d.text((title_x, sec2_y), '02', font=f_section_num, fill=INK)
d.text((title_x + 44, sec2_y + 4), 'PARALLEL REVIEW', font=f_section_lbl, fill=INK)

def model_card(x1, y1, palette, name, finds_lines):
    x2, y2 = x1 + card_w, y1 + card_h
    box((x1, y1, x2, y2), fill=palette['fill'],
        border=palette['border'], radius=14, width=2)

    # Vertical bar accent — manuscript marginalia feel
    accent_swatch(x1 + 22, y1 + 18, palette['accent'], w=4, h=22)

    # Name (bold sans)
    d.text((x1 + 38, y1 + 14), name, font=f_label, fill=palette['ink'])

    # Sub-label
    d.text((x1 + 22, y1 + 64), '5-FRAME REVIEW',
           font=f_mono_micro_b, fill=palette['accent'])

    # Inner rule under header
    d.line((x1 + 22, y1 + 88, x2 - 22, y1 + 88), fill=palette['border'], width=1)

    # Finds list
    line_y = y1 + 104
    for line in finds_lines:
        d.text((x1 + 22, line_y), line, font=f_body, fill=palette['ink'])
        line_y += 28

model_card(cards_x_start, cards_y1, CLAUDE, 'CLAUDE CODE',
           ['ordering, atomicity', 'rollback gaps', 'alert thresholds'])
model_card(cards_x_start + card_w + card_gap, cards_y1, CODEX, 'CODEX CLI',
           ['idempotency', 'schema drift', 'transport failures'])
model_card(cards_x_start + 2 * (card_w + card_gap), cards_y1, GEMINI, 'GEMINI CLI',
           ['timezone, partition', 'cross-region races', 'GCP-native traps'])

# ----- Converge lines into consolidate bar -----
cards_y2 = cards_y1 + card_h
conv_top_y = cards_y2 + 6
consol_cx = W // 2
conv_bottom_y = cards_y2 + 78
for sx in (claude_cx, codex_cx, gemini_cx):
    d.line((sx, conv_top_y, consol_cx, conv_bottom_y), fill=INK_MUTE, width=2)
arrow_down(consol_cx, conv_bottom_y - 4, INK_MUTE, size=8)

# ----- Section 03 — CONSOLIDATE -----
sec3_y = cards_y2 + 44
d.text((title_x, sec3_y), '03', font=f_section_num, fill=INK)
d.text((title_x + 44, sec3_y + 4), 'CONSOLIDATE', font=f_section_lbl, fill=INK)

cons_w, cons_h = 540, 64
cons_x1 = consol_cx - cons_w // 2
cons_y1 = sec3_y + 30
box((cons_x1, cons_y1, cons_x1 + cons_w, cons_y1 + cons_h),
    fill=INK, border=INK, radius=10, width=2)
d.text((consol_cx, cons_y1 + 18), '4th LLM call', font=f_label, fill=BG, anchor='mm')
d.text((consol_cx, cons_y1 + 46), 'merges findings by meaning, not by string match',
       font=f_italic_sm, fill=(195, 190, 180), anchor='mm')

# Arrow to findings
out_arrow_top = cons_y1 + cons_h
out_arrow_bot = out_arrow_top + 38
d.line((consol_cx, out_arrow_top + 4, consol_cx, out_arrow_bot - 4), fill=INK_MUTE, width=2)
arrow_down(consol_cx, out_arrow_bot - 4, INK_MUTE, size=8)

# ----- Section 04 — RANKED FINDINGS -----
sec4_y = out_arrow_bot + 18
d.text((title_x, sec4_y), '04', font=f_section_num, fill=INK)
d.text((title_x + 44, sec4_y + 4), 'RANKED FINDINGS', font=f_section_lbl, fill=INK)

panel_w = 1120
panel_h = 184
panel_x1 = W // 2 - panel_w // 2
panel_y1 = sec4_y + 28
panel_x2 = panel_x1 + panel_w
panel_y2 = panel_y1 + panel_h
box((panel_x1, panel_y1, panel_x2, panel_y2), fill=BG, border=INK, radius=12, width=2)

# Header micro-row inside panel
d.text((panel_x1 + 28, panel_y1 + 14), 'CATEGORY',
       font=f_mono_micro_b, fill=INK_MUTE)
d.text((panel_x1 + 300, panel_y1 + 14), 'CRITERION',
       font=f_mono_micro_b, fill=INK_MUTE)
d.text((panel_x1 + 680, panel_y1 + 14), 'INTERPRETATION',
       font=f_mono_micro_b, fill=INK_MUTE)
d.line((panel_x1 + 28, panel_y1 + 38, panel_x2 - 28, panel_y1 + 38),
       fill=RULE, width=1)

# Row 1 — Consensus
row1_y = panel_y1 + 50
d.ellipse((panel_x1 + 32, row1_y + 8, panel_x1 + 48, row1_y + 24), fill=INK_SOFT)
d.text((panel_x1 + 60, row1_y + 5), 'Consensus', font=f_label, fill=INK)
d.text((panel_x1 + 300, row1_y + 9), '2+ teams agreed',
       font=f_body, fill=INK_SOFT)
d.text((panel_x1 + 680, row1_y + 9),
       'strongest signal — almost certainly real',
       font=f_body, fill=INK_SOFT)

# Row 2 — Unique [HIGHLIGHT]
row2_y = row1_y + 44
hi_x1, hi_y1, hi_x2, hi_y2 = panel_x1 + 16, row2_y - 6, panel_x2 - 16, row2_y + 38
box((hi_x1, hi_y1, hi_x2, hi_y2),
    fill=VIOLET['fill'], border=VIOLET['border'], radius=8, width=2)
d.ellipse((panel_x1 + 32, row2_y + 8, panel_x1 + 48, row2_y + 24),
          fill=VIOLET['solid'])
d.text((panel_x1 + 60, row2_y + 5), 'Unique', font=f_label, fill=VIOLET['ink'])
d.text((panel_x1 + 300, row2_y + 9), '1 team only — others missed it',
       font=f_body, fill=VIOLET['ink'])
d.text((panel_x1 + 680, row2_y + 9),
       'where single-model review would have failed',
       font=f_body, fill=VIOLET['ink'])

# Row 3 — Blind spot
row3_y = row2_y + 50
d.ellipse((panel_x1 + 32, row3_y + 8, panel_x1 + 48, row3_y + 24),
          outline=INK_SOFT, width=2)
d.text((panel_x1 + 60, row3_y + 5), 'Blind spot', font=f_label, fill=INK)
d.text((panel_x1 + 300, row3_y + 9), 'all 3 missed it',
       font=f_body, fill=INK_SOFT)
d.text((panel_x1 + 680, row3_y + 9),
       'flagged by consolidator, conservatively',
       font=f_body, fill=INK_SOFT)

# Pointer to "Unique" with annotation
ptr_x1 = panel_x2 + 16
ptr_y  = row2_y + 16
ptr_x2 = ptr_x1 + 64
d.line((ptr_x1, ptr_y, ptr_x2 - 6, ptr_y), fill=VIOLET['solid'], width=2)
arrow_right(ptr_x2 - 6, ptr_y, VIOLET['solid'], size=6)
d.text((ptr_x2 + 4, ptr_y - 22), 'value',     font=f_mono_micro_b, fill=VIOLET['solid'])
d.text((ptr_x2 + 4, ptr_y - 4),  'compounds', font=f_mono_micro_b, fill=VIOLET['solid'])
d.text((ptr_x2 + 4, ptr_y + 14), 'here',      font=f_mono_micro_b, fill=VIOLET['solid'])

# =====================================================================
# FOOTER
# =====================================================================
hr2_y = panel_y2 + 44
hairline(hr2_y)

# Bottom byline (italic display, left)
d.text((120, hr2_y + 22),
       'no install · no plugin · no marketplace',
       font=f_italic_lg, fill=INK)

# Right-side mono note
d.text((W - 120, hr2_y + 30),
       'paste ~30 lines into your CLAUDE.md → done',
       font=f_mono_small, fill=INK_SOFT, anchor='rt')

# =====================================================================
# SAVE
# =====================================================================
out_path = r'D:\AI_Structure\multi-model-redteam\assets\architecture.png'
img.save(out_path, optimize=True)
print(f'Saved: {out_path}')
print(f'Dimensions: {W}x{H}, size: {os.path.getsize(out_path)} bytes')
