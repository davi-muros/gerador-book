from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from qfluentwidgets import SubtitleLabel, CardWidget, BodyLabel, StrongBodyLabel, PushButton

from models import SessionLocal, BookGerado, RascunhoModel

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Dashboard")
        self.setStyleSheet("QWidget#Dashboard { background-color: #f3f1ea; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        hbox_head = QHBoxLayout()
        vbox_txt = QVBoxLayout()
        vbox_txt.addWidget(SubtitleLabel("Dashboard de Uso", self))
        lbl_sub = BodyLabel("Métricas consolidadas de utilização do DataBook", self)
        lbl_sub.setStyleSheet("color: gray;")
        vbox_txt.addWidget(lbl_sub)
        hbox_head.addLayout(vbox_txt)
        
        btn_refresh = PushButton("Atualizar Dados", self)
        btn_refresh.setStyleSheet("background-color: #f0f0f0; color: #1a1a1a; border: 1px solid #cccccc; border-radius: 4px; padding: 6px 12px;")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.carregar_metricas_banco)
        hbox_head.addWidget(btn_refresh)
        layout.addLayout(hbox_head)
        layout.addSpacing(16)

        h_layout = QHBoxLayout()
        
        self.card_total_books = self.criar_card("0", "Books Gerados (Total)")
        self.card_sucesso = self.criar_card("0", "Gerados c/ Sucesso")
        self.card_erros = self.criar_card("0", "Falhas / Erros")
        self.card_rascunhos = self.criar_card("0", "Rascunhos Ativos")

        for card in (self.card_total_books, self.card_sucesso, self.card_erros, self.card_rascunhos):
            h_layout.addWidget(card["widget"])
        layout.addLayout(h_layout)
        layout.addSpacing(16)

        card_tabela = CardWidget(self)
        card_tabela.setStyleSheet("CardWidget { background-color: #ffffff; border: 1px solid #d8d4c8; border-radius: 8px; }")
        vbox_tab = QVBoxLayout(card_tabela)
        vbox_tab.addWidget(StrongBodyLabel("Últimos Books Processados no Sistema"))

        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(5)
        self.tabela_historico.setHorizontalHeaderLabels(["USUÁRIO", "CÓDIGO DO BOOK", "REGISTRO / PF", "STATUS", "DATA DE GERAÇÃO"])
        self._estilizar_tabela(self.tabela_historico)
        vbox_tab.addWidget(self.tabela_historico)

        layout.addWidget(card_tabela)
        layout.addStretch(1)

        self.carregar_metricas_banco()

    def criar_card(self, valor, texto):
        card = CardWidget(self)
        card.setStyleSheet("CardWidget { background-color: #ffffff; border: 1px solid #d8d4c8; border-radius: 8px; }")
        card.setFixedSize(220, 100)
        vbox = QVBoxLayout(card)
        lbl_valor = SubtitleLabel(valor, card)
        lbl_valor.setStyleSheet("color: #005bb5; font-size: 24px; font-weight: bold;")
        vbox.addWidget(lbl_valor)
        lbl_desc = BodyLabel(texto, card)
        lbl_desc.setStyleSheet("color: #1a1a1a;")
        vbox.addWidget(lbl_desc)
        return {"widget": card, "valor": lbl_valor}

    def _estilizar_tabela(self, tabela):
        style = (
            "QTableWidget { background-color: white; color: #000000; border: none; gridline-color: #d8d4c8; }\n"
            "QHeaderView::section { background-color: #1a1a1a; color: #ffffff; font-weight: bold; font-size: 11px; border: none; border-bottom: 1px solid #d8d4c8; padding: 6px; }\n"
            "QTableWidget::item { color: #000000; padding: 6px; }"
        )
        tabela.setStyleSheet(style)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def carregar_metricas_banco(self):
        session = SessionLocal()
        try:
            total_books = session.query(BookGerado).count()
            books_sucesso = session.query(BookGerado).filter(BookGerado.status == "SUCESSO").count()
            erros = session.query(BookGerado).filter(BookGerado.status == "ERRO").count()
            total_rascunhos = session.query(RascunhoModel).count()

            self.card_total_books["valor"].setText(str(total_books))
            self.card_sucesso["valor"].setText(str(books_sucesso))
            self.card_erros["valor"].setText(str(erros))
            self.card_rascunhos["valor"].setText(str(total_rascunhos))

            ultimos = session.query(BookGerado).order_by(BookGerado.id.desc()).limit(8).all()
            self.tabela_historico.setRowCount(len(ultimos))

            for row, b in enumerate(ultimos):
                self.tabela_historico.setItem(row, 0, QTableWidgetItem(b.nome_usuario or "-"))
                self.tabela_historico.setItem(row, 1, QTableWidgetItem(b.codigo or "-"))
                
                reg = b.registro if b.registro else "-"
                pf = b.pf if b.pf else "-"
                self.tabela_historico.setItem(row, 2, QTableWidgetItem(f"{reg} / {pf}"))
                self.tabela_historico.setItem(row, 3, QTableWidgetItem(b.status or "SUCESSO"))
                
                data_str = b.data_geracao.strftime("%d/%m/%Y %H:%M") if b.data_geracao else "-"
                self.tabela_historico.setItem(row, 4, QTableWidgetItem(data_str))

        except Exception as e:
            print(f"Erro ao carregar métricas: {e}")
        finally:
            session.close()

    def atualizar_metricas(self, anexados_count=0):
        self.carregar_metricas_banco()