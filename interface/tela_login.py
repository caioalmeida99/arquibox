import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Funcionario
from database.session import SessionLocal
from database.firebase_config import auth
from interface.tela_menu import TelaMenu
import database.session

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arquibox - LOGIN")
        self.state('zoomed')  # Tela cheia
        self.db = SessionLocal()

        # Frame principal que ocupa toda a tela
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.pack(fill="both", expand=True)

        # Frame centralizado (formulário)
        self.frame_central = ctk.CTkFrame(self.frame_principal, corner_radius=15)
        self.frame_central.place(relx=0.5, rely=0.5, anchor="center")  # centraliza

        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_central,
            text="🔐 Login no Arquibox",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 10))

        # Linha separadora
        self.linha = ctk.CTkFrame(self.frame_central, height=2, fg_color="#2b2b2b")
        self.linha.pack(fill="x", padx=20, pady=(0, 20))

        # Campo Matrícula
        self.entry_matricula = ctk.CTkEntry(
            self.frame_central,
            placeholder_text="Digite sua matrícula",
            height=40,
            width=300,
            font=ctk.CTkFont(size=14)
        )
        self.entry_matricula.pack(pady=10, padx=20)

        # Campo Senha
        self.entry_senha = ctk.CTkEntry(
            self.frame_central,
            placeholder_text="Digite sua senha",
            show="*",
            height=40,
            width=300,
            font=ctk.CTkFont(size=14)
        )
        self.entry_senha.pack(pady=10, padx=20)

        # Botão Login
        self.botao_login = ctk.CTkButton(
            self.frame_central,
            text="Entrar",
            height=40,
            width=300,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.realizar_login
        )
        self.botao_login.pack(pady=20, padx=20)

    def realizar_login(self):
        matricula = self.entry_matricula.get()
        senha = self.entry_senha.get()

        if not matricula or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        try:
            funcionario = self.db.query(Funcionario).filter_by(matricula=int(matricula)).first()

            if not funcionario:
                messagebox.showerror("Erro", "Funcionário não encontrado.")
                return

            email = funcionario.email

            try:
                auth.sign_in_with_email_and_password(email, senha)
                messagebox.showinfo("Sucesso", f"Login realizado com sucesso!\nUsuário: {email}")
                Session.matricula_logada = int(matricula)
                self.destroy()
                menu = TelaMenu()
                menu.mainloop()

            except Exception:
                messagebox.showerror("Erro de autenticação", "Email ou senha incorretos.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar login: {e}")


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
