import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from models.models import Funcionario, Departamento
from database.session import SessionLocal
import pyrebase
from database.firebase_config import firebase_config  
from interface.permissao import verificar_permissao

# Inicialização Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Configurações de aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class CadastroFuncionarioApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastro de Funcionários")
        self.state('zoomed')

        # Verificação de permissão
        nivel_permissao = verificar_permissao(Session.matricula_logada)
        if nivel_permissao is None or nivel_permissao < 3:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta tela.")
            self.destroy()
            return

        # Sessão do banco
        self.db = SessionLocal()

        # Container principal
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="both", expand=True)

        # Título
        title = ctk.CTkLabel(container, text="Cadastro de Funcionário", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Entradas de dados
        self.entry_nome = ctk.CTkEntry(container, placeholder_text="Nome")
        self.entry_nome.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.entry_email = ctk.CTkEntry(container, placeholder_text="Email")
        self.entry_email.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.entry_senha = ctk.CTkEntry(container, placeholder_text="Senha", show="*")
        self.entry_senha.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.entry_cargo = ctk.CTkEntry(container, placeholder_text="Cargo")
        self.entry_cargo.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.option_departamento = ctk.CTkOptionMenu(container, values=[])
        self.option_departamento.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.combo_permissao = ctk.CTkComboBox(container, values=["1", "2", "3"], state="readonly")
        self.combo_permissao.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Botão Salvar
        btn_salvar = ctk.CTkButton(container, text="Salvar", command=self._salvar_funcionario)
        btn_salvar.grid(row=7, column=0, columnspan=2, pady=20)

        # Lista de funcionários
        self.lista_funcionarios = ctk.CTkTextbox(container, height=12)
        self.lista_funcionarios.grid(row=8, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

        container.rowconfigure(8, weight=1)
        container.columnconfigure((0, 1), weight=1)

        # Carregar opções e atualizar lista
        self._carregar_opcoes()
        self._limpar_campos()
        self.atualizar_lista()

    def _carregar_opcoes(self):
        """Carrega departamentos no OptionMenu."""
        with SessionLocal() as session:
            departamentos = session.query(Departamento).all()
            self.departamentos_dict = {f"{d.id} - {d.nome}": d.id for d in departamentos}
            self.option_departamento.configure(values=list(self.departamentos_dict.keys()))
            if departamentos:
                self.option_departamento.set(list(self.departamentos_dict.keys())[0])

    def _salvar_funcionario(self):
        """Salva um novo funcionário no Firebase e no banco local."""
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        cargo = self.entry_cargo.get().strip()
        departamento_key = self.option_departamento.get()
        permissao = self.combo_permissao.get().strip()

        if not nome or not email or not senha or not cargo or not departamento_key or not permissao:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            # Criação no Firebase
            auth.create_user_with_email_and_password(email, senha)

            # Grava no banco local
            departamento_id = self.departamentos_dict.get(departamento_key)
            with SessionLocal() as session:
                funcionario = Funcionario(
                    nome=nome,
                    email=email,
                    cargo=cargo,
                    departamento_id=departamento_id,
                    permissao=permissao
                )
                session.add(funcionario)
                session.commit()

            messagebox.showinfo("Sucesso", "Funcionário cadastrado com sucesso!")
            self._limpar_campos()
            self.atualizar_lista()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário no Firebase:\n{e}")

    def _limpar_campos(self):
        """Limpa todos os campos de entrada e reseta seleções."""
        self.entry_nome.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_senha.delete(0, "end")
        self.entry_cargo.delete(0, "end")

        # Reset OptionMenu de departamento
        valores_departamento = self.option_departamento.cget("values")
        if valores_departamento:
            self.option_departamento.set(valores_departamento[0])

        # Reset ComboBox de permissão
        valores_permissao = self.combo_permissao.cget("values")
        if valores_permissao:
            self.combo_permissao.set(valores_permissao[0])

    def atualizar_lista(self):
        """Atualiza o Textbox com a lista de funcionários cadastrados."""
        self.lista_funcionarios.delete("0.0", "end")
        with SessionLocal() as session:
            funcionarios = session.query(Funcionario).all()
            for f in funcionarios:
                texto = f"Matricula: {f.matricula}, Nome: {f.nome}, Cargo: {f.cargo}, Permissão: {f.permissao}\n"
                self.lista_funcionarios.insert("end", texto)


if __name__ == "__main__":
    app = CadastroFuncionarioApp()
    app.mainloop()
