# Arquivo: capa.py
import os
import tempfile
from contextlib import contextmanager
import fitz  # PyMuPDF

@contextmanager
def abrir_capa(registro, pf, codigo, divisoria=None):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # Tamanho A4 vertical (Retrato)

    #  detecta pluralidade
    label_registro = "REGISTROS:" if ("/" in registro or "," in registro or " " in registro) else "REGISTRO:"
    label_pf = "OM:" if ("/" in pf or "," in pf or " " in pf) else "OM:"

    texto_registro = f"{label_registro} {registro}."
    texto_pf = f"{label_pf} {pf}."

    page.insert_textbox(fitz.Rect(50, 150, 545, 200), codigo, fontname="times-bold", fontsize=18, align=1)

    texto_divisoria = divisoria if divisoria else "DATA BOOK - GERAL"
    page.insert_textbox(fitz.Rect(50, 300, 545, 400), texto_divisoria, fontname="times-bold", fontsize=24, align=1)

    page.insert_textbox(fitz.Rect(50, 500, 545, 560), texto_registro, fontname="times-bold", fontsize=14, align=1)
    page.insert_textbox(fitz.Rect(50, 570, 545, 650), texto_pf, fontname="times-bold", fontsize=14, align=1)

    temp_path = tempfile.mktemp(suffix=".pdf")
    doc.save(temp_path)
    doc.close()

    try:
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass