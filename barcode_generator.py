import os
import io
import re
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm

X_MM = 22
Y_MM_FROM_TOP = 45.0
BAR_HEIGHT_MM = 10
BAR_WIDTH_MM = 0.4

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def get_transfer_note(pdf_path):
    reader = PdfReader(pdf_path)
    text = reader.pages[0].extract_text()
    match = re.search(r"Transfer Note Ref\\. No\\.\\s*(\\w+)", text)
    if not match:
        raise ValueError("Transfer Note Ref. No. tidak ditemukan")
    return match.group(1)

def process_pdf(file_name):
    src = os.path.join(INPUT_DIR, file_name)
    dst = os.path.join(OUTPUT_DIR, file_name.replace(".pdf", "_BARCODE_FINAL.pdf"))

    barcode_value = get_transfer_note(src)

    reader = PdfReader(src)
    writer = PdfWriter()
    page = reader.pages[0]

    w = float(page.mediabox.width)
    h = float(page.mediabox.height)

    x_pt = X_MM * mm
    y_pt = h - (Y_MM_FROM_TOP * mm)
    y_pt = max(5 * mm, min(y_pt, h - (15 * mm)))

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(w, h))

    barcode = code128.Code128(
        barcode_value,
        barHeight=BAR_HEIGHT_MM * mm,
        barWidth=BAR_WIDTH_MM * mm
    )

    barcode.drawOn(c, x_pt, y_pt)
    c.save()
    packet.seek(0)

    overlay = PdfReader(packet)
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(dst, "wb") as f:
        writer.write(f)

def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(".pdf"):
            try:
                process_pdf(file)
            except Exception as e:
                print(f"ERROR {file}: {e}")

if __name__ == "__main__":
    main()
