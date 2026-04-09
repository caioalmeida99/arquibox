import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import Session
from models.models import Status
from database.session import SessionLocal
from interface.permissao import verificar_permissao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CadastroStatusApp(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Status")
        self.state('zoomed')
        
        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 2:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return

        self.db = SessionLocal()

        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True)

        self.frame_campos = ctk.CTkFrame(self.frame_principal)
        self.frame_campos.pack(side="left", fill="y", padx=20, pady=20)

        self.label_tipo = ctk.CTkLabel(self.frame_campos, text="Status", anchor="w")
        self.label_tipo.pack(fill="x", pady=(0, 2))
        self.entry_tipo = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_tipo.pack(fill="x", pady=(0, 10))
     
        self.frame_botoes = ctk.CTkFrame(self.frame_campos)
        self.frame_botoes.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar", command=self.salvar_status)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        self.lista_status = ctk.CTkTextbox(self.frame_principal, height=6)
        self.lista_status.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.limpar_campos()
        self.atualizar_lista()

    def salvar_status(self):
            status_str = self.entry_tipo.get().strip()

            novo_status = Status(tipo=status_str)

            try:
                self.db.add(novo_status)
                self.db.commit()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", "Status salvo com sucesso!")
                self.limpar_campos()
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Erro ao salvar", str(e))

    def limpar_campos(self):
        self.entry_tipo.delete(0, "end")

    def atualizar_lista(self):
        self.lista_status.delete("0.0", "end")
        status = self.db.query(Status).all()
        for status in status:
            texto = f"ID: {status.id}, Tipo: {status.tipo}\n"
            self.lista_status.insert("end", texto)

if __name__ == "__main__":
    app = CadastroStatusApp()
    app.mainloop()