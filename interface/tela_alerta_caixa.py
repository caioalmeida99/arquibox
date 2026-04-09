import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.models import Caixa, Status, Documento
from database.session import SessionLocal
from interface.permissao import verificar_permissao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AlertaCaixaApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Alerta de Caixa")
        self.state('zoomed')
        self.configure(bg="#000000") 

        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 2:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return

        self.db = SessionLocal()
        self.create_widgets()
        self.carregar_caixas_alerta()

    def create_widgets(self):
        titulo = ctk.CTkLabel(
            self,
            text="Caixas vencidas ou com vencimento em até 6 meses",
            font=("Arial", 20, "bold"),
            text_color="white",
        )
        titulo.pack(pady=20)

        # Frame da tabela
        frame_tabela = ctk.CTkFrame(self, fg_color="#000000")
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=10)

        colunas = ("id Caixa", "tipo_documento", "dt_previsao", "status")

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background="#000000",
            foreground="white",
            fieldbackground="#000000",
            rowheight=28,
            font=("Segoe UI", 12)
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            foreground="white",
            background="#000000"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#222222")],
            foreground=[("selected", "white")]
        )

        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=20, style="Custom.Treeview")

        # Cabeçalhos
        self.tree.heading("id Caixa", text="ID Caixa")
        self.tree.heading("tipo_documento", text="Tipo de Documento")
        self.tree.heading("dt_previsao", text="Data Previsão Exclusão")
        self.tree.heading("status", text="Status")

        # Colunas
        self.tree.column("id Caixa", width=100, anchor="center")
        self.tree.column("tipo_documento", width=400, anchor="center")  # centralizado
        self.tree.column("dt_previsao", width=180, anchor="center")
        self.tree.column("status", width=150, anchor="center")

        vsb = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        frame_tabela.rowconfigure(0, weight=1)
        frame_tabela.columnconfigure(0, weight=1)

        btn_atualizar = ctk.CTkButton(
            self,
            text="Atualizar Lista",
            text_color="white",
            fg_color="#3380F3",
            hover_color="#3380F3",
            command=self.carregar_caixas_alerta
        )
        btn_atualizar.pack(pady=10)

    def carregar_caixas_alerta(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        hoje = datetime.now()
        limite = hoje + timedelta(days=180)

        # Consulta caixas com dt_previsao até 6 meses à frente e status arquivado
        caixas = (
            self.db.query(Caixa, Documento.tp_doc.label("tipo_doc"), Status.tipo.label("status_tipo"))
            .join(Status)
            .join(Documento)
            .filter(Status.tipo == "Arquivado")
            .filter(Caixa.dt_previsao != None)
            .filter(Caixa.dt_previsao <= limite)
            .all()
        )

        if not caixas:
            self.tree.insert("", "end", values=("—", "Nenhuma caixa encontrada", "—", "—"))
            return

        for caixa, tipo_doc, status_tipo in caixas:
            dt_previsao_str = caixa.dt_previsao.strftime("%d/%m/%Y")

            # Cor da linha
            if caixa.dt_previsao < hoje:
                fg_color = "red"         # Vencida
            elif caixa.dt_previsao <= hoje + timedelta(days=180):
                fg_color = "yellow"      # Próxima a vencer
            else:
                fg_color = "white"       # Normal

            self.tree.insert("", "end", values=(
                caixa.id,
                tipo_doc,
                dt_previsao_str,
                status_tipo
            ), tags=(fg_color,))

        # Configura tags para cores
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("yellow", foreground="yellow")
        self.tree.tag_configure("white", foreground="white")

    def destroy(self):
        if hasattr(self, "db"):
            self.db.close()
        super().destroy()


if __name__ == "__main__":
    app = AlertaCaixaApp()
    app.mainloop()
