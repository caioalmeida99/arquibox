import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import Session
from models.models import Caixa, Status, Documento
from interface.permissao import verificar_permissao
from interface.consulta_localizacao import localizacoes_vazia
from database.session import SessionLocal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CadastroCaixaApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro Caixa")
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
        self.documento_options = self.get_documento_options()

        # Campo Inicio do periodo
        self.label_periodo_inc = ctk.CTkLabel(self.frame_campos, text="Data inicio do periodo (DD/MM/YYYY):", anchor="w")
        self.label_periodo_inc.pack(fill="x", pady=(0, 2))
        self.entry_periodo_inc = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_periodo_inc.pack(fill="x", pady=(0, 10))
        self.entry_periodo_inc.bind("<KeyRelease>", self.formatar_data)

        # Campo Fim do periodo
        self.label_periodo_fim = ctk.CTkLabel(self.frame_campos, text="Data final do periodo (DD/MM/YYYY):", anchor="w")
        self.label_periodo_fim.pack(fill="x", pady=(0, 2))
        self.entry_periodo_fim = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_periodo_fim.pack(fill="x", pady=(0, 10)) 
        self.entry_periodo_fim.bind("<KeyRelease>", self.formatar_data)       

        # Campo Data exclusão
        self.label_dt_previsao = ctk.CTkLabel(self.frame_campos, text="Data Prevista para Exclusão (DD/MM/YYYY):", anchor="w")
        self.label_dt_previsao.pack(fill="x", pady=(0, 2))
        self.entry_dt_previsao = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_dt_previsao.pack(fill="x", pady=(0, 10))
        self.entry_dt_previsao.bind("<KeyRelease>", self.formatar_data)

        # Campo da data que está sendo arquivado
        self.label_dt_arquivamento = ctk.CTkLabel(self.frame_campos, text="Data Arquivamento (DD/MM/YYYY):", anchor="w")
        self.label_dt_arquivamento.pack(fill="x", pady=(0, 2))
        self.entry_dt_arquivamento = ctk.CTkEntry(self.frame_campos, justify="left")
        self.entry_dt_arquivamento.pack(fill="x", pady=(0, 10))
        self.entry_dt_arquivamento.bind("<KeyRelease>", self.formatar_data)

        # Campo dos status
        self.label_status = ctk.CTkLabel(self.frame_campos, text="Status:", anchor="w")
        self.label_status.pack(fill="x", pady=(10, 2))
        self.status_options = self.get_status_options()
        self.combo_status = ctk.CTkComboBox(self.frame_campos, values=self.status_options)
        self.combo_status.pack(fill="x", pady=(0, 10))
        self.combo_status.configure(state="readonly")

        # Campo Localização Vazia
        self.label_localizacao = ctk.CTkLabel(self.frame_campos, text="Localização Vazia:", anchor="w")
        self.label_localizacao.pack(fill="x", pady=(10, 2))  
        self.combo_localizacao = ctk.CTkComboBox(self.frame_campos, state="readonly")  
        self.combo_localizacao.pack(fill="x", pady=(0, 10))

        # Campo Documento
        self.label_documento = ctk.CTkLabel(self.frame_campos, text="Tipo de Documento:", anchor="w")
        self.label_documento.pack(fill="x", pady=(10, 2))
        self.combo_documento = ctk.CTkComboBox(self.frame_campos, values=self.documento_options)
        self.combo_documento.pack(fill="x", pady=(0, 10))
        self.combo_documento.configure(state="readonly")

        self.frame_botoes = ctk.CTkFrame(self.frame_campos)
        self.frame_botoes.pack(pady=10)

        self.btn_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar Caixa", command=self.salvar_caixa)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        self.lista_caixas = ctk.CTkTextbox(self.frame_principal, height=6)
        self.lista_caixas.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        self.atualizar_combobox_localizacao()
        self.limpar_campos()
        self.atualizar_lista()

    def salvar_caixa(self):
        periodo_inc_str = self.entry_periodo_inc.get().strip()
        periodo_fim_str = self.entry_periodo_fim.get().strip()
        dt_prev_exclusao_str = self.entry_dt_previsao.get().strip()
        dt_arquivamento_str = self.entry_dt_arquivamento.get().strip()
        localizacao_str = self.combo_localizacao.get().strip()  # Obter a localização do combobox
        status_nome = self.combo_status.get()
        status_id = self.status_map.get(status_nome)

        if not periodo_inc_str or not periodo_fim_str or not dt_prev_exclusao_str or not dt_arquivamento_str or not status_nome or not localizacao_str:
            messagebox.showerror("Erro", "Preencha todos os campos antes de salvar.")
            return

        try:
            periodo_inc = datetime.strptime(periodo_inc_str, "%d/%m/%Y")
            periodo_fim = datetime.strptime(periodo_fim_str, "%d/%m/%Y")
            dt_prev_exclusao = datetime.strptime(dt_prev_exclusao_str, "%d/%m/%Y")
            dt_arquivamento = datetime.strptime(dt_arquivamento_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/YYYY.")
            return

        if not status_id:
            messagebox.showerror("Erro", "Selecione um status válido.")
            return

        tp_doc = self.combo_documento.get()
        documento_id = self.documento_map.get(tp_doc)

        if not documento_id:
            messagebox.showerror("Erro", "Selecione um tipo de documento válido.")
            return

        # Obter o ID da localização correspondente
        localizacao_id = self.get_localizacao_id(localizacao_str)

        if localizacao_id is None:
            messagebox.showerror("Erro", "Localização inválida selecionada.")
            return

        nova_caixa = Caixa(
            periodo_inc=periodo_inc,
            periodo_fim=periodo_fim,
            dt_previsao=dt_prev_exclusao,
            dt_arquivamento=dt_arquivamento,
            status_id=status_id,
            localizacao_id=localizacao_id,  # Aqui deve ser o ID da localização
            documento_id=documento_id
        )

        try:
            self.db.add(nova_caixa)
            self.db.commit()
            self.atualizar_lista()  # Atualiza a lista de caixas
            self.atualizar_combobox_localizacao()
            messagebox.showinfo("Sucesso", "Caixa salva com sucesso!")
            self.limpar_campos()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro ao salvar", str(e))

    def get_localizacao_id(self, localizacao_str):
        """Retorna o ID da localização correspondente à string formatada."""
        localizacoes_vazias = localizacoes_vazia(self.db)
        for loc in localizacoes_vazias:
            if f"{loc.sala} - Prateleira {loc.prateleira} - Coluna {loc.coluna}" == localizacao_str:
                return loc.id
        return None

    def atualizar_lista(self):
        self.lista_caixas.delete("0.0", "end")
        caixas = self.db.query(Caixa).all()
        for caixa in caixas:
            dt_prev = caixa.dt_previsao.strftime("%d/%m/%Y")
            dt_arq = caixa.dt_arquivamento.strftime("%d/%m/%Y")
            texto = f"ID: {caixa.id}, Período inicial: {caixa.periodo_inc}, Período final: {caixa.periodo_fim}, Data Prevista para Exclusão: {dt_prev}, Arquivamento: {dt_arq}\n"
            self.lista_caixas.insert("end", texto)

    def limpar_campos(self):
        self.entry_periodo_inc.delete(0, "end")
        self.entry_periodo_fim.delete(0, "end")
        self.entry_dt_previsao.delete(0, "end")
        self.entry_dt_arquivamento.delete(0, "end")
        self.entry_periodo_inc.focus()
        self.combo_status.set(self.status_options[0] if self.status_options else "")
        self.combo_localizacao.set("Selecione a localização")  # Limpa a seleção do combobox de localizações
        data_atual = datetime.now().strftime("%d/%m/%Y")
        self.entry_dt_arquivamento.insert(0, data_atual)  # Preenche a data de arquivamento automaticamente

    def formatar_data(self, event):
        entry = event.widget
        texto = entry.get()

        # Remove tudo que não for dígito
        somente_numeros = ''.join(filter(str.isdigit, texto))

        # Limita a 8 dígitos (DDMMAAAA)
        somente_numeros = somente_numeros[:8]

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
            status_arquivado = self.db.query(Status).filter(Status.tipo == "Arquivado").first()
            
            if not status_arquivado:
                raise ValueError("Status 'Arquivado' não encontrado no banco de dados")
                
            self.status_map = {"Arquivado": status_arquivado.id}
            return ["Arquivado"]
            
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

    def atualizar_combobox_localizacao(self):
        localizacoes_vazias = localizacoes_vazia(self.db)  
        
        opcoes = [
            f"{loc.sala} - Prateleira {loc.prateleira} - Coluna {loc.coluna}" 
            for loc in localizacoes_vazias
        ]
        
        self.combo_localizacao.configure(values=opcoes)
        
        if not opcoes:
            self.combo_localizacao.configure(state="disabled")
            self.combo_localizacao.set("Nenhuma localização disponível")
        else:
            self.combo_localizacao.set("Selecione a localização")

if __name__ == "__main__":
    app = CadastroCaixaApp()
    app.mainloop()
