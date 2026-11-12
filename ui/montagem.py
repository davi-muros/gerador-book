import os
import re
import json
import uuid

from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                             QMessageBox, QInputDialog, QDialog, QFormLayout, QDialogButtonBox, QCheckBox)
from qfluentwidgets import (SubtitleLabel, PrimaryPushButton, CardWidget, PushButton, LineEdit,
                            StrongBodyLabel, BodyLabel, SmoothScrollArea)
import fitz  # PyMuPDF

from config import TAXONOMIA, obter_taxonomia_usuario, PADRAO_REGISTRO_PF, PADRAO_CODIGO, SESSAO
from pdf_utils import validar_pdf
from capa import abrir_capa
from models import SessionLocal, BookGerado, RascunhoModel

class MontagemBookWidget(QWidget):
    def __init__(self, dashboard_ref=None, parent=None):
        super().__init__(parent=parent)
        self.dashboard_ref = dashboard_ref
        self.setObjectName("Montagem")
        
        self.usuario_atual = SESSAO.get("usuario", "padrao")
        self.taxonomia_dinamica = obter_taxonomia_usuario(self.usuario_atual)
        
        self.setStyleSheet("QWidget#Montagem { background-color: #f3f1ea; }")
        
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("QWidget { background-color: #f3f1ea; }")
        self.scrollArea.setWidget(self.scrollWidget)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scrollArea)
        
        self.layout = QVBoxLayout(self.scrollWidget)
        self.layout.setContentsMargins(24, 24, 24, 24)

        lbl_titulo = SubtitleLabel(f"Montagem Dinâmica do Book - Operador: {self.usuario_atual.upper()}", self)
        self.layout.addWidget(lbl_titulo)

        card_ident = CardWidget(self)
        card_ident.setStyleSheet("CardWidget { background-color: #ffffff; border: 1px solid #d8d4c8; border-radius: 8px; }")
        vbox_ident = QVBoxLayout(card_ident)
        vbox_ident.addWidget(StrongBodyLabel("Identificação do Book"))
        hbox_inputs = QHBoxLayout()
        
        self.input_registro = self._criar_input("REGISTROS (Ex: 320824 / 320825)", 200)
        self.input_pf = self._criar_input("OM / PF (Ex: 2029810494)", 200)
        self.input_codigo = self._criar_input("Código (Ex: PRJ-001-2025)", 100)
        
        for campo in (self.input_registro, self.input_pf, self.input_codigo):
            hbox_inputs.addWidget(campo)
        vbox_ident.addLayout(hbox_inputs)
        self.layout.addWidget(card_ident)

        hbox_acoes = QHBoxLayout()
        btn_limpar = PushButton("Limpar e Resetar Padrão", self)
        btn_limpar.setStyleSheet("background-color: #e0e0e0; color: #1a1a1a; border: 1px solid #b0b0b0; border-radius: 4px; padding: 6px;")
        btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpar.clicked.connect(self.limpar_rascunho)
        
        btn_salvar_rascunho = PushButton("Salvar Rascunho", self)
        btn_salvar_rascunho.setStyleSheet("background-color: #1a1a1a; color: white; border: 1px solid #000000; border-radius: 4px; padding: 6px;")
        btn_salvar_rascunho.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salvar_rascunho.clicked.connect(lambda: self.salvar_rascunho(notificar=True))

        self.btn_gerar = PrimaryPushButton("Gerar Book Final (PDF)", self)
        self.btn_gerar.setStyleSheet("background-color: #005bb5; color: white; border: 1px solid #004494; border-radius: 4px; padding: 6px;")
        self.btn_gerar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gerar.clicked.connect(self.validar_e_gerar)

        hbox_acoes.addWidget(btn_limpar)
        hbox_acoes.addWidget(btn_salvar_rascunho)
        hbox_acoes.addStretch(1)
        hbox_acoes.addWidget(self.btn_gerar)

        self.layout.addSpacing(20)
        self.layout.addLayout(hbox_acoes)
        self.layout.addStretch(1)

        self.botoes_anexar = {}
        self.botoes_remover = {}
        self.widget_taxonomia = None
        
        self.carregar_rascunho()

    def _criar_input(self, placeholder, max_len):
        campo = LineEdit(self)
        campo.setPlaceholderText(placeholder)
        campo.setMaxLength(max_len)
        campo.setValidator(QRegularExpressionValidator(QRegularExpression(r"[A-Za-z0-9._\s/,-]*"), campo))
        return campo

    def renderizar_taxonomia(self):
        if self.widget_taxonomia:
            self.layout.removeWidget(self.widget_taxonomia)
            self.widget_taxonomia.deleteLater()
            
        self.widget_taxonomia = QWidget()
        vbox_tax = QVBoxLayout(self.widget_taxonomia)
        vbox_tax.setContentsMargins(0, 0, 0, 0)
        
        self.botoes_anexar.clear()
        self.botoes_remover.clear()
        
        for secao_idx, secao in enumerate(self.taxonomia_dinamica):
            vbox_tax.addSpacing(16)
            vbox_tax.addWidget(StrongBodyLabel(secao['div'], self.widget_taxonomia))
            
            card_divisoria = CardWidget(self.widget_taxonomia)
            card_divisoria.setStyleSheet("CardWidget { background-color: #ffffff; border: 1px solid #d8d4c8; border-radius: 8px; }")
            vbox_divisoria = QVBoxLayout(card_divisoria)
            
            for item_idx, item in enumerate(secao['items']):
                self.criar_linha(vbox_divisoria, secao_idx, item_idx, item)
            
            btn_add = PushButton("+ Adicionar Documento Extra", self.widget_taxonomia)
            btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_add.setStyleSheet("background-color: #f9f9f9; color: #1a1a1a; border: 1px dashed #cccccc; border-radius: 4px; padding: 4px;")
            btn_add.clicked.connect(lambda _, s=secao_idx: self.adicionar_item(s))
            vbox_divisoria.addSpacing(8)
            vbox_divisoria.addWidget(btn_add)
            
            vbox_tax.addWidget(card_divisoria)
            
        self.layout.insertWidget(1, self.widget_taxonomia)
        self.atualizar_dashboard_contagem()

    def criar_linha(self, parent_layout, secao_idx, item_idx, item):
        item_layout = QHBoxLayout()
        item_layout.addWidget(BodyLabel(item['code'], self.widget_taxonomia))
        item_layout.addWidget(StrongBodyLabel(item['name'], self.widget_taxonomia))

        lbl_status = BodyLabel("obrigatório" if item['req'] else "opcional", self.widget_taxonomia)
        lbl_status.setStyleSheet("color: #005bb5; font-weight: bold;" if item['req'] else "color: gray;")
        item_layout.addWidget(lbl_status)
        item_layout.addStretch(1)
        
        key = item['key']
        arquivo_atual = self.arquivos_anexados.get(key)

        btn_excluir = PushButton("Excluir", self.widget_taxonomia)
        btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excluir.setStyleSheet("background-color: #fcebeb; color: #a30000; border: 1px solid #a30000; border-radius: 4px; padding: 4px 10px;")
        btn_excluir.clicked.connect(lambda _, s=secao_idx, i=item_idx: self.excluir_item(s, i))

        btn_mover = PushButton("Mover", self.widget_taxonomia)
        btn_mover.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_mover.setStyleSheet("background-color: #e6f0fa; color: #005bb5; border: 1px solid #005bb5; border-radius: 4px; padding: 4px 10px;")
        btn_mover.clicked.connect(lambda _, s=secao_idx, i=item_idx: self.mover_item(s, i))

        btn_anexar = PushButton(os.path.basename(arquivo_atual) if arquivo_atual else "Anexar PDF", self.widget_taxonomia)
        btn_anexar.setStyleSheet("background-color: #f0f0f0; color: #1a1a1a; border: 1px solid #cccccc; border-radius: 4px; padding: 4px 10px;")
        btn_anexar.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_remover = PushButton("Remover", self.widget_taxonomia)
        btn_remover.setStyleSheet("PushButton { background-color: #ffe6e6; color: #a30000; border: 1px solid #a30000; border-radius: 4px; padding: 4px 10px; }")
        btn_remover.setCursor(Qt.CursorShape.PointingHandCursor)
        if not arquivo_atual:
            btn_remover.hide()
        
        btn_anexar.clicked.connect(lambda: self.selecionar_arq(btn_anexar, btn_remover, key))
        btn_remover.clicked.connect(lambda: self.remover_arq(btn_anexar, btn_remover, key))

        self.botoes_anexar[key] = btn_anexar
        self.botoes_remover[key] = btn_remover

        item_layout.addWidget(btn_excluir)
        item_layout.addWidget(btn_mover)
        item_layout.addWidget(btn_remover)
        item_layout.addWidget(btn_anexar)
        parent_layout.addLayout(item_layout)

    def adicionar_item(self, secao_idx):
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar Documento Extra")
        dialog.setFixedSize(360, 200)
        layout = QFormLayout(dialog)
        
        input_cod = LineEdit(dialog)
        input_cod.setPlaceholderText("Ex: 5.4")
        input_nome = LineEdit(dialog)
        input_nome.setPlaceholderText("Nome do Documento")
        
        cb_req = QCheckBox("Classificar como OBRIGATÓRIO", dialog)
        cb_req.setStyleSheet("color: #005bb5; font-weight: bold; margin-top: 5px;")
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        
        layout.addRow("Código:", input_cod)
        layout.addRow("Nome:", input_nome)
        layout.addRow("", cb_req)
        layout.addWidget(btn_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cod = input_cod.text().strip()
            nome = input_nome.text().strip()
            req = cb_req.isChecked()
            
            if not cod or not nome:
                QMessageBox.warning(self, "Aviso", "Preencha o Código e o Nome.")
                return
                    
            nova_key = f"custom_{uuid.uuid4().hex[:8]}"
            novo_item = {"code": cod, "name": nome, "req": req, "key": nova_key}
            self.taxonomia_dinamica[secao_idx]['items'].append(novo_item)
            self.arquivos_anexados[nova_key] = None
            self.renderizar_taxonomia()

    def excluir_item(self, secao_idx, item_idx):
        item = self.taxonomia_dinamica[secao_idx]['items'][item_idx]
        if item['req']:
            QMessageBox.critical(self, "Acesso Negado", "Impossível excluir documentos OBRIGATÓRIOS.")
            return
            
        if QMessageBox.question(self, "Excluir Tópico", f"Excluir o tópico '{item['name']}'?", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            key = item['key']
            self.taxonomia_dinamica[secao_idx]['items'].pop(item_idx)
            if key in self.arquivos_anexados:
                del self.arquivos_anexados[key]
            self.renderizar_taxonomia()

    def mover_item(self, secao_idx, item_idx):
        opcoes = [s['div'] for s in self.taxonomia_dinamica]
        div_atual = opcoes[secao_idx]
        div_escolhida, ok = QInputDialog.getItem(self, "Mover Documento", "Selecione a nova divisão:", opcoes, secao_idx, False)
        
        if ok and div_escolhida and div_escolhida != div_atual:
            novo_secao_idx = opcoes.index(div_escolhida)
            item = self.taxonomia_dinamica[secao_idx]['items'].pop(item_idx)
            self.taxonomia_dinamica[novo_secao_idx]['items'].append(item)
            self.renderizar_taxonomia()

    def atualizar_dashboard_contagem(self):
        if self.dashboard_ref:
            exigidos_anexados = sum(1 for sec in self.taxonomia_dinamica for item in sec['items'] if item['req'] and self.arquivos_anexados.get(item['key']))
            self.dashboard_ref.atualizar_metricas(exigidos_anexados)

    def selecionar_arq(self, btn_anexar, btn_remover, key):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar PDF", "", "PDF Files (*.pdf)")
        if not arquivo: return
        erro = validar_pdf(arquivo)
        if erro:
            QMessageBox.warning(self, "Arquivo recusado", f"{os.path.basename(arquivo)}\n\n{erro}.")
            return
        self.arquivos_anexados[key] = arquivo
        btn_anexar.setText(os.path.basename(arquivo))
        btn_remover.show()
        self.atualizar_dashboard_contagem()

    def remover_arq(self, btn_anexar, btn_remover, key):
        self.arquivos_anexados[key] = None
        btn_anexar.setText("Anexar PDF")
        btn_remover.hide()
        self.atualizar_dashboard_contagem()

    def salvar_rascunho(self, notificar=False):
        session = SessionLocal()
        try:
            rascunho = session.query(RascunhoModel).filter_by(nome_usuario=self.usuario_atual).first()
            if not rascunho:
                rascunho = RascunhoModel(nome_usuario=self.usuario_atual)
                session.add(rascunho)
            
            rascunho.registro = self.input_registro.text().strip()
            rascunho.pf = self.input_pf.text().strip()
            rascunho.codigo = self.input_codigo.text().strip()
            
            dados = {"taxonomia": self.taxonomia_dinamica, "arquivos": self.arquivos_anexados}
            rascunho.arquivos_json = json.dumps(dados, ensure_ascii=False)
            
            session.commit()
            if notificar:
                QMessageBox.information(self, "Rascunho Salvo", "Salvo no banco de dados!")
        except Exception as e:
            if notificar: QMessageBox.warning(self, "Erro ao Salvar", f"Erro: {e}")
        finally:
            session.close()

    def carregar_rascunho(self):
        self.arquivos_anexados = {item['key']: None for sec in self.taxonomia_dinamica for item in sec['items']}
        session = SessionLocal()
        try:
            rascunho = session.query(RascunhoModel).filter_by(nome_usuario=self.usuario_atual).first()
            if not rascunho:
                self.renderizar_taxonomia()
                return

            self.input_registro.setText(rascunho.registro or "")
            self.input_pf.setText(rascunho.pf or "")
            self.input_codigo.setText(rascunho.codigo or "")
            
            if rascunho.arquivos_json:
                dados = json.loads(rascunho.arquivos_json)
                if "taxonomia" in dados:
                    self.taxonomia_dinamica = dados["taxonomia"]
                    self.arquivos_anexados = dados["arquivos"]
        except Exception:
            pass
        finally:
            session.close()
            self.renderizar_taxonomia()

    def limpar_rascunho(self):
        self.input_registro.clear()
        self.input_pf.clear()
        self.input_codigo.clear()
        
        self.taxonomia_dinamica = obter_taxonomia_usuario(self.usuario_atual)
        self.arquivos_anexados = {item['key']: None for sec in self.taxonomia_dinamica for item in sec['items']}
        
        session = SessionLocal()
        try:
            rascunho = session.query(RascunhoModel).filter_by(nome_usuario=self.usuario_atual).first()
            if rascunho:
                session.delete(rascunho)
                session.commit()
        except Exception:
            pass
        finally:
            session.close()
            self.renderizar_taxonomia()

    def validar_e_gerar(self):
        erros = []
        for secao in self.taxonomia_dinamica:
            for item in secao['items']:
                if item['req'] and not self.arquivos_anexados.get(item['key']):
                    erros.append(f"{item['code']} - {item['name']}")
                    
        if erros:
            QMessageBox.critical(self, "Pendência", "Os seguintes itens são OBRIGATÓRIOS:\n\n" + "\n".join(erros))
            return

        registro = self.input_registro.text().strip()
        pf = self.input_pf.text().strip()
        codigo = self.input_codigo.text().strip()
        
        if not (re.fullmatch(PADRAO_REGISTRO_PF, registro) and re.fullmatch(PADRAO_REGISTRO_PF, pf) and re.fullmatch(PADRAO_CODIGO, codigo)):
            QMessageBox.critical(self, "Identificação inválida", "Preencha Registro, PF e Código de forma válida.")
            return

        pastas = [os.path.dirname(p) for p in self.arquivos_anexados.values() if p]
        pasta_inicial = pastas[0] if pastas else ""
        nome_sugerido = f"Book_{registro.replace('/', '-').replace(' ', '')}.pdf"
        destino, _ = QFileDialog.getSaveFileName(self, "Salvar Book", os.path.join(pasta_inicial, nome_sugerido), "PDF (*.pdf)")
        if not destino: return
        if not destino.lower().endswith(".pdf"): destino += ".pdf"

        self.btn_gerar.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.montar_book(registro, pf, codigo, destino)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao gerar", f"Erro:\n{e}")
        else:
            QMessageBox.information(self, "Sucesso", f"Book gerado com sucesso e formatado para impressão frente e verso:\n{destino}")
            self.limpar_rascunho()
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_gerar.setEnabled(True)

    def montar_book(self, registro, pf, codigo, destino):
        doc_final = fitz.open()
        toc = []

        def adicionar(nivel, titulo, doc_origem):
            if doc_final.page_count > 0 and doc_final.page_count % 2 != 0:
                doc_final.new_page()
            toc.append([nivel, titulo, doc_final.page_count + 1])
            doc_final.insert_pdf(doc_origem)

        try:
            with abrir_capa(registro, pf, codigo) as capa:
                adicionar(1, "Capa", capa)

            for secao in self.taxonomia_dinamica:
                titulo_div = secao['div']
                presentes = [(item['key'], f"{item['code']} - {item['name']}") for item in secao['items'] if self.arquivos_anexados.get(item['key'])]
                if not presentes: continue
                    
                with abrir_capa(registro, pf, codigo, titulo_div) as capa:
                    adicionar(1, titulo_div, capa)
                    
                for chave, titulo in presentes:
                    with fitz.open(self.arquivos_anexados[chave], filetype="pdf") as origem:
                        adicionar(2, titulo, origem)

            doc_final.set_toc(toc)
            doc_final.set_metadata({"title": f"Data Book - {codigo}", "author": "Empresa XYZ"})
            doc_final.save(destino, garbage=3, deflate=True)
            self.enviar_log_banco(registro, pf, codigo, destino, "SUCESSO", f"Gerado com {doc_final.page_count} páginas.")

        except Exception as e:
            self.enviar_log_banco(registro, pf, codigo, destino, "ERRO", f"Falha: {str(e)}")
            raise e
        finally:
            doc_final.close()

    def enviar_log_banco(self, registro, pf, codigo, caminho, status, detalhe):
        session = SessionLocal()
        try:
            novo_log = BookGerado(nome_usuario=self.usuario_atual, registro=registro[:50], pf=pf[:50], codigo=codigo,
                                  caminho_pdf=caminho, status=status, log_detalhado=detalhe)
            session.add(novo_log)
            session.commit()
        except Exception:
            pass
        finally:
            session.close()