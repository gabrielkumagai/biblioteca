import tkinter as tk
import threading
from tkinter import ttk, messagebox
import api_client as api


def rodar_em_thread(janela, tarefa, ao_concluir):
    """Executa `tarefa` fora da thread da interface.

    Chama ao_concluir(resultado, erro) de volta na thread do Tkinter.
    `erro` é uma mensagem (str) ou None.
    """
    def worker():
        try:
            resultado, erro = tarefa(), None
        except api.ApiError as e:
            resultado, erro = None, str(e)
        except Exception as e:
            resultado, erro = None, f"Erro inesperado: {e}"
        try:
            janela.after(0, lambda: janela.winfo_exists() and ao_concluir(resultado, erro))
        except RuntimeError:
            pass
    threading.Thread(target=worker, daemon=True).start()


class TelaLogin(tk.Toplevel):
    """Janela de login do bibliotecário.

    Chama ao_logar(bibliotecario) quando o login dá certo e
    ao_fechar() se o usuário fechar a janela sem entrar.
    """

    def __init__(self, master, ao_logar, ao_fechar):
        super().__init__(master)
        self.ao_logar = ao_logar
        self.ao_fechar = ao_fechar
        self.title("Login - Sistema de Biblioteca")
        self.geometry("360x250")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Login do Bibliotecário", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))

        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_email = ttk.Entry(frame, width=30)
        self.ent_email.grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky="w", pady=4)
        self.ent_senha = ttk.Entry(frame, width=30, show="*")
        self.ent_senha.grid(row=2, column=1, pady=4)

        botoes = ttk.Frame(frame)
        botoes.grid(row=3, column=0, columnspan=2, pady=15)
        self.btn_entrar = ttk.Button(botoes, text="Entrar", command=self.entrar)
        self.btn_entrar.pack(side="left", padx=5)
        self.btn_cadastrar = ttk.Button(botoes, text="Criar conta", command=self.abrir_cadastro)
        self.btn_cadastrar.pack(side="left", padx=5)

        self.lbl_status = ttk.Label(frame, text="")
        self.lbl_status.grid(row=4, column=0, columnspan=2)

        self.bind("<Return>", lambda _e: self.entrar())
        self.ent_email.focus_set()

    def ocupado(self, sim, texto=""):
        estado = ["disabled"] if sim else ["!disabled"]
        self.btn_entrar.state(estado)
        self.btn_cadastrar.state(estado)
        self.lbl_status.config(text=texto)
        self.config(cursor="watch" if sim else "")

    def entrar(self):
        if self.btn_entrar.instate(["disabled"]):
            return
        email = self.ent_email.get().strip()
        senha = self.ent_senha.get()
        if not email or not senha:
            messagebox.showwarning("Atenção", "Informe email e senha", parent=self)
            return
        self.ocupado(True, "Entrando...")
        rodar_em_thread(self, lambda: api.login(email, senha), self.depois_do_login)

    def depois_do_login(self, resultado, erro):
        self.ocupado(False)
        if erro:
            messagebox.showerror("Erro", erro, parent=self)
            self.ent_senha.delete(0, tk.END)
            return
        bibliotecario = resultado["bibliotecario"]
        self.destroy()
        self.ao_logar(bibliotecario)

    def abrir_cadastro(self):
        TelaCadastroBibliotecario(self, self.preencher_email)

    def preencher_email(self, email):
        self.ent_email.delete(0, tk.END)
        self.ent_email.insert(0, email)
        self.ent_senha.delete(0, tk.END)
        self.ent_senha.focus_set()

    def fechar(self):
        self.destroy()
        self.ao_fechar()


class TelaCadastroBibliotecario(tk.Toplevel):
    """Cadastro de um novo bibliotecário a partir da tela de login."""

    def __init__(self, master, ao_cadastrar):
        super().__init__(master)
        self.ao_cadastrar = ao_cadastrar
        self.title("Criar conta de bibliotecário")
        self.geometry("380x250")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        campos = (("Nome:", None), ("Email:", None), ("Senha:", "*"), ("Confirmar senha:", "*"))
        self.entradas = []
        for linha, (rotulo, mascara) in enumerate(campos):
            ttk.Label(frame, text=rotulo).grid(row=linha, column=0, sticky="w", pady=4)
            entrada = ttk.Entry(frame, width=30, show=mascara or "")
            entrada.grid(row=linha, column=1, pady=4)
            self.entradas.append(entrada)
        self.ent_nome, self.ent_email, self.ent_senha, self.ent_confirma = self.entradas

        self.btn_salvar = ttk.Button(frame, text="Cadastrar", command=self.salvar)
        self.btn_salvar.grid(row=4, column=0, columnspan=2, pady=15)

        self.bind("<Return>", lambda _e: self.salvar())
        self.ent_nome.focus_set()

    def salvar(self):
        if self.btn_salvar.instate(["disabled"]):
            return
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()
        senha = self.ent_senha.get()
        if not nome or not email or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos", parent=self)
            return
        if senha != self.ent_confirma.get():
            messagebox.showwarning("Atenção", "As senhas não conferem", parent=self)
            return

        self.btn_salvar.state(["disabled"])
        dados = {"nome": nome, "email": email, "senha": senha}
        rodar_em_thread(self, lambda: api.criar("bibliotecarios", dados), self.depois_de_salvar)

    def depois_de_salvar(self, resultado, erro):
        self.btn_salvar.state(["!disabled"])
        if erro:
            messagebox.showerror("Erro", erro, parent=self)
            return
        messagebox.showinfo("Sucesso", "Conta criada! Faça o login.", parent=self)
        email = resultado["email"]
        self.destroy()
        self.ao_cadastrar(email)
