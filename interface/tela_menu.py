import customtkinter as ctk
from database.session import SessionLocal
from interface.tela_cadastro_departamento import CadastroDepartamentoApp
from interface.tela_cadastro_documento import CadastroDocumentoApp
from interface.tela_cadastro_funcionario import CadastroFuncionarioApp
from interface.tela_cadastro_localizacao import CadastroLocalizacaoApp
from interface.tela_cadastro_status import CadastroStatusApp
from interface.tela_menu_caixa import TelaMenuCaixa
from interface.tela_menu_relatorios import TelaRelatoriosMenu

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelaMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arquibox - Arquivamento Inteligente")
        self.state("zoomed")  
        self.db = SessionLocal()
        
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.pack(fill="both", expand=True)
       
        self.frame_central = ctk.CTkFrame(self.frame_principal, corner_radius=15)
        self.frame_central.place(relx=0.5, rely=0.5, anchor="center")

        
        self.label_titulo = ctk.CTkLabel(
            self.frame_central,
            text="📂 Menu Principal",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 20))
        
        botoes = [
            ("📦 Menu Caixa", self.abrir_cadastro_caixa),
            ("🏢 Cadastrar Departamento", self.abrir_cadastro_departamento),
            ("📄 Cadastrar Documentos", self.abrir_cadastro_documentos),
            ("👤 Cadastrar Funcionários", self.abrir_cadastro_funcionario),
            ("📍 Cadastrar Localização", self.abrir_cadastro_localizacao),
            ("✅ Cadastrar Status", self.abrir_cadastro_status),
            ("📊 Relatórios", self.abrir_relatorios)
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                self.frame_central,
                text=texto,
                width=300,
                height=40,
                font=ctk.CTkFont(size=15, weight="bold"),
                command=comando
            ).pack(pady=10)

    
    def abrir_cadastro_caixa(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = TelaMenuCaixa(self)
        else:
            self.janela_cadastro.focus()

    def abrir_cadastro_departamento(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroDepartamentoApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_cadastro_documentos(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroDocumentoApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_cadastro_funcionario(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroFuncionarioApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_cadastro_localizacao(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroLocalizacaoApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_cadastro_status(self):
        if not hasattr(self, 'janela_cadastro') or not self.janela_cadastro.winfo_exists():
            self.janela_cadastro = CadastroStatusApp(self)
        else:
            self.janela_cadastro.focus()

    def abrir_relatorios(self):
        if not hasattr(self, 'janela_relatorios') or not self.janela_relatorios.winfo_exists():
            self.janela_relatorios = TelaRelatoriosMenu(self)
        else:
            self.janela_relatorios.focus()

if __name__ == "__main__":
    app = TelaMenu()
    app.mainloop()
