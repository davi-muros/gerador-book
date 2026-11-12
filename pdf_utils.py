# Arquivo: pdf_utils.py
import os
import fitz  # PyMuPDF
from config import MAX_PDF_BYTES, MAX_PAGINAS_PDF

def validar_pdf(caminho_arquivo):
    """
    Verifica se o PDF é válido, se não está corrompido, 
    e se respeita os limites de tamanho e páginas definidos em config.py.
    Retorna uma string de erro caso falhe, ou None se estiver tudo ok.
    """
    if not os.path.exists(caminho_arquivo):
        return "Arquivo não encontrado."

    tamanho_bytes = os.path.getsize(caminho_arquivo)
    if tamanho_bytes > MAX_PDF_BYTES:
        return f"Arquivo excede o limite permitido de {MAX_PDF_BYTES / (1024*1024):.0f} MB."

    try:
        with fitz.open(caminho_arquivo) as doc:
            if doc.is_encrypted:
                return "O PDF está protegido por senha ou criptografia."
            
            num_paginas = doc.page_count
            if num_paginas == 0:
                return "O PDF não contém nenhuma página legível."
                
            if num_paginas > MAX_PAGINAS_PDF:
                return f"O PDF possui {num_paginas} páginas. O limite é {MAX_PAGINAS_PDF}."
                
    except Exception as e:
        return f"O arquivo parece estar corrompido ou não é um PDF válido. Detalhe: {str(e)}"

    return None