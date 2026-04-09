'''import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Pessoa
from database.session import SessionLocal

# Aparência
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")  

class CadastroPessoaApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Pessoa")
        self.geometry("1024x768")
        self.db = SessionLocal()

    
        container = ctk.CTkFrame(self, corner_radius=15)
        container.pack(padx=40, pady=40, fill="both", expand=True)

        title = ctk.CTkLabel(container, text="Cadastro de Pessoa", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(10, 30))

        self.entry_nome = ctk.CTkEntry(container, placeholder_text="Nome", width=300, height=40)
        self.entry_nome.pack(pady=10)

        btn_salvar = ctk.CTkButton(container, text="Salvar", command=self._salvar_pessoa, width=120, height=40)
        btn_salvar.pack(pady=20)

    def _salvar_pessoa(self):
        nome = self.entry_nome.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Preencha o nome!")
            return

        try:
            with SessionLocal() as session:
                pessoa = Pessoa(nome=nome)
                session.add(pessoa)
                session.commit()

            messagebox.showinfo("Sucesso", "Pessoa cadastrada com sucesso!")
            self.entry_nome.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

if __name__ == "__main__":
    app = CadastroPessoaApp()
    app.mainloop()
'''