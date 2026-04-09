import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Documento
from database.session import SessionLocal
from interface.permissao import verificar_permissao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CadastroDocumentoApp(ctk.CTkToplevel):

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Documentos")
        self.state("zoomed")

        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 2:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return

        self.db = SessionLocal()

        self.db = SessionLocal()

        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True)

        self.frame_campos = ctk.CTkFrame(self.frame_principal)
        self.frame_campos.pack(side="left", fill="y", padx=20, pady=20)

        # Campo Tipo de Documento
        self.label_tipo = ctk.CTkLabel(self.frame_campos, text="Tipo de Documento", anchor="w")
        self.label_tipo.pack(fill="x", pady=(0, 2))
        self.entry_tipo = ctk.CTkEntry(self.frame_campos)
        self.entry_tipo.pack(fill="x", pady=(0, 10))

        # Campo Tempo de Arquivamento
        self.label_tempo = ctk.CTkLabel(self.frame_campos, text="Tempo de Arquivamento (anos)", anchor="w")
        self.label_tempo.pack(fill="x", pady=(0, 2))
        self.entry_tempo = ctk.CTkEntry(self.frame_campos)
        self.entry_tempo.pack(fill="x", pady=(0, 10))

        # Botões
        self.frame_botoes = ctk.CTkFrame(self.frame_campos)
        self.frame_botoes.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar", command=self.salvar_documento)
        self.btn_salvar.pack()

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        # Lista de Documentos
        self.lista_documentos = ctk.CTkTextbox(self.frame_principal, height=6)
        self.lista_documentos.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.limpar_campos()
        self.atualizar_lista()

    def salvar_documento(self):
        tipo = self.entry_tipo.get().strip()
        tempo_str = self.entry_tempo.get().strip()

        if not tipo or not tempo_str:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return

        try:
            tempo = int(tempo_str)
        except ValueError:
            messagebox.showerror("Erro", "Tempo de arquivamento deve ser um número inteiro.")
            return

        novo_documento = Documento(tp_doc=tipo, temp_arq=tempo)

        try:
            self.db.add(novo_documento)
            self.db.commit()
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Documento salvo com sucesso!")
            self.limpar_campos()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro ao salvar", str(e))

    def limpar_campos(self):
        self.entry_tipo.delete(0, "end")
        self.entry_tempo.delete(0, "end")

    def atualizar_lista(self):
        self.lista_documentos.delete("0.0", "end")
        documentos = self.db.query(Documento).all()
        for doc in documentos:
            linha = f"ID: {doc.id} | Tipo: {doc.tp_doc} | Tempo: {doc.temp_arq} anos\n"
            self.lista_documentos.insert("end", linha)

if __name__ == "__main__":
    app = CadastroDocumentoApp()
    app.mainloop()