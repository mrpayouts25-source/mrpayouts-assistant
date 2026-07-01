from PIL import Image, ImageDraw, ImageFont
import os


def load_font(size, bold=False):
    possible_fonts = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]

    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            pass

    return ImageFont.load_default()


def draw_wrapped_text(draw, text, position, font, fill, max_width, line_spacing=10, max_lines=5):
    x, y = position
    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)

        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines[:max_lines]:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing


def base_canvas(subtitle):
    width = 1080
    height = 1350

    bg = "#080B12"
    card = "#121826"
    gold = "#D4AF37"
    muted = "#94A3B8"

    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    title_font = load_font(74, bold=True)
    subtitle_font = load_font(34)

    draw.rounded_rectangle((50, 50, width - 50, height - 50), radius=45, fill=card)

    draw.text((90, 90), "MRPAYOUTS", font=title_font, fill=gold)
    draw.text((95, 175), subtitle, font=subtitle_font, fill=muted)

    return image, draw


def generate_trade_image(trade):
    width = 1080
    height = 1350

    inner = "#0B0F19"
    white = "#F8FAFC"
    muted = "#94A3B8"
    green = "#22C55E"
    red = "#EF4444"

    image, draw = base_canvas("Signals • Personal Trading Journal")

    value_font = load_font(48, bold=True)
    label_font = load_font(30, bold=True)
    small_font = load_font(30)
    subtitle_font = load_font(34)
    badge_font = load_font(58, bold=True)

    direction = trade["direction"].upper()
    direction_colour = green if direction == "BUY" else red

    draw.text((90, 270), f"TRADE {trade['trade_number']}", font=value_font, fill=white)

    draw.rounded_rectangle((90, 350, 990, 520), radius=35, fill=inner)
    draw.text((130, 385), direction, font=badge_font, fill=direction_colour)
    draw.text((130, 455), trade["symbol"], font=subtitle_font, fill=white)

    y = 610

    items = [
        ("ENTRY", trade["entry"]),
        ("STOP LOSS", trade["sl"]),
        ("TAKE PROFIT", trade["tp"]),
        ("RISK", "1%"),
        ("RR", f"1:{trade['rr']}")
    ]

    for label, value in items:
        draw.text((100, y), label, font=label_font, fill=muted)
        draw.text((100, y + 40), str(value), font=value_font, fill=white)
        y += 125

    reason_y = 1110
    draw.rounded_rectangle((90, reason_y, 990, 1245), radius=30, fill=inner)
    draw.text((120, reason_y + 25), "STRATEGY", font=label_font, fill=muted)

    draw_wrapped_text(
        draw,
        "HTF Bias • LTF Confirmation",
        (120, reason_y + 70),
        small_font,
        white,
        800
    )

    draw.text(
        (90, 1275),
        "Not financial advice. Trade at your own risk.",
        font=small_font,
        fill=muted
    )

    os.makedirs("data/exports", exist_ok=True)

    path = f"data/exports/{trade['trade_number'].replace('#', '')}_{trade['symbol']}_{direction}.png"
    image.save(path)

    return path


def generate_result_image(trade, result, profit):
    width = 1080
    height = 1350

    inner = "#0B0F19"
    white = "#F8FAFC"
    muted = "#94A3B8"
    green = "#22C55E"
    red = "#EF4444"
    grey = "#CBD5E1"

    image, draw = base_canvas("Trade Result")

    label_font = load_font(30, bold=True)
    value_font = load_font(58, bold=True)
    big_font = load_font(96, bold=True)
    subtitle_font = load_font(34)
    small_font = load_font(30)

    result = result.upper()
    result_colour = green if result == "TP" else red if result == "SL" else grey

    draw.text((90, 270), f"TRADE {trade['trade_number']}", font=value_font, fill=white)

    draw.rounded_rectangle((90, 370, 990, 600), radius=40, fill=inner)
    draw.text((130, 410), result, font=big_font, fill=result_colour)
    draw.text((130, 520), f"{trade['symbol']} • {trade['direction']}", font=subtitle_font, fill=white)

    draw.text((100, 700), "PROFIT / LOSS", font=label_font, fill=muted)
    draw.text((100, 750), f"£{profit}", font=big_font, fill=result_colour)

    draw.text((100, 900), "ENTRY", font=label_font, fill=muted)
    draw.text((100, 945), str(trade["entry"]), font=value_font, fill=white)

    draw.text((100, 1060), "RR", font=label_font, fill=muted)
    draw.text((100, 1105), f"1:{trade['rr']}", font=value_font, fill=white)

    draw.text(
        (90, 1275),
        "Not financial advice. Trade at your own risk.",
        font=small_font,
        fill=muted
    )

    os.makedirs("data/exports", exist_ok=True)

    path = f"data/exports/result_{trade['trade_number'].replace('#', '')}_{trade['symbol']}_{result}.png"
    image.save(path)

    return path


def generate_update_image(trade, title, main_text):
    inner = "#0B0F19"
    white = "#F8FAFC"
    muted = "#94A3B8"
    gold = "#D4AF37"

    image, draw = base_canvas("Trade Update")

    label_font = load_font(30, bold=True)
    value_font = load_font(58, bold=True)
    big_font = load_font(82, bold=True)
    subtitle_font = load_font(34)
    small_font = load_font(30)

    draw.text((90, 270), f"TRADE {trade['trade_number']}", font=value_font, fill=white)

    draw.rounded_rectangle((90, 370, 990, 570), radius=40, fill=inner)
    draw.text((130, 410), title.upper(), font=big_font, fill=gold)
    draw.text((130, 505), f"{trade['symbol']} • {trade['direction']}", font=subtitle_font, fill=white)

    draw.rounded_rectangle((90, 680, 990, 1040), radius=40, fill=inner)
    draw.text((130, 720), "UPDATE", font=label_font, fill=muted)

    draw_wrapped_text(
        draw,
        main_text,
        (130, 780),
        value_font,
        white,
        780,
        line_spacing=18,
        max_lines=4
    )

    draw.text(
        (90, 1275),
        "Not financial advice. Trade at your own risk.",
        font=small_font,
        fill=muted
    )

    os.makedirs("data/exports", exist_ok=True)

    safe_title = title.lower().replace(" ", "_")
    path = f"data/exports/update_{trade['trade_number'].replace('#', '')}_{trade['symbol']}_{safe_title}.png"
    image.save(path)

    return path