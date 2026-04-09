import customtkinter as ctk
from tkinter import messagebox
from interface.tela_relatorio_caixa import RelatorioCaixas
from interface.tela_relatorio_localizacoes import RelatorioLocalizacoes
from interface.tela_relatorio_documentos import RelatorioDocumentos

class TelaRelatoriosMenu(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Menu de Relatórios")
        self.state('zoomed')

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        self.frame_fundo = ctk.CTkFrame(self.container, fg_color="#2F2F2F", corner_radius=10)
        self.frame_fundo.pack(padx=10, pady=10, anchor="w")

        self.label_titulo = ctk.CTkLabel(self.frame_fundo, text="Relatórios", font=("Arial", 22), text_color="white")
        self.label_titulo.pack(pady=(10, 15), padx=20, anchor="w")

        largura_botoes = 250

        self.btn_caixas = ctk.CTkButton(self.frame_fundo, text="Relatório de Caixas", width=largura_botoes, command=self.abrir_relatorio_caixas)
        self.btn_caixas.pack(pady=5, padx=20, anchor="w")

        self.btn_localizacoes = ctk.CTkButton(self.frame_fundo, text="Relatório de Localizações", width=largura_botoes, command=self.abrir_relatorio_localizacoes)
        self.btn_localizacoes.pack(pady=5, padx=20, anchor="w")

        self.btn_documentos = ctk.CTkButton(self.frame_fundo, text="Relatório de Documentos", width=largura_botoes, command=self.abrir_relatorio_documentos)
        self.btn_documentos.pack(pady=5, padx=20, anchor="w")

    def abrir_relatorio_caixas(self):
        janela_relatorio = RelatorioCaixas(self)
        janela_relatorio.grab_set()

    def abrir_relatorio_localizacoes(self):
        janela_relatorio = RelatorioLocalizacoes(self)
        janela_relatorio.grab_set()

    def abrir_relatorio_documentos(self):
        janela_relatorio = RelatorioDocumentos(self)
        janela_relatorio.grab_set()

