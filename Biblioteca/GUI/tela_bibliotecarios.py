import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api
from tela_base import TelaBase, formatar_data, preencher


class TelaBibliotecario(TelaBase):
    """Cadastro de bibliotecários.

    Na atualização a senha é opcional: em branco, mantém a senha atual.
    O bibliotecário logado não pode excluir a própria conta.
    """

    def __init__(self, master):
        super().__init__(master, "Cadastro de Bibliotecários", "700x540")
        self.bibliotecario_id = None
        self.bibliotecarios = {}

        form = ttk.LabelFrame(self, text="Dados do Bibliotecário", padding=10)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_nome = ttk.Entry(form, width=50)
        self.ent_nome.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_email = ttk.Entry(form, width=50)
        self.ent_email.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Senha:").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_senha = ttk.Entry(form, width=30, show="*")
        self.ent_senha.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        ttk.Label(form, text="Ao atualizar, deixe a senha em branco para mantê-la.",
                  foreground="gray").grid(row=3, column=1, sticky="w", padx=5)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", padx=10)
        self.botoes = [
            ttk.Button(botoes, text="Inserir", command=self.inserir),
            ttk.Button(botoes, text="Atualizar", command=self.atualizar),
            ttk.Button(botoes, text="Deletar", command=self.deletar),
            ttk.Button(botoes, text="Limpar", command=self.limpar),
            ttk.Button(botoes, text="Recarregar", command=self.listar),
        ]
        for b in self.botoes:
            b.pack(side="left", padx=3)

        self.criar_status()
        self.tree = self.criar_tabela([
            ("id_bibliotecario", "ID", 50, "center"),
            ("nome", "Nome", 220, "w"),
            ("email", "Email", 250, "w"),
            ("data_cadastro", "Cadastrado em", 130, "center"),
        ])
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)
        self.listar()

    def id_logado(self):
        return str(self.master.bibliotecario["id_bibliotecario"])

    def listar(self):
        self.executar("Carregando bibliotecários...", lambda: api.listar("bibliotecarios"),
                      self.preencher_tabela)

    def preencher_tabela(self, bibliotecarios):
        self.tree.delete(*self.tree.get_children())
        self.bibliotecarios = {}
        for b in bibliotecarios or []:
            iid = str(b["id_bibliotecario"])
            self.bibliotecarios[iid] = b
            self.tree.insert("", "end", iid=iid, values=(
                b["id_bibliotecario"], b["nome"], b["email"], formatar_data(b.get("data_cadastro"))))

    def ao_selecionar(self, _event):
        iid = self.id_selecionado(self.tree)
        if not iid:
            return
        b = self.bibliotecarios[iid]
        self.bibliotecario_id = iid
        preencher(self.ent_nome, b["nome"])
        preencher(self.ent_email, b["email"])
        self.ent_senha.delete(0, tk.END)

    def dados(self, senha_obrigatoria):
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()
        senha = self.ent_senha.get()
        if not nome or not email or (senha_obrigatoria and not senha):
            self.aviso("Preencha nome, email e senha" if senha_obrigatoria else "Preencha nome e email")
            return None
        dados = {"nome": nome, "email": email}
        if senha:
            dados["senha"] = senha
        return dados

    def inserir(self):
        dados = self.dados(senha_obrigatoria=True)
        if not dados:
            return
        self.executar("Salvando bibliotecário...", lambda: api.criar("bibliotecarios", dados),
                      lambda _r: self.sucesso("Bibliotecário cadastrado com sucesso"))

    def atualizar(self):
        if not self.bibliotecario_id:
            self.aviso("Selecione um bibliotecário!")
            return
        dados = self.dados(senha_obrigatoria=False)
        if not dados:
            return
        iid = self.bibliotecario_id
        self.executar("Atualizando bibliotecário...", lambda: api.atualizar("bibliotecarios", iid, dados),
                      self.depois_de_atualizar)

    def depois_de_atualizar(self, bibliotecario):
        # Se alterou a própria conta, atualiza o nome mostrado na janela principal.
        if str(bibliotecario["id_bibliotecario"]) == self.id_logado():
            self.master.definir_usuario(bibliotecario)
        self.sucesso("Bibliotecário atualizado!")

    def deletar(self):
        if not self.bibliotecario_id:
            self.aviso("Selecione um bibliotecário!")
            return
        if self.bibliotecario_id == self.id_logado():
            self.aviso("Você não pode excluir a própria conta enquanto está logado")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir este bibliotecário?", parent=self):
            return
        iid = self.bibliotecario_id
        self.executar("Excluindo bibliotecário...", lambda: api.deletar("bibliotecarios", iid),
                      lambda _r: self.sucesso())

    def limpar(self):
        self.bibliotecario_id = None
        for entry in (self.ent_nome, self.ent_email, self.ent_senha):
            entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())
