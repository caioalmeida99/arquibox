import customtkinter as ctk
from tkinter import messagebox, Scrollbar, VERTICAL, RIGHT, Y
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from database.session import SessionLocal
from models.models import Documento, Caixa, Status, Localizacao
from interface.permissao import verificar_permissao

class RelatorioDocumentos(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Relatório de Documentos")
        self.state("zoomed")
        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 1:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return
        self.resizable(False, False)

        self.resultados = []
        self.lista_tipos = []
        self._construir_interface()
        self._carregar_tipos_documentos()

    def _construir_interface(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Data Início
        label_inicio = ctk.CTkLabel(frame, text="Data Início (dd/mm/aaaa - opcional):")
        label_inicio.pack(anchor="w", pady=(0, 5))
        self.entrada_data_inicio = ctk.CTkEntry(frame, width=200)
        self.entrada_data_inicio.pack(anchor="w", pady=(0, 10))
        self.entrada_data_inicio.bind("<KeyRelease>", self._formatar_data_entrada)

        # Data Fim
        label_fim = ctk.CTkLabel(frame, text="Data Fim (dd/mm/aaaa - opcional):")
        label_fim.pack(anchor="w", pady=(0, 5))
        self.entrada_data_fim = ctk.CTkEntry(frame, width=200)
        self.entrada_data_fim.pack(anchor="w", pady=(0, 10))
        self.entrada_data_fim.bind("<KeyRelease>", self._formatar_data_entrada)

        # Tipo de Documento
        label_doc = ctk.CTkLabel(frame, text="Tipo de Documento (opcional):")
        label_doc.pack(anchor="w", pady=(0, 5))
        self.combobox_tipo_doc = ctk.CTkComboBox(frame, values=[])
        self.combobox_tipo_doc.pack(anchor="w", pady=(0, 15))

        # Botões
        btn_buscar = ctk.CTkButton(frame, text="Buscar", width=100, command=self.buscar_documentos)
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

    def _carregar_tipos_documentos(self):
        session: Session = SessionLocal()
        try:
            tipos = session.query(distinct(Documento.tp_doc)).order_by(Documento.tp_doc).all()
            self.lista_tipos = [''] + [tp[0] for tp in tipos if tp[0]]
            self.combobox_tipo_doc.configure(values=self.lista_tipos)
            self.combobox_tipo_doc.set('')
        finally:
            session.close()

    def _formatar_data_entrada(self, event):
        widget = event.widget
        texto = widget.get()
        numeros = ''.join(filter(str.isdigit, texto))

        novo_texto = ''
        for i, n in enumerate(numeros):
            if i == 2 or i == 4:
                novo_texto += '/'
            novo_texto += n
            if i >= 7:
                break

        pos = widget.index("insert")
        pos = min(pos, len(novo_texto))

        widget.delete(0, "end")
        widget.insert(0, novo_texto)

        if event.keysym.lower() != 'backspace':
            if pos in (3, 6):
                pos += 1
            widget.icursor(pos)

    def buscar_documentos(self):
        data_inicio_str = self.entrada_data_inicio.get().strip()
        data_fim_str = self.entrada_data_fim.get().strip()
        tipo_doc_str = self.combobox_tipo_doc.get().strip()

        data_inicio = None
        data_fim = None

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erro", "Data Início inválida. Use dd/mm/aaaa.")
                return

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erro", "Data Fim inválida. Use dd/mm/aaaa.")
                return

        if data_inicio and data_fim and data_fim < data_inicio:
            messagebox.showerror("Erro", "Data Fim não pode ser anterior à Data Início.")
            return

        if not data_inicio_str and not data_fim_str and not tipo_doc_str:
            messagebox.showwarning("Aviso", "Preencha pelo menos um campo para buscar.")
            return

        session: Session = SessionLocal()
        try:
            query = session.query(Documento, Caixa, Status, Localizacao) \
                .join(Caixa, Caixa.documento_id == Documento.id) \
                .join(Status, Caixa.status_id == Status.id) \
                .filter(Status.tipo != "Eliminado")\
                .join(Localizacao, Caixa.localizacao_id == Localizacao.id)
                

            if data_inicio:
                query = query.filter(Caixa.dt_arquivamento >= data_inicio)
            if data_fim:
                query = query.filter(Caixa.dt_arquivamento <= data_fim)
            if tipo_doc_str:
                query = query.filter(Documento.tp_doc == tipo_doc_str)

            resultados = query.all()
            self.resultados = resultados
            self.texto_resultado.delete("0.0", "end")

            if not resultados:
                self.texto_resultado.insert("end", "Nenhum documento encontrado.")
            else:
                for documento, caixa, status, localizacao in resultados:
                    self.texto_resultado.insert(
                        "end",
                        f"Documento: {documento.tp_doc}, Caixa: {caixa.id}, "
                        f"Status: {status.tipo}, "
                        f"Localização: Sala {localizacao.sala}, Prat. {localizacao.prateleira}, Col. {localizacao.coluna}\n"
                    )

        finally:
            session.close()

    def gerar_pdf(self):
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum dado para gerar PDF.")
            return

        nome_arquivo = "relatorio_documentos.pdf"
        downloads = Path.home() / "Downloads"
        caminho_completo = downloads / nome_arquivo

        try:
            c = canvas.Canvas(str(caminho_completo), pagesize=A4)
            largura, altura = A4

            # Cabeçalho
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(largura / 2, altura - 50, "ARQUIBOX - Relatório de Documentos")

            c.setFont("Helvetica", 10)
            c.drawRightString(largura - 50, altura - 70, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            total = len(self.resultados)
            c.drawString(50, altura - 90, f"Total de documentos: {total}")

            # Cabeçalhos
            col_doc = 50
            col_caixa = 200
            col_status = 260
            col_localizacao = 340

            c.setFont("Helvetica-Bold", 9)
            y_header = altura - 110
            c.drawString(col_doc, y_header, "DOCUMENTO")
            c.drawString(col_caixa, y_header, "CAIXA")
            c.drawString(col_status, y_header, "STATUS")
            c.drawString(col_localizacao, y_header, "LOCALIZAÇÃO")

            # Conteúdo
            y = altura - 130
            c.setFont("Helvetica", 8)
            line_height = 12

            for documento, caixa, status, localizacao in self.resultados:
                c.drawString(col_doc, y, str(documento.tp_doc))
                c.drawString(col_caixa, y, str(caixa.id))
                c.drawString(col_status, y, str(status.tipo))
                c.drawString(col_localizacao, y, f"S:{localizacao.sala} P:{localizacao.prateleira} C:{localizacao.coluna}")

                y -= line_height
                if y < 80:
                    c.showPage()
                    y = altura - 100
                    c.setFont("Helvetica", 8)

            c.save()
            messagebox.showinfo("Sucesso", f"PDF '{nome_arquivo}' gerado com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}")
