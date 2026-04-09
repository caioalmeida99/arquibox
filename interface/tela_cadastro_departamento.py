import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Departamento
from database.session import SessionLocal
from interface.permissao import verificar_permissao

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class CadastroDepartamentoApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro Departamento")
        self.state('zoomed')
        
        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 3:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return

        self.db = SessionLocal()

    
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(container, text="Cadastro de Departamento", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(0, 20))

        self.entry_nome = ctk.CTkEntry(container, placeholder_text="Nome do Departamento")
        self.entry_nome.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        btn_salvar = ctk.CTkButton(container, text="Salvar", command=self._salvar_departamento)
        btn_salvar.grid(row=2, column=0, pady=20)

        container.columnconfigure(0, weight=1)

    def _salvar_departamento(self):
        nome = self.entry_nome.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Preencha o nome!")
            return

        with SessionLocal() as session:
            departamento = Departamento(nome=nome)
            session.add(departamento)
            session.commit()

        messagebox.showinfo("Sucesso", "Departamento cadastrado com sucesso!")
        self.entry_nome.delete(0, "end")

if __name__ == "__main__":
    app = CadastroDepartamentoApp()
    app.mainloop()