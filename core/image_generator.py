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


def draw_wrapped_text(draw, text, position, font, fill, max_width, line_spacing=10):
    x, y = position
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)

        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines[:5]:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing


def generate_trade_image(trade):
    width = 1080
    height = 1350

    bg = "#080B12"
    card = "#121826"
    inner = "#0B0F19"
    gold = "#D4AF37"
    white = "#F8FAFC"
    muted = "#94A3B8"
    green = "#22C55E"
    red = "#EF4444"

    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    title_font = load_font(74, bold=True)
    subtitle_font = load_font(34)
    label_font = load_font(30, bold=True)
    value_font = load_font(48, bold=True)
    small_font = load_font(30)
    badge_font = load_font(58, bold=True)

    direction = trade["direction"].upper()
    direction_colour = green if direction == "BUY" else red

    draw.rounded_rectangle((50, 50, width - 50, height - 50), radius=45, fill=card)

    draw.text((90, 90), "MRPAYOUTS", font=title_font, fill=gold)
    draw.text((95, 175), "Signals • Personal Trading Journal", font=subtitle_font, fill=muted)

    draw.text((90, 270), f"TRADE {trade['trade_number']}", font=value_font, fill=white)

    draw.rounded_rectangle((90, 350, 990, 520), radius=35, fill=inner)
    draw.text((130, 385), direction, font=badge_font, fill=direction_colour)
    draw.text((130, 455), trade["symbol"], font=subtitle_font, fill=white)

    y = 610

    items = [
        ("ENTRY", trade["entry"]),
        ("STOP LOSS", trade["sl"]),
        ("TAKE PROFIT", trade["tp"]),
        ("RISK", f"{trade['risk']}%"),
        ("RR", f"1:{trade['rr']}")
    ]

    for label, value in items:
        draw.text((100, y), label, font=label_font, fill=muted)
        draw.text((100, y + 40), str(value), font=value_font, fill=white)
        y += 125

    reason_y = 1110

    draw.rounded_rectangle((90, reason_y, 990, 1245), radius=30, fill=inner)
    draw.text((120, reason_y + 25), "REASON", font=label_font, fill=muted)

    draw_wrapped_text(
        draw,
        trade["reason"],
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

    bg = "#080B12"
    card = "#121826"
    inner = "#0B0F19"
    gold = "#D4AF37"
    white = "#F8FAFC"
    muted = "#94A3B8"
    green = "#22C55E"
    red = "#EF4444"
    grey = "#CBD5E1"

    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    title_font = load_font(74, bold=True)
    subtitle_font = load_font(34)
    label_font = load_font(30, bold=True)
    value_font = load_font(58, bold=True)
    big_font = load_font(96, bold=True)
    small_font = load_font(30)

    result = result.upper()
    result_colour = green if result == "TP" else red if result == "SL" else grey

    draw.rounded_rectangle((50, 50, width - 50, height - 50), radius=45, fill=card)

    draw.text((90, 90), "MRPAYOUTS", font=title_font, fill=gold)
    draw.text((95, 175), "Trade Result", font=subtitle_font, fill=muted)

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