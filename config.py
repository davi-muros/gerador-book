import copy
import sys
import os

# Variável de sessão que o login.py está procurando
SESSAO = {"usuario": "padrao"}

PADRAO_REGISTRO_PF = r"^[A-Za-z0-9._\s/,-]+$"
PADRAO_CODIGO = r"^[A-Za-z0-9._-]+$"
MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_PAGINAS_PDF = 500

TAXONOMIA = [
    {"div": "DATA BOOK PADRÃO", "items": [{"code": "1.0", "name": "Documentação Geral", "req": True, "key": "geral_1"}]}
]

# PERFIS GENÉRICOS 
PERFIS_TAXONOMIA = {
    "operador.nivel1": [
        {
            "div": "DATA BOOK - EXECUÇÃO",
            "items": [
                {"code": "1.1", "name": "Cópia da SS", "req": True, "key": "op1_ss"},
                {"code": "1.2", "name": "Delineamento", "req": True, "key": "op1_del"},
                {"code": "1.3", "name": "Relatório de Qualidade", "req": False, "key": "op1_rel"},
            ]
        }
    ],
    "operador.nivel2": [
        {
            "div": "ENSAIOS E RASTREABILIDADE",
            "items": [
                {"code": "2.1", "name": "Mapa de Rastreabilidade", "req": True, "key": "op2_mapa"},
                {"code": "2.2", "name": "Ensaio Visual", "req": True, "key": "op2_vis"},
                {"code": "2.3", "name": "Raio X", "req": False, "key": "op2_rx"},
            ]
        }
    ]
}

def obter_taxonomia_usuario(login_digitado):
    usuario = login_digitado.lower().strip()
    if usuario in PERFIS_TAXONOMIA:
        return copy.deepcopy(PERFIS_TAXONOMIA[usuario])
    return copy.deepcopy(TAXONOMIA)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)