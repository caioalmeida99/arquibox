import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Localizacao
from database.session import SessionLocal
from interface.permissao import verificar_permissao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CadastroLocalizacaoApp(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Localizacoes")
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

        # Campo Sala
        self.label_sala = ctk.CTkLabel(self.frame_campos, text="Sala", anchor="w")
        self.label_sala.pack(fill="x", pady=(0, 2))
        self.entry_sala = ctk.CTkEntry(self.frame_campos)
        self.entry_sala.pack(fill="x", pady=(0, 10))

        # Campo Prateleira
        self.label_prateleira = ctk.CTkLabel(self.frame_campos, text="Prateleira", anchor="w")
        self.label_prateleira.pack(fill="x", pady=(0, 2))
        self.entry_prateleira = ctk.CTkEntry(self.frame_campos)
        self.entry_prateleira.pack(fill="x", pady=(0, 10))

        # Campo Coluna
        self.label_coluna = ctk.CTkLabel(self.frame_campos, text="Coluna", anchor="w")
        self.label_coluna.pack(fill="x", pady=(0, 2))
        self.entry_coluna = ctk.CTkEntry(self.frame_campos)
        self.entry_coluna.pack(fill="x", pady=(0, 10))

        # Botões
        self.frame_botoes = ctk.CTkFrame(self.frame_campos)
        self.frame_botoes.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar", command=self.salvar_localizacao)
        self.btn_salvar.pack()

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        # Lista de Localizações
        self.lista_localizacao = ctk.CTkTextbox(self.frame_principal, height=6)
        self.lista_localizacao.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.limpar_campos()
        self.atualizar_lista()

    def salvar_localizacao(self):
        sala = self.entry_sala.get().strip()
        prateleira = self.entry_prateleira.get().strip()
        coluna = self.entry_coluna.get().strip()

        if not sala or not prateleira or not coluna:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return

        nova_localizacao = Localizacao(sala=sala, prateleira=prateleira, coluna=coluna)

        try:
            self.db.add(nova_localizacao)
            self.db.commit()
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Localização salva com sucesso!")
            self.limpar_campos()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro ao salvar", str(e))

    def limpar_campos(self):
        self.entry_sala.delete(0, "end")
        self.entry_prateleira.delete(0, "end")
        self.entry_coluna.delete(0, "end")

    def atualizar_lista(self):
        self.lista_localizacao.delete("0.0", "end")
        localizacoes = self.db.query(Localizacao).all()
        for loc in localizacoes:
            linha = f"ID: {loc.id} | Sala: {loc.sala} | Prateleira: {loc.prateleira} | Coluna: {loc.coluna}\n"
            self.lista_localizacao.insert("end", linha)