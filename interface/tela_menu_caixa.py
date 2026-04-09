import customtkinter as ctk
from sqlalchemy.orm import Session
from database.session import SessionLocal
from interface.tela_cadastro_caixa import CadastroCaixaApp
from interface.tela_editar_caixa import EditarCaixaApp
from interface.tela_menu_relatorios import TelaRelatoriosMenu
from interface.tela_alerta_caixa import AlertaCaixaApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelaMenuCaixa(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Menu Caixa")
        self.state("zoomed")  
        self.db = SessionLocal()
        self.caixa_selecionada = None

        # Frame principal
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.pack(fill="both", expand=True)

        # Frame central
        self.frame_central = ctk.CTkFrame(self.frame_principal, corner_radius=15)
        self.frame_central.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_central,
            text="📦 Menu de Caixas",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 15))

        # Botão - Cadastrar Caixa
        self.botao_abrir_cadastro = ctk.CTkButton(
            self.frame_central,
            text="Cadastrar Caixa",
            width=250,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.abrir_cadastro_caixa
        )
        self.botao_abrir_cadastro.pack(pady=10)

        # Botão - Editar Caixa
        self.botao_abrir_editar_caixa = ctk.CTkButton(
            self.frame_central,
            text="Editar Caixa",
            width=250,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.abrir_editar_caixa
        )
        self.botao_abrir_editar_caixa.pack(pady=10)

        # Botão - Alerta Caixa
        self.botao_abrir_alerta_caixa = ctk.CTkButton(
            self.frame_central,
            text="Alerta Caixa",
            width=250,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.abrir_alerta_caixa 
        )
        self.botao_abrir_alerta_caixa.pack(pady=10)

    def abrir_cadastro_caixa(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroCaixaApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_editar_caixa(self):
        if not hasattr(self, 'janela_edicao') or not self.janela_edicao.winfo_exists():
            self.janela_edicao = EditarCaixaApp(self)
        else:
            self.janela_edicao.focus()

    def abrir_alerta_caixa(self):
        if not hasattr(self, 'janela_alerta') or not self.janela_alerta.winfo_exists():
            self.janela_alerta = AlertaCaixaApp(self)
        else:
            self.janela_alerta.focus()


if __name__ == "__main__":
    app = TelaMenuCaixa()
    app.mainloop()
