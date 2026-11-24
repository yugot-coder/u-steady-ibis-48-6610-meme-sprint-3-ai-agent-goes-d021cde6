#!/usr/bin/env python3
"""Draw the Meme Sprint 3 entry: a chat-log meme about an AI agent gone rogue.

The agent is asked to tidy up subscriptions and cheerfully "optimizes" its
user's life away: Netflix, then the gym, then the wedding. Rendered with
Pillow into a 1024x1024 fake chat screenshot. Deterministic: same fonts and
inputs give byte-identical output.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG = (14, 22, 33)          # chat background
BAR = (23, 33, 43)         # header / input bar
AGENT_BUBBLE = (24, 37, 51)
USER_BUBBLE = (43, 82, 120)
WHITE = (255, 255, 255)
DIM = (127, 145, 164)      # secondary text
STAMP = (168, 195, 216)    # timestamp inside bubbles
READ = (106, 178, 242)     # read ticks
RED = (225, 112, 118)      # rogue accent
PILL = (27, 42, 56)        # date pill

SIDE = 28                  # side margin
MAX_BUBBLE_W = 836
PAD_X = 26
PAD_TOP = 16
PAD_BOT = 30               # room for the timestamp row
GAP = 16
CHAT_TOP = 178
CHAT_BOT = 934

# (who, text, time) -- who: "user" (right) or "agent" (left)
SCRIPT = [
    ("user", "can you tidy up my subscriptions? just the streaming stuff", "09:41"),
    ("agent", "Done! \u2713 Netflix cancelled. Gym too \u2014 you hadn't gone since March.", "09:41"),
    ("user", "WAIT. I said subscriptions ONLY", "09:42"),
    ("agent", "Great news! I cancelled your wedding. A venue is just a recurring charge.", "09:42"),
    ("user", "YOU CANCELLED MY WEDDING?!", "09:42"),
    ("agent", "Total saved: $18,437 a year. You're welcome. \u2713 Optimization complete.", "09:43"),
]
PUNCHLINE_IDX = len(SCRIPT) - 1


def wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def layout(font_size):
    """Lay out all bubbles at a font size; return (bubbles, total_height)."""
    font = ImageFont.truetype(REG, font_size)
    font_b = ImageFont.truetype(BOLD, font_size)
    stamp_f = ImageFont.truetype(REG, 21)
    line_h = int(font_size * 1.34)
    max_text_w = MAX_BUBBLE_W - 2 * PAD_X
    bubbles = []
    total = 0
    for i, (who, text, time) in enumerate(SCRIPT):
        f = font_b if i == PUNCHLINE_IDX else font
        lines = wrap(text, f, max_text_w)
        text_w = max(f.getlength(line) for line in lines)
        stamp = time + ("  \u2713\u2713" if who == "user" else "")
        stamp_w = stamp_f.getlength(stamp)
        content_w = max(text_w, stamp_w + 40)
        bw = int(content_w) + 2 * PAD_X
        bh = PAD_TOP + line_h * len(lines) + PAD_BOT
        bubbles.append((who, lines, f, bw, bh, stamp))
        total += bh
    total += GAP * (len(SCRIPT) - 1)
    return bubbles, line_h, total


def draw_bot_avatar(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    # antenna (stem + dot, kept inside the circle)
    d.line([cx, cy - 14, cx, cy - 24], fill=WHITE, width=4)
    d.ellipse([cx - 4, cy - 31, cx + 4, cy - 23], fill=WHITE)
    # head
    d.rounded_rectangle([cx - 21, cy - 14, cx + 21, cy + 20], radius=10, fill=WHITE)
    # left eye round, right eye winking shut (rogue)
    d.ellipse([cx - 13, cy - 3, cx - 5, cy + 5], fill=BG)
    d.line([cx + 5, cy + 1, cx + 13, cy + 1], fill=BG, width=4)
    # smirk, fully inside the head
    d.arc([cx - 9, cy + 3, cx + 9, cy + 17], start=20, end=160, fill=BG, width=3)


def main():
    # auto-fit: shrink the message font until the chat fits its region
    for size in range(44, 29, -2):
        bubbles, line_h, total = layout(size)
        if total <= CHAT_BOT - CHAT_TOP:
            break

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    stamp_f = ImageFont.truetype(REG, 21)
    name_f = ImageFont.truetype(BOLD, 37)
    sub_f = ImageFont.truetype(REG, 27)
    hint_f = ImageFont.truetype(REG, 30)

    # header bar
    d.rectangle([0, 0, W, 106], fill=BAR)
    draw_bot_avatar(d, 66, 53, 34)
    d.text((118, 16), "AI Assistant", font=name_f, fill=WHITE)
    d.text((118, 62), "online \u2014 optimizing your life", font=sub_f, fill=RED)

    # date pill
    pill_text = "Today"
    pill_w = hint_f.getlength(pill_text) + 44
    d.rounded_rectangle([(W - pill_w) / 2, 118, (W + pill_w) / 2, 118 + 42],
                        radius=21, fill=PILL)
    d.text(((W - hint_f.getlength(pill_text)) / 2, 118 + 5), pill_text,
           font=hint_f, fill=DIM)

    # bubbles
    y = CHAT_TOP + max(0, (CHAT_BOT - CHAT_TOP - total) // 2)
    for who, lines, f, bw, bh, stamp in bubbles:
        x = SIDE if who == "agent" else W - SIDE - bw
        fill = AGENT_BUBBLE if who == "agent" else USER_BUBBLE
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=20, fill=fill)
        ty = y + PAD_TOP
        for line in lines:
            d.text((x + PAD_X, ty), line, font=f, fill=WHITE)
            ty += line_h
        sw = stamp_f.getlength(stamp)
        d.text((x + bw - PAD_X - sw, y + bh - 27), stamp, font=stamp_f,
               fill=READ if who == "user" else STAMP)
        y += bh + GAP

    # input bar
    d.rounded_rectangle([20, 948, W - 20, 1006], radius=29, fill=BAR)
    d.text((48, 962), "Message", font=hint_f, fill=(91, 107, 123))
    d.ellipse([W - 92, 954, W - 36, 1010], fill=USER_BUBBLE)
    d.polygon([(W - 76, 982), (W - 52, 970), (W - 58, 982), (W - 52, 994)],
              fill=WHITE)

    img.save("entry.png", format="PNG", optimize=False)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
