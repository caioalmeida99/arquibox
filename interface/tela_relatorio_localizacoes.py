import customtkinter as ctk
from tkinter import messagebox, Scrollbar, VERTICAL, RIGHT, Y
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from database.session import SessionLocal
from models.models import Caixa, Documento, Status, Localizacao
from interface.permissao import verificar_permissao

class RelatorioLocalizacoes(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Relatório de Localizações")
        self.state("zoomed")

        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 2:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return
        self.resizable(False, False)

        self.resultados = []
        self.lista_salas = []
        self._construir_interface()
        self._carregar_salas()

    def _construir_interface(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Sala
        label_sala = ctk.CTkLabel(frame, text="Sala (opcional):")
        label_sala.pack(anchor="w", pady=(0, 5))
        self.combobox_sala = ctk.CTkComboBox(frame, values=[])
        self.combobox_sala.pack(anchor="w", pady=(0, 10))

        # Prateleira
        label_prat = ctk.CTkLabel(frame, text="Prateleira (opcional):")
        label_prat.pack(anchor="w", pady=(0, 5))
        self.entrada_prateleira = ctk.CTkEntry(frame, width=200)
        self.entrada_prateleira.pack(anchor="w", pady=(0, 10))

        # Coluna
        label_col = ctk.CTkLabel(frame, text="Coluna (opcional):")
        label_col.pack(anchor="w", pady=(0, 5))
        self.entrada_coluna = ctk.CTkEntry(frame, width=200)
        self.entrada_coluna.pack(anchor="w", pady=(0, 15))

        # Botões
        btn_buscar = ctk.CTkButton(frame, text="Buscar", width=100, command=self.buscar_localizacoes)
        btn_buscar.pack(anchor="w", pady=(0, 10))

        btn_pdf = ctk.CTkButton(frame, text="Gerar PDF", width=100, command=self.gerar_pdf)
        btn_pdf.pack(anchor="w", pady=(0, 20))

        # Área de texto
        frame_texto = ctk.CTkFrame(frame, fg_color="#1f1f1f", border_width=1, border_color="#444")
        frame_texto.pack(fill="both", expand=True)

        self.texto_resultado = ctk.CTkTextbox(frame_texto, fg_color="#2b2b2b", border_width=0, text_color="white")
        self.texto_resultado.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame_texto, orient=VERTICAL, command=self.texto_resultado.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.texto_resultado.configure(yscrollcommand=scrollbar.set)

    def _carregar_salas(self):
        session: Session = SessionLocal()
        try:
            salas = session.query(distinct(Localizacao.sala)).order_by(Localizacao.sala).all()
            self.lista_salas = [''] + [s[0] for s in salas if s[0]]
            self.combobox_sala.configure(values=self.lista_salas)
            self.combobox_sala.set('')
        finally:
            session.close()

    def buscar_localizacoes(self):
        sala_str = self.combobox_sala.get().strip()
        prateleira_str = self.entrada_prateleira.get().strip()
        coluna_str = self.entrada_coluna.get().strip()

        if not sala_str and not prateleira_str and not coluna_str:
            messagebox.showwarning("Aviso", "Preencha pelo menos um campo para buscar.")
            return

        session: Session = SessionLocal()
        try:
            query = session.query(Localizacao, Caixa, Documento, Status) \
                .join(Caixa, Caixa.localizacao_id == Localizacao.id) \
                .join(Documento, Caixa.documento_id == Documento.id) \
                .join(Status, Caixa.status_id == Status.id)

            if sala_str:
                query = query.filter(Localizacao.sala == sala_str)
            if prateleira_str:
                query = query.filter(Localizacao.prateleira == prateleira_str)
            if coluna_str:
                query = query.filter(Localizacao.coluna == coluna_str)

            resultados = query.all()
            self.resultados = resultados
            self.texto_resultado.delete("0.0", "end")

            if not resultados:
                self.texto_resultado.insert("end", "Nenhuma localização encontrada com esses filtros.")
            else:
                for localizacao, caixa, documento, status in resultados:
                    self.texto_resultado.insert(
                        "end",
                        f"Sala: {localizacao.sala}, Prateleira: {localizacao.prateleira}, Coluna: {localizacao.coluna}, "
                        f"Caixa: {caixa.id}, Documento: {documento.tp_doc}, Status: {status.tipo}\n"
                    )

        finally:
            session.close()

    def gerar_pdf(self):
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum dado para gerar PDF.")
            return

        nome_arquivo = "relatorio_localizacoes.pdf"
        downloads = Path.home() / "Downloads"
        caminho_completo = downloads / nome_arquivo

        try:
            c = canvas.Canvas(str(caminho_completo), pagesize=A4)
            largura, altura = A4

            # Cabeçalho
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(largura / 2, altura - 50, "ARQUIBOX - Relatório de Localizações")

            c.setFont("Helvetica", 10)
            c.drawRightString(largura - 50, altura - 70, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            total = len(self.resultados)
            c.drawString(50, altura - 90, f"Total de localizações: {total}")

            # Cabeçalhos
            col_sala = 50
            col_prat = 110
            col_coluna = 180
            col_caixa = 250
            col_doc = 310
            col_status = 420

            c.setFont("Helvetica-Bold", 9)
            y_header = altura - 110
            c.drawString(col_sala, y_header, "SALA")
            c.drawString(col_prat, y_header, "PRAT.")
            c.drawString(col_coluna, y_header, "COL.")
            c.drawString(col_caixa, y_header, "CAIXA")
            c.drawString(col_doc, y_header, "DOCUMENTO")
            c.drawString(col_status, y_header, "STATUS")

            # Conteúdo
            y = altura - 130
            c.setFont("Helvetica", 8)
            line_height = 12

            for localizacao, caixa, documento, status in self.resultados:
                c.drawString(col_sala, y, str(localizacao.sala))
                c.drawString(col_prat, y, str(localizacao.prateleira))
                c.drawString(col_coluna, y, str(localizacao.coluna))
                c.drawString(col_caixa, y, str(caixa.id))
                c.drawString(col_doc, y, str(documento.tp_doc))
                c.drawString(col_status, y, str(status.tipo))

                y -= line_height
                if y < 80:
                    c.showPage()
                    y = altura - 100
                    c.setFont("Helvetica", 8)

            c.save()
            messagebox.showinfo("Sucesso", f"PDF '{nome_arquivo}' gerado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}")
