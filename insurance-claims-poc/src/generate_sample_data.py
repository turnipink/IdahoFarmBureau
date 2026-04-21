"""
Generate realistic sample insurance claim documents for the POC demo.
Creates:
- A mock police/accident report PDF
- Synthetic damage photos (with annotations)
- A mock medical bill PDF
"""

import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, gray, white, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "sample_reports"
PHOTOS_DIR = DATA_DIR / "sample_photos"

CLAIM_DATA = {
    "claim_number": "CLM-2026-004817",
    "policy_number": "HO-FB-2024-991203",
    "insured_name": "Robert J. Henderson",
    "insured_address": "4521 Maple Creek Dr, Boise, ID 83702",
    "insured_phone": "(208) 555-0147",
    "date_of_loss": "April 12, 2026",
    "time_of_loss": "2:35 AM",
    "type_of_loss": "Wind/Hail Storm Damage",
    "location_of_loss": "4521 Maple Creek Dr, Boise, ID 83702",
    "officer_name": "Officer David M. Torres",
    "officer_badge": "BPD-4412",
    "report_number": "BPD-2026-041200387",
    "description": (
        "On April 12, 2026, at approximately 2:35 AM, a severe thunderstorm "
        "with sustained winds of 65 mph and golf-ball-sized hail impacted the "
        "Maple Creek subdivision in Boise, ID. The insured property at 4521 "
        "Maple Creek Dr sustained significant damage to the roof, siding, "
        "windows, and landscaping. A large oak tree in the front yard was "
        "uprooted and fell onto the detached garage, causing structural damage "
        "to the garage roof and north wall. Multiple vehicles in the driveway "
        "sustained hail damage. The insured reports water intrusion in the "
        "master bedroom and upstairs hallway due to compromised roof shingles."
    ),
    "estimated_damage": "$47,250.00",
    "witnesses": [
        {"name": "Susan K. Park", "phone": "(208) 555-0198", "address": "4519 Maple Creek Dr"},
        {"name": "Michael R. Dunn", "phone": "(208) 555-0234", "address": "4523 Maple Creek Dr"},
    ],
    "responding_units": ["Engine 7", "BPD Unit 22", "Ada County Emergency Mgmt"],
    "weather_source": "NWS Boise Office – Severe Thunderstorm Warning #0412-026",
    "adjuster_name": "Patricia L. Vasquez",
    "adjuster_id": "ADJ-8821",
}


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("SmallGray", parent=ss["Normal"], fontSize=8, textColor=gray))
    ss.add(ParagraphStyle("Field", parent=ss["Normal"], fontSize=10, leading=14))
    ss.add(ParagraphStyle("FieldBold", parent=ss["Normal"], fontSize=10, leading=14, fontName="Helvetica-Bold"))
    ss.add(ParagraphStyle("SectionHead", parent=ss["Heading2"], fontSize=12, textColor=HexColor("#1a3a6b"), spaceAfter=6, spaceBefore=12))
    return ss


def _field_row(label, value, ss):
    return [Paragraph(f"<b>{label}:</b>", ss["FieldBold"]), Paragraph(str(value), ss["Field"])]


def generate_police_report():
    path = str(REPORTS_DIR / "police_report_BPD-2026-041200387.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    ss = _styles()
    d = CLAIM_DATA
    story = []
    story.append(Paragraph("<b>BOISE POLICE DEPARTMENT</b>", ss["Title"]))
    story.append(Paragraph("INCIDENT / ACCIDENT REPORT", ss["Heading2"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#1a3a6b")))
    story.append(Spacer(1, 12))
    meta = [
        _field_row("Report Number", d["report_number"], ss),
        _field_row("Date of Incident", d["date_of_loss"], ss),
        _field_row("Time of Incident", d["time_of_loss"], ss),
        _field_row("Reporting Officer", d["officer_name"], ss),
        _field_row("Badge Number", d["officer_badge"], ss),
        _field_row("Incident Type", d["type_of_loss"], ss),
    ]
    t = Table(meta, colWidths=[2.2*inch, 4.5*inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)
    story.append(Paragraph("INCIDENT LOCATION", ss["SectionHead"]))
    story.append(Paragraph(d["location_of_loss"], ss["Field"]))
    story.append(Paragraph("INVOLVED PARTIES", ss["SectionHead"]))
    parties = [
        _field_row("Property Owner", d["insured_name"], ss),
        _field_row("Address", d["insured_address"], ss),
        _field_row("Phone", d["insured_phone"], ss),
    ]
    t2 = Table(parties, colWidths=[2.2*inch, 4.5*inch])
    t2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t2)
    story.append(Paragraph("NARRATIVE / DESCRIPTION", ss["SectionHead"]))
    story.append(Paragraph(d["description"], ss["Field"]))
    story.append(Paragraph("WITNESSES", ss["SectionHead"]))
    for i, w in enumerate(d["witnesses"], 1):
        story.append(Paragraph(f"<b>Witness {i}:</b> {w['name']} — {w['phone']} — {w['address']}", ss["Field"]))
    story.append(Paragraph("RESPONDING UNITS", ss["SectionHead"]))
    story.append(Paragraph(", ".join(d["responding_units"]), ss["Field"]))
    story.append(Paragraph("WEATHER REFERENCE", ss["SectionHead"]))
    story.append(Paragraph(d["weather_source"], ss["Field"]))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=gray))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Preliminary Estimated Damage:</b> {d['estimated_damage']}", ss["Field"]))
    story.append(Spacer(1, 30))
    sig = [
        [Paragraph("_________________________", ss["Field"]), Paragraph("_________________________", ss["Field"])],
        [Paragraph(d["officer_name"], ss["SmallGray"]), Paragraph("Date", ss["SmallGray"])],
    ]
    t3 = Table(sig, colWidths=[3.3*inch, 3.3*inch])
    story.append(t3)
    doc.build(story)
    print(f"  ✓ Police report → {path}")
    return path


def generate_medical_bill():
    path = str(REPORTS_DIR / "medical_bill_Henderson.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    ss = _styles()
    story = []
    story.append(Paragraph("<b>ST. LUKE'S REGIONAL MEDICAL CENTER</b>", ss["Title"]))
    story.append(Paragraph("190 E. Bannock St, Boise, ID 83712", ss["Normal"]))
    story.append(Paragraph("Phone: (208) 381-2222 | Fax: (208) 381-2223", ss["Normal"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#cc0000")))
    story.append(Spacer(1, 12))
    story.append(Paragraph("PATIENT BILLING STATEMENT", ss["Heading2"]))
    story.append(Spacer(1, 8))
    meta = [
        _field_row("Patient", "Robert J. Henderson", ss),
        _field_row("DOB", "03/14/1978", ss),
        _field_row("Account #", "SLH-2026-88401", ss),
        _field_row("Date of Service", "April 12, 2026", ss),
        _field_row("Attending Physician", "Dr. Sarah M. Kim, MD", ss),
    ]
    t = Table(meta, colWidths=[2.2*inch, 4.5*inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)
    story.append(Paragraph("SERVICES RENDERED", ss["SectionHead"]))
    charges = [
        ["Code", "Description", "Amount"],
        ["99283", "Emergency Dept Visit – Moderate", "$1,245.00"],
        ["73030", "X-Ray, Shoulder (2 views)", "$385.00"],
        ["29105", "Splint Application, Long Arm", "$290.00"],
        ["99070", "Supplies / Materials", "$125.00"],
        ["", "", ""],
        ["", "TOTAL CHARGES", "$2,045.00"],
    ]
    t2 = Table(charges, colWidths=[1.2*inch, 3.5*inch, 1.5*inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a3a6b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, gray),
        ("FONTNAME", (1, -1), (2, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Diagnosis:</b> Contusion right shoulder (S40.011A), Laceration right forearm (S51.811A) "
        "– sustained during storm event while securing property.",
        ss["Field"]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Notes:</b> Patient presented to ER at 3:15 AM on 4/12/2026 reporting injury from falling "
        "debris during severe windstorm. Discharged same day with follow-up in 7 days.",
        ss["Field"]
    ))
    doc.build(story)
    print(f"  ✓ Medical bill → {path}")
    return path


def _draw_label(draw, text, x, y, font_size=18, bg_color=(200, 0, 0)):
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()
    bbox = draw.textbbox((x, y), text, font=font)
    padding = 4
    draw.rectangle([bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding], fill=bg_color)
    draw.text((x, y), text, fill=(255, 255, 255), font=font)


def generate_roof_damage_photo():
    import math
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), color=(120, 140, 160))
    draw = ImageDraw.Draw(img)
    for y in range(0, h // 3):
        gray_val = 150 + y // 4
        draw.line([(0, y), (w, y)], fill=(gray_val, gray_val, gray_val + 10))
    draw.rectangle([100, 350, 1100, 800], fill=(180, 160, 140), outline=(100, 80, 60), width=3)
    draw.polygon([(50, 350), (600, 100), (1150, 350)], fill=(80, 60, 50), outline=(40, 30, 20))
    damage_spots = [(200, 240, 320, 290), (450, 180, 580, 220), (700, 200, 850, 260), (900, 250, 1000, 310)]
    for spot in damage_spots:
        draw.rectangle(spot, fill=(60, 40, 30))
        for stripe_y in range(spot[1], spot[3], 4):
            draw.line([(spot[0], stripe_y), (spot[2], stripe_y)], fill=(90, 70, 50), width=1)
    for wx in [250, 500, 750, 950]:
        draw.rectangle([wx, 450, wx+100, 600], fill=(180, 200, 220), outline=(60, 60, 60), width=2)
        if wx in [500, 950]:
            cx, cy = wx+50, 525
            for angle_offset in range(0, 360, 45):
                ex = cx + int(40 * math.cos(math.radians(angle_offset)))
                ey = cy + int(40 * math.sin(math.radians(angle_offset)))
                draw.line([(cx, cy), (ex, ey)], fill=(100, 100, 120), width=1)
    draw.rectangle([850, 550, 1080, 780], fill=(160, 140, 120), outline=(80, 60, 40), width=2)
    draw.text((870, 560), "GARAGE", fill=(80, 60, 40))
    draw.line([(300, 200), (950, 650)], fill=(80, 50, 20), width=20)
    for bx, by in [(500, 350), (650, 450), (800, 550)]:
        draw.line([(bx, by), (bx-60, by-80)], fill=(60, 40, 10), width=8)
        draw.line([(bx, by), (bx+50, by-70)], fill=(60, 40, 10), width=6)
    random.seed(42)
    for _ in range(80):
        hx, hy, hr = random.randint(100, 1100), random.randint(750, 880), random.randint(3, 8)
        draw.ellipse([hx-hr, hy-hr, hx+hr, hy+hr], fill=(230, 240, 250))
    _draw_label(draw, "MISSING SHINGLES", 200, 195)
    _draw_label(draw, "HAIL IMPACT", 450, 155)
    _draw_label(draw, "FALLEN TREE \u2192 GARAGE", 650, 480)
    _draw_label(draw, "CRACKED WINDOW", 460, 610)
    _draw_label(draw, "HAIL STONES", 350, 855)
    _draw_label(draw, "04/12/2026 09:15 AM | ADJ-8821 | Photo 1 of 4", 20, 15, font_size=14, bg_color=(0, 0, 0))
    path = str(PHOTOS_DIR / "damage_roof_overview.png")
    img.save(path, quality=95)
    print(f"  ✓ Roof damage → {path}")
    return path


def generate_hail_closeup_photo():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), color=(190, 180, 170))
    draw = ImageDraw.Draw(img)
    for y in range(0, h, 30):
        draw.line([(0, y), (w, y)], fill=(170, 160, 150), width=1)
        board_color = (185 + (y % 60) // 10, 175 + (y % 60) // 10, 165 + (y % 60) // 10)
        draw.rectangle([0, y+1, w, y+29], fill=board_color)
    random.seed(99)
    for _ in range(25):
        cx, cy, r = random.randint(100, 1100), random.randint(100, 800), random.randint(8, 22)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(150, 140, 130), outline=(120, 110, 100), width=2)
        draw.ellipse([cx-r//3, cy-r//3, cx+r//3, cy+r//3], fill=(130, 120, 110))
    draw.line([(400, 300), (460, 280), (500, 310), (540, 290)], fill=(100, 90, 80), width=3)
    draw.line([(700, 500), (750, 520), (800, 490), (830, 510)], fill=(100, 90, 80), width=3)
    draw.rectangle([50, 400, 350, 430], fill=(255, 255, 0), outline=(0, 0, 0), width=2)
    for tick in range(50, 351, 30):
        draw.line([(tick, 400), (tick, 430)], fill=(0, 0, 0), width=1)
    _draw_label(draw, "12 inches", 120, 435, font_size=14, bg_color=(0, 0, 0))
    _draw_label(draw, "HAIL IMPACT DENTS \u2014 VINYL SIDING", 300, 50)
    _draw_label(draw, "CRACK IN SIDING", 380, 260)
    _draw_label(draw, "1.5 inch DIAMETER IMPACTS", 550, 550)
    _draw_label(draw, "04/12/2026 09:22 AM | ADJ-8821 | Photo 2 of 4", 20, 15, font_size=14, bg_color=(0, 0, 0))
    path = str(PHOTOS_DIR / "damage_hail_siding_closeup.png")
    img.save(path, quality=95)
    print(f"  ✓ Hail closeup → {path}")
    return path


def generate_interior_water_photo():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), color=(240, 235, 225))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 300], fill=(245, 240, 232))
    draw.rectangle([0, 300, w, h], fill=(235, 230, 220))
    draw.line([(0, 300), (w, 300)], fill=(200, 195, 185), width=4)
    random.seed(77)
    stain_cx, stain_cy = 600, 180
    for _ in range(200):
        sx = stain_cx + random.randint(-120, 120)
        sy = stain_cy + random.randint(-80, 80)
        sr = random.randint(5, 20)
        alpha = random.randint(160, 200)
        draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=(alpha, alpha-20, alpha-50))
    for dx in [550, 600, 640]:
        for dy in range(300, 650, 3):
            drip_w = max(1, 4 - (dy-300)//100)
            draw.line([(dx+random.randint(-2, 2), dy), (dx+random.randint(-2, 2), dy+3)], fill=(200, 190, 170), width=drip_w)
    draw.polygon([(500, 310), (530, 305), (540, 340), (510, 350), (495, 330)], fill=(250, 245, 235), outline=(180, 170, 160))
    draw.polygon([(560, 315), (590, 308), (595, 345), (565, 350)], fill=(250, 245, 235), outline=(180, 170, 160))
    draw.rectangle([200, 700, 1000, h], fill=(160, 150, 130))
    _draw_label(draw, "SATURATED CARPET", 450, 750)
    _draw_label(draw, "WATER STAIN \u2014 CEILING", 430, 80)
    _draw_label(draw, "PEELING PAINT / BUBBLING", 400, 355)
    _draw_label(draw, "ACTIVE WATER INTRUSION", 520, 500)
    _draw_label(draw, "04/12/2026 09:30 AM | ADJ-8821 | Photo 3 of 4", 20, 15, font_size=14, bg_color=(0, 0, 0))
    path = str(PHOTOS_DIR / "damage_interior_water.png")
    img.save(path, quality=95)
    print(f"  ✓ Water damage → {path}")
    return path


def generate_vehicle_hail_photo():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), color=(80, 80, 85))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 500, w, h], fill=(140, 135, 130))
    draw.rounded_rectangle([150, 100, 1050, 750], radius=40, fill=(30, 60, 120), outline=(20, 40, 80), width=3)
    draw.rounded_rectangle([200, 120, 1000, 280], radius=20, fill=(160, 180, 200), outline=(100, 120, 140), width=2)
    draw.line([(450, 200), (500, 160), (600, 210), (700, 150)], fill=(200, 200, 220), width=3)
    random.seed(55)
    for _ in range(40):
        dx, dy, dr = random.randint(250, 950), random.randint(300, 700), random.randint(6, 18)
        draw.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], outline=(20, 45, 100), width=2)
        draw.arc([dx-dr, dy-dr, dx+dr, dy+dr], 200, 360, fill=(50, 80, 150), width=1)
    _draw_label(draw, "HAIL DENTS \u2014 VEHICLE HOOD", 350, 50)
    _draw_label(draw, "WINDSHIELD CRACK", 430, 250)
    _draw_label(draw, "~40 IMPACT POINTS ON HOOD", 350, 760)
    _draw_label(draw, "04/12/2026 09:35 AM | ADJ-8821 | Photo 4 of 4", 20, 15, font_size=14, bg_color=(0, 0, 0))
    path = str(PHOTOS_DIR / "damage_vehicle_hail.png")
    img.save(path, quality=95)
    print(f"  ✓ Vehicle hail → {path}")
    return path


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating sample insurance claim documents...\n")
    generate_police_report()
    generate_medical_bill()
    generate_roof_damage_photo()
    generate_hail_closeup_photo()
    generate_interior_water_photo()
    generate_vehicle_hail_photo()
    print("\n✅ All sample data generated!")
    print(f"   Reports: {REPORTS_DIR}")
    print(f"   Photos:  {PHOTOS_DIR}")


if __name__ == "__main__":
    main()
