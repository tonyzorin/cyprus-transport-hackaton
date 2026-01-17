#!/usr/bin/env python3
"""Generate a government news image with QR code for 2026 Tax Reform"""

from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

# Image dimensions (16:9 aspect ratio for display)
WIDTH = 1920
HEIGHT = 1080

# Colors - Cyprus government style (blue and gold)
BG_COLOR = "#1a365d"  # Dark blue
ACCENT_COLOR = "#d69e2e"  # Gold
TEXT_COLOR = "#ffffff"
SUBTITLE_COLOR = "#a0aec0"

# Create the image
img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Add a gradient-like effect with rectangles
for i in range(100):
    alpha = int(255 * (1 - i/100))
    y = HEIGHT - i * 3
    draw.rectangle([(0, y), (WIDTH, HEIGHT)], fill="#0d1b2a")

# Add decorative gold line at top
draw.rectangle([(0, 0), (WIDTH, 8)], fill=ACCENT_COLOR)

# Add Cyprus coat of arms placeholder (gold circle)
draw.ellipse([(80, 80), (180, 180)], fill=ACCENT_COLOR)
draw.ellipse([(95, 95), (165, 165)], fill=BG_COLOR)

# Try to use a nice font, fallback to default
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Header text
draw.text((220, 100), "REPUBLIC OF CYPRUS", font=subtitle_font, fill=ACCENT_COLOR)

# Main title
draw.text((80, 200), "2026 Tax Reform", font=title_font, fill=TEXT_COLOR)

# Subtitle
draw.text((80, 300), "New Tax Regulations Coming Into Effect", font=subtitle_font, fill=SUBTITLE_COLOR)

# Key points
points = [
    "• Income tax brackets updated for 2026",
    "• New digital services tax implemented",
    "• VAT exemptions for essential goods extended",
    "• Green energy incentives increased by 25%",
    "• Small business tax relief program expanded"
]

y_pos = 400
for point in points:
    draw.text((100, y_pos), point, font=body_font, fill=TEXT_COLOR)
    y_pos += 50

# Generate QR code
qr_url = "https://mof.gov.cy/tax-reform-2026"
qr = qrcode.QRCode(version=1, box_size=8, border=2)
qr.add_data(qr_url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#1a365d", back_color="white")

# Resize QR code
qr_size = 250
qr_img = qr_img.resize((qr_size, qr_size))

# Position QR code on the right side
qr_x = WIDTH - qr_size - 100
qr_y = HEIGHT // 2 - qr_size // 2

# Add white background for QR code
draw.rectangle([(qr_x - 20, qr_y - 20), (qr_x + qr_size + 20, qr_y + qr_size + 20)], fill="white", outline=ACCENT_COLOR, width=3)

# Paste QR code
img.paste(qr_img, (qr_x, qr_y))

# QR code label
draw.text((qr_x - 10, qr_y + qr_size + 40), "Scan for details", font=small_font, fill=SUBTITLE_COLOR)
draw.text((qr_x - 10, qr_y + qr_size + 70), "mof.gov.cy/tax-reform-2026", font=small_font, fill=ACCENT_COLOR)

# Footer
draw.rectangle([(0, HEIGHT - 80), (WIDTH, HEIGHT)], fill="#0d1b2a")
draw.text((80, HEIGHT - 55), "Ministry of Finance  |  Effective from January 1, 2026", font=small_font, fill=SUBTITLE_COLOR)

# Save the image
output_path = "/app/uploads/gov_tax_reform_2026.png"
img.save(output_path, "PNG", quality=95)
print(f"Image saved to {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
