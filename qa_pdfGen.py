from fpdf import FPDF

pdf = FPDF()

def createPDF(_d: list, _PdfN: str):
    if not type(_d) is list: raise TypeError(f"Required type {list} for arg _d")
    if not type(_PdfN) is str: raise TypeError(f"Required type {str} for arg _PdfN")
    # Steup
    pdf.add_page()
    pdf.set_font("Courier", size=12)

    for x in _d:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'L')

    pdf.output(_PdfN)