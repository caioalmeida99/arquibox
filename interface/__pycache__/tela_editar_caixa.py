import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import Session
from models.models import Caixa, Status, Documento, Localizacao
from database.session import SessionLocal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class EditarCaixaApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro Caixa")
        self.geometry("1024x768")
        self.db = SessionLocal()
        self.caixa_selecionada = None

        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True)

        self.frame_campos = ctk.CTkFrame(self.frame_principal)
        self.frame_campos.pack(side="left", fill="y", padx=20, pady=20)

        self.documento_options = self.get_documento_options()

        # Campo pesquisa caixa
        self.label_ps_caixa = ctk.CTkLabel(self.frame_campos, text="Pesquisar Caixa (ID):", anchor="w")
        self.label_ps_caixa.pack(fill="x", pady=(0, 2))
        self.entry_ps_caixa = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_ps_caixa.pack(fill="x", pady=(0, 10))
        self.entry_ps_caixa.bind("<Return>", self.buscar_caixa)

        # Campo Início do período
        self.label_periodo_inc = ctk.CTkLabel(self.frame_campos, text="Data início do período (DD/MM/YYYY):", anchor="w")
        self.label_periodo_inc.pack(fill="x", pady=(0, 2))
        self.entry_periodo_inc = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_periodo_inc.pack(fill="x", pady=(0, 10))
        self.entry_periodo_inc.bind("<KeyRelease>", self.formatar_data)

        # Campo Fim do período
        self.label_periodo_fim = ctk.CTkLabel(self.frame_campos, text="Data final do período (DD/MM/YYYY):", anchor="w")
        self.label_periodo_fim.pack(fill="x", pady=(0, 2))
        self.entry_periodo_fim = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_periodo_fim.pack(fill="x", pady=(0, 10))
        self.entry_periodo_fim.bind("<KeyRelease>", self.formatar_data)

        # Campo Data Previsão Exclusão
        self.label_dt_previsao = ctk.CTkLabel(self.frame_campos, text="Data Prevista para Exclusão (DD/MM/YYYY):", anchor="w")
        self.label_dt_previsao.pack(fill="x", pady=(0, 2))
        self.entry_dt_previsao = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_dt_previsao.pack(fill="x", pady=(0, 10))
        self.entry_dt_previsao.bind("<KeyRelease>", self.formatar_data)

        # Campo Data Arquivamento
        self.label_dt_arquivamento = ctk.CTkLabel(self.frame_campos, text="Data Arquivamento (DD/MM/YYYY):", anchor="w")
        self.label_dt_arquivamento.pack(fill="x", pady=(0, 2))
        self.entry_dt_arquivamento = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_dt_arquivamento.pack(fill="x", pady=(0, 10))
        self.entry_dt_arquivamento.bind("<KeyRelease>", self.formatar_data)

        # Campo Status
        self.label_status = ctk.CTkLabel(self.frame_campos, text="Status:", anchor="w")
        self.label_status.pack(fill="x", pady=(10, 2))
        self.status_options = self.get_status_options()
        self.combo_status = ctk.CTkComboBox(self.frame_campos, values=self.status_options, state="readonly")
        self.combo_status.pack(fill="x", pady=(0, 10))

        # Campo Localização
        self.label_localizacao = ctk.CTkLabel(self.frame_campos, text="Localização", anchor="w")
        self.label_localizacao.pack(fill="x", pady=(0, 2))
        self.entry_localizacao = ctk.CTkEntry(self.frame_campos)
        self.entry_localizacao.pack(fill="x", pady=(0, 10))

        # Campo Tipo de Documento
        self.label_documento = ctk.CTkLabel(self.frame_campos, text="Tipo de Documento:", anchor="w")
        self.label_documento.pack(fill="x", pady=(10, 2))
        self.combo_documento = ctk.CTkComboBox(self.frame_campos, values=self.documento_options, state="readonly")
        self.combo_documento.pack(fill="x", pady=(0, 10))

        # Botões
        self.frame_botoes = ctk.CTkFrame(self.frame_campos)
        self.frame_botoes.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar Caixa", command=self.salvar_caixa)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        
        self.lista_caixas = ctk.CTkTextbox(self.frame_principal, height=6)
        self.lista_caixas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        
        self.limpar_campos()
        self.atualizar_lista()

    def buscar_caixa(self, event=None):
        caixa_id = self.entry_ps_caixa.get().strip()
        if not caixa_id.isdigit():
            messagebox.showerror("Erro", "Por favor, insira um ID válido.")
            return

        caixa = self.db.query(Caixa).filter(Caixa.id == int(caixa_id)).first()
        if caixa:
            self.preencher_campos(caixa)
            self.caixa_selecionada = caixa  
        else:
            messagebox.showerror("Erro", "Caixa não encontrada.")

    def preencher_campos(self, caixa):
        self.entry_periodo_inc.delete(0, "end")
        self.entry_periodo_inc.insert(0, caixa.periodo_inc.strftime("%d/%m/%Y"))

        self.entry_periodo_fim.delete(0, "end")
        self.entry_periodo_fim.insert(0, caixa.periodo_fim.strftime("%d/%m/%Y"))

        self.entry_dt_previsao.delete(0, "end")
        self.entry_dt_previsao.insert(0, caixa.dt_previsao.strftime("%d/%m/%Y"))

        self.entry_dt_arquivamento.delete(0, "end")
        self.entry_dt_arquivamento.insert(0, caixa.dt_arquivamento.strftime("%d/%m/%Y"))

        localizacao = self.db.query(Localizacao).filter(Localizacao.id == caixa.localizacao_id).first()
        self.entry_localizacao.delete(0, "end")
        self.entry_localizacao.insert(0, str(localizacao.id))

        status_nome = next((k for k, v in self.status_map.items() if v == caixa.status_id), "")
        self.combo_status.set(status_nome)

        documento_nome = next((k for k, v in self.documento_map.items() if v == caixa.documento_id), "")
        self.combo_documento.set(documento_nome)

    def salvar_caixa(self):
        if not self.caixa_selecionada:
            messagebox.showwarning("Aviso", "Nenhuma caixa foi selecionada para edição.")
            return

        try:
           
            self.caixa_selecionada.periodo_inc = datetime.strptime(self.entry_periodo_inc.get(), "%d/%m/%Y")
            self.caixa_selecionada.periodo_fim = datetime.strptime(self.entry_periodo_fim.get(), "%d/%m/%Y")
            self.caixa_selecionada.dt_previsao = datetime.strptime(self.entry_dt_previsao.get(), "%d/%m/%Y")
            self.caixa_selecionada.dt_arquivamento = datetime.strptime(self.entry_dt_arquivamento.get(), "%d/%m/%Y")

            
            localizacao_id_str = self.entry_localizacao.get()
            if localizacao_id_str.isdigit():
                self.caixa_selecionada.localizacao_id = int(localizacao_id_str)

            
            status = self.combo_status.get()
            if status in self.status_map:
                self.caixa_selecionada.status_id = self.status_map[status]

            
            documento = self.combo_documento.get()
            if documento in self.documento_map:
                self.caixa_selecionada.documento_id = self.documento_map[documento]

            
            self.db.commit()
            self.limpar_campos()  
            
            messagebox.showinfo("Sucesso", "Caixa atualizada com sucesso!")
            self.atualizar_lista()  
        except Exception as e:
            self.db.rollback()  
            messagebox.showerror("Erro", f"Erro ao atualizar a caixa: {str(e)}")

    def atualizar_lista(self):
        self.lista_caixas.delete("0.0", "end")
        caixas = self.db.query(Caixa).all()
        for caixa in caixas:
            dt_prev = caixa.dt_previsao.strftime("%d/%m/%Y")
            dt_arq = caixa.dt_arquivamento.strftime("%d/%m/%Y")
            texto = (
                f"ID: {caixa.id}, Período inicial: {caixa.periodo_inc.strftime('%d/%m/%Y')}, "
                f"Período final: {caixa.periodo_fim.strftime('%d/%m/%Y')}, "
                f"Data Prevista para Exclusão: {dt_prev}, Arquivamento: {dt_arq}\n"
            )
            self.lista_caixas.insert("end", texto)

    def limpar_campos(self):
        self.entry_periodo_inc.delete(0, "end")
        self.entry_periodo_fim.delete(0, "end")
        self.entry_dt_previsao.delete(0, "end")
        self.entry_dt_arquivamento.delete(0, "end")
        self.entry_localizacao.delete(0, "end")
        self.entry_ps_caixa.delete(0, "end")
        self.combo_status.set(self.status_options[0] if self.status_options else "")
        self.combo_documento.set(self.documento_options[0] if self.documento_options else "")
        self.entry_dt_arquivamento.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_periodo_inc.focus()

    def formatar_data(self, event):
        entry = event.widget
        texto = entry.get()
        somente_numeros = ''.join(filter(str.isdigit, texto))[:8]

        resultado = ''
        for i, char in enumerate(somente_numeros):
            if i == 2 or i == 4:
                resultado += '/'
            resultado += char

        pos_cursor = entry.index("insert")
        entry.delete(0, "end")
        entry.insert(0, resultado)
        if pos_cursor == len(texto):
            entry.icursor(len(resultado))
        else:
            entry.icursor(pos_cursor)

    def get_status_options(self):
        try:
            status_list = self.db.query(Status).all()
            self.status_map = {s.tipo: s.id for s in status_list}
            return list(self.status_map.keys())
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar status: {e}")
            return []

    def get_documento_options(self):
        try:
            documentos = self.db.query(Documento).all()
            self.documento_map = {d.tp_doc: d.id for d in documentos}
            return list(self.documento_map.keys())
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar documentos: {e}")
            return []


if __name__ == "__main__":
    app = EditarCaixaApp()
    app.mainloop()