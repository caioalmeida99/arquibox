import customtkinter as ctk
from tkinter import messagebox, Scrollbar, VERTICAL, RIGHT, Y
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, desc
from database.session import SessionLocal
from models.models import Caixa, Documento, Status, Localizacao, Funcionario, AcessoCaixa
from database.session import SessionLocal
from interface.permissao import verificar_permissao
 
 
class RelatorioCaixas(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Relatório de Caixas")
        self.state("zoomed")

        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 1:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return
        
        self.resizable(True, True)
        self.resultados = []
        self.lista_tipos_documentos = []
        self.tipo_consulta_atual = ""
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
        # Consultas Avançadas
        label_avancada = ctk.CTkLabel(frame, text="Consultas Avançadas:")
        label_avancada.pack(anchor="w", pady=(0, 5))
        self.combobox_consulta_avancada = ctk.CTkComboBox(
            frame,
            values=[
                " ",
                "Últimas caixas por tipo de documento",
                "Caixas com mais de 5 anos",
                "Quantidade de caixas por status e tipo",
                "Acessos recentes por funcionário"
            ]
        )
        self.combobox_consulta_avancada.pack(anchor="w", pady=(0, 15))
        # Botões
        btn_buscar = ctk.CTkButton(frame, text="Buscar", width=100, command=self.buscar_caixas)
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
            self.lista_tipos_documentos = [''] + [tp[0] for tp in tipos if tp[0]]
            self.combobox_tipo_doc.configure(values=self.lista_tipos_documentos)
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
        pos = min(widget.index("insert"), len(novo_texto))
        widget.delete(0, "end")
        widget.insert(0, novo_texto)
        if event.keysym.lower() != 'backspace':
            if pos in (3, 6):
                pos += 1
            widget.icursor(pos)

    def buscar_caixas(self):
        self.tipo_consulta_atual = self.combobox_consulta_avancada.get().strip()
        data_inicio_str = self.entrada_data_inicio.get().strip()
        data_fim_str = self.entrada_data_fim.get().strip()
        tipo_doc_str = self.combobox_tipo_doc.get().strip()

        data_inicio = None
        data_fim = None
        # Conversão de datas
        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erro", "Formato de Data Início inválido.")
                return
        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erro", "Formato de Data Fim inválido.")
                return
        if data_inicio and data_fim and data_fim < data_inicio:
            messagebox.showerror("Erro", "Data Fim não pode ser anterior à Data Início.")
            return
        session: Session = SessionLocal()
        try:
            self.texto_resultado.delete("0.0", "end")

            if self.tipo_consulta_atual == "Últimas caixas por tipo de documento":
                subq = (
                    session.query(
                        Caixa.id.label("caixa_id"),
                        Documento.tp_doc.label("tp_doc"),
                        Caixa.dt_arquivamento.label("dt_arquivamento"),
                        Status.tipo.label("status_tipo"),
                        Localizacao.sala.label("local_sala"),
                        Localizacao.prateleira.label("local_prateleira"),
                        Localizacao.coluna.label("local_coluna"),
                        func.row_number().over(
                            partition_by=Documento.tp_doc,
                            order_by=desc(Caixa.dt_arquivamento)
                        ).label("rn")
                    )
                    .join(Documento, Caixa.documento_id == Documento.id)
                    .join(Status, Caixa.status_id == Status.id)
                    .join(Localizacao, Caixa.localizacao_id == Localizacao.id)
                    .filter(Status.tipo != "Eliminado")
                ).subquery()
                query = session.query(subq).filter(subq.c.rn == 1)
                self.resultados = query.all()
                if not self.resultados:
                    self.texto_resultado.insert("end", "Nenhum resultado encontrado.")
                else:
                    for row in self.resultados:
                        localizacao_str = f"Sala: {row.local_sala}, Prateleira: {row.local_prateleira}, Coluna: {row.local_coluna}"
                        linha = f"{row.caixa_id} | {row.tp_doc or ''} | {row.dt_arquivamento.strftime('%d/%m/%Y') if row.dt_arquivamento else ''} | {row.status_tipo or ''} | {localizacao_str}\n"
                        self.texto_resultado.insert("end", linha)
                return

            elif self.tipo_consulta_atual == "Caixas com mais de 5 anos":
                data_limite = datetime.now().date() - timedelta(days=5*365)
                query = (
                    session.query(Caixa, Documento, Status, Localizacao)
                    .join(Documento, Caixa.documento_id == Documento.id)
                    .join(Status, Caixa.status_id == Status.id)
                    .join(Localizacao, Caixa.localizacao_id == Localizacao.id)
                    .filter(Caixa.dt_arquivamento <= data_limite)
                    .filter(Status.tipo !="Eliminado")
                )
                self.resultados = query.all()
                if not self.resultados:
                    self.texto_resultado.insert("end", "Nenhum resultado encontrado.")
                else:
                    for row in self.resultados:
                        caixa, documento, status, localizacao = row
                        periodo_inc_str = caixa.periodo_inc.strftime('%d/%m/%Y') if caixa.periodo_inc else 'N/A'
                        periodo_fim_str = caixa.periodo_fim.strftime('%d/%m/%Y') if caixa.periodo_fim else 'N/A'
                        loc_str = f"Sala: {localizacao.sala}, Prateleira: {localizacao.prateleira}, Coluna: {localizacao.coluna}"
                        linha = (
                            f"{caixa.id} | {caixa.dt_arquivamento.strftime('%d/%m/%Y')} | {periodo_inc_str} | "
                            f"{periodo_fim_str} | {documento.tp_doc or ''} | {status.tipo or ''} | {loc_str}\n"
                        )
                        self.texto_resultado.insert("end", linha)
                return

            elif self.tipo_consulta_atual == "Quantidade de caixas por status e tipo":
                query = (
                    session.query(
                        Documento.tp_doc,
                        Status.tipo,
                        func.count(Caixa.id).label("total_caixas")
                    )
                    .join(Documento, Caixa.documento_id == Documento.id)
                    .join(Status, Caixa.status_id == Status.id)
                    .group_by(Documento.tp_doc, Status.tipo)
                    .order_by(func.count(Caixa.id).desc())
                    .filter(Status.tipo != "Eliminado")
                )
                self.resultados = query.all()
                if not self.resultados:
                    self.texto_resultado.insert("end", "Nenhum resultado encontrado.")
                else:
                    for row in self.resultados:
                        linha = f"{row.tp_doc or ''} | {row.tipo or ''} | {row.total_caixas}\n"
                        self.texto_resultado.insert("end", linha)
                return

            elif self.tipo_consulta_atual == "Acessos recentes por funcionário":
                data_limite = datetime.now().date() - timedelta(days=30)
                query = (
                    session.query(
                        AcessoCaixa.dt_acesso,
                        Funcionario.nome.label("funcionario_nome"),
                        Funcionario.cargo.label("funcionario_cargo"),
                        Caixa.id.label("caixa_id"),
                        Documento.tp_doc.label("tipo_documento"),
                        Status.tipo.label("status_caixa"),
                        Localizacao.sala,
                        Localizacao.prateleira,
                        Localizacao.coluna
                    )
                    .join(Funcionario, AcessoCaixa.funcionario_matricula == Funcionario.matricula)
                    .join(Caixa, AcessoCaixa.caixa_id == Caixa.id)
                    .join(Documento, Caixa.documento_id == Documento.id)
                    .join(Status, Caixa.status_id == Status.id)
                    .join(Localizacao, Caixa.localizacao_id == Localizacao.id)
                    .filter(AcessoCaixa.dt_acesso >= data_limite)
                    .filter(Status.tipo != "Eliminado")
                    .order_by(AcessoCaixa.dt_acesso.desc())
                )
                self.resultados = query.all()
                if not self.resultados:
                    self.texto_resultado.insert("end", "Nenhum acesso recente encontrado.")
                else:
                    for row in self.resultados:
                        loc_str = f"Sala: {row.sala}, Prateleira: {row.prateleira}, Coluna: {row.coluna}"
                        linha = (
                            f"{row.dt_acesso.strftime('%d/%m/%Y %H:%M')} | {row.funcionario_nome} ({row.funcionario_cargo}) | "
                            f"Caixa {row.caixa_id} | {row.tipo_documento} | {row.status_caixa} | {loc_str}\n"
                        )
                        self.texto_resultado.insert("end", linha)
                return
            
            else:
                if not data_inicio_str and not data_fim_str and not tipo_doc_str:
                    messagebox.showwarning("Aviso", "Preencha pelo menos um campo.")
                    return
                query = (
                    session.query(Caixa, Documento, Status, Localizacao)
                    .join(Documento, Caixa.documento_id == Documento.id)
                    .join(Status, Caixa.status_id == Status.id)
                    .join(Localizacao, Caixa.localizacao_id == Localizacao.id)
                    .filter(Status.tipo !="Eliminado")
                )
                if data_inicio:
                    query = query.filter(Caixa.dt_arquivamento >= data_inicio)
                if data_fim:
                    query = query.filter(Caixa.dt_arquivamento <= data_fim)
                if tipo_doc_str:
                    query = query.filter(Documento.tp_doc == tipo_doc_str)
                self.resultados = query.all()
                if not self.resultados:
                    self.texto_resultado.insert("end", "Nenhum resultado encontrado.")
                else:
                    for row in self.resultados:
                        caixa, documento, status, localizacao = row
                        periodo_inc_str = caixa.periodo_inc.strftime('%d/%m/%Y') if caixa.periodo_inc else 'N/A'
                        periodo_fim_str = caixa.periodo_fim.strftime('%d/%m/%Y') if caixa.periodo_fim else 'N/A'
                        loc_str = f"Sala: {localizacao.sala}, Prateleira: {localizacao.prateleira}, Coluna: {localizacao.coluna}"
                        linha = (
                            f"{caixa.id} | {caixa.dt_arquivamento.strftime('%d/%m/%Y')} | {periodo_inc_str} | "
                            f"{periodo_fim_str} | {documento.tp_doc or ''} | {status.tipo or ''} | {loc_str}\n"
                        )
                        self.texto_resultado.insert("end", linha)
        finally:
            session.close()

    def gerar_pdf(self):
        def quebrar_texto(texto, largura_coluna):
            max_chars = int(largura_coluna / 4.8)
            linhas = []
            while texto:
                linhas.append(texto[:max_chars])
                texto = texto[max_chars:]
            return linhas

        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum dado para gerar PDF.")
            return
        nome_arquivo = "relatorio_caixas.pdf"
        downloads = Path.home() / "Downloads"
        caminho_completo_arquivo = downloads / nome_arquivo

        try:
            c = canvas.Canvas(str(caminho_completo_arquivo), pagesize=A4)
            largura, altura = A4
            margem_esquerda = 50
            margem_direita = 50
            largura_util = largura - margem_esquerda - margem_direita
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(largura / 2, altura - 50, "ARQUIBOX - Relatório de Caixas")
            c.setFont("Helvetica", 10)
            c.drawRightString(largura - 50, altura - 70, datetime.now().strftime("%d/%m/%Y %H:%M"))
            y = altura - 90
            c.setFont("Helvetica-Bold", 10)
            # Cabeçalhos e larguras (ajustadas para caber na página)
            if self.tipo_consulta_atual == "Últimas caixas por tipo de documento":
                cabecalho = ["Caixa ID", "Tipo Documento", "Dt. Arq.", "Status", "Localização"]
                larguras = [60, 100, 70, 70, 160]
            elif self.tipo_consulta_atual == "Caixas com mais de 5 anos":
                cabecalho = ["Código", "Arq.", "Período Inc", "Período Fim", "Doc.", "Status", "Localização"]
                larguras = [50, 70, 70, 60, 80, 60, 90]
            elif self.tipo_consulta_atual == "Quantidade de caixas por status e tipo":
                cabecalho = ["Tipo Doc.", "Status", "Total Caixas"]
                larguras = [180, 150, 80]
            elif self.tipo_consulta_atual == "Acessos recentes por funcionário":
                cabecalho = ["Dt. Acesso", "Funcionário", "Cargo", "Caixa ID", "Tipo Doc.", "Status", "Localização"]
                # ajustado para 7 colunas
                larguras = [80, 110, 60, 50, 70, 60, 60]
            else:
                cabecalho = ["Código", "Arq.", "Período Inc", "Período Fim", "Documento", "Status", "Localização"]
                larguras = [50, 70, 70, 60, 80, 60, 90]

            # desenha cabeçalho
            x = margem_esquerda
            for i, coluna in enumerate(cabecalho):
                c.drawString(x, y, coluna)
                x += larguras[i]
            y -= 18
            c.setFont("Helvetica", 8)
            c.line(margem_esquerda, y + 10, largura - margem_direita, y + 10)

            for row in self.resultados:
                if y < 80:
                    c.showPage()
                    y = altura - 50
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(largura / 2, altura - 50, "ARQUIBOX - Relatório de Caixas")
                    y -= 40
                    c.setFont("Helvetica-Bold", 10)
                    x = margem_esquerda
                    for i, coluna in enumerate(cabecalho):
                        c.drawString(x, y, coluna)
                        x += larguras[i]
                    y -= 18
                    c.setFont("Helvetica", 8)
                    c.line(margem_esquerda, y + 10, largura - margem_direita, y + 10)
                x = margem_esquerda
                if self.tipo_consulta_atual == "Últimas caixas por tipo de documento":
                    localizacao_str = f"Sala: {row.local_sala}, Prateleira: {row.local_prateleira}, Coluna: {row.local_coluna}"
                    valores = [
                        str(row.caixa_id),
                        row.tp_doc or '',
                        row.dt_arquivamento.strftime('%d/%m/%Y') if row.dt_arquivamento else '',
                        row.status_tipo or '',
                        localizacao_str
                    ]
                elif self.tipo_consulta_atual == "Caixas com mais de 5 anos":
                    caixa, documento, status, localizacao = row
                    periodo_inc_str = caixa.periodo_inc.strftime('%d/%m/%Y') if caixa.periodo_inc else 'N/A'
                    periodo_fim_str = caixa.periodo_fim.strftime('%d/%m/%Y') if caixa.periodo_fim else 'N/A'
                    localizacao_str = f"Sala: {localizacao.sala}, Prateleira: {localizacao.prateleira}, Coluna: {localizacao.coluna}"
                    valores = [
                        str(caixa.id),
                        caixa.dt_arquivamento.strftime('%d/%m/%Y') if caixa.dt_arquivamento else '',
                        periodo_inc_str,
                        periodo_fim_str,
                        documento.tp_doc or '',
                        status.tipo or '',
                        localizacao_str
                    ]
                elif self.tipo_consulta_atual == "Quantidade de caixas por status e tipo":
                    valores = [
                        row.tp_doc or '',
                        row.tipo or '',
                        str(row.total_caixas)
                    ]
                elif self.tipo_consulta_atual == "Acessos recentes por funcionário":
                    localizacao_str = f"Sala: {row.sala}, Prateleira: {row.prateleira}, Coluna: {row.coluna}"
                    valores = [
                        row.dt_acesso.strftime('%d/%m/%Y %H:%M') if row.dt_acesso else '',
                        row.funcionario_nome or '',
                        row.funcionario_cargo or '',
                        str(row.caixa_id),
                        row.tipo_documento or '',
                        row.status_caixa or '',
                        localizacao_str
                    ]
                else:
                    caixa, documento, status, localizacao = row
                    periodo_inc_str = caixa.periodo_inc.strftime('%d/%m/%Y') if caixa.periodo_inc else 'N/A'
                    periodo_fim_str = caixa.periodo_fim.strftime('%d/%m/%Y') if caixa.periodo_fim else 'N/A'
                    localizacao_str = f"Sala: {localizacao.sala}, Prateleira: {localizacao.prateleira}, Coluna: {localizacao.coluna}"
                    valores = [
                        str(caixa.id),
                        caixa.dt_arquivamento.strftime('%d/%m/%Y') if caixa.dt_arquivamento else '',
                        periodo_inc_str,
                        periodo_fim_str,
                        documento.tp_doc or '',
                        status.tipo or '',
                        localizacao_str
                    ]

                altura_linha = 0
                linhas_por_coluna = []

                for i, val in enumerate(valores):
                    linhas = quebrar_texto(val, larguras[i])
                    linhas_por_coluna.append(linhas)
                    altura_linha = max(altura_linha, len(linhas))

                for linha_idx in range(altura_linha):
                    x = margem_esquerda
                    for i, linhas in enumerate(linhas_por_coluna):
                        texto = linhas[linha_idx] if linha_idx < len(linhas) else ''
                        c.drawString(x, y, texto)
                        x += larguras[i]
                    y -= 10

            c.save()
            messagebox.showinfo("Sucesso", f"PDF salvo em {caminho_completo_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
