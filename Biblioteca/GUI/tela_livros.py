import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api
from tela_base import TelaBase, preencher


class TelaLivro(TelaBase):
    """Cadastro de livros. Mostra também quantos exemplares estão disponíveis."""

    def __init__(self, master):
        super().__init__(master, "Cadastro de Livros", "800x560")
        self.livro_id = None
        self.livros = {}

        form = ttk.LabelFrame(self, text="Dados do Livro", padding=10)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Título:").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_titulo = ttk.Entry(form, width=55)
        self.ent_titulo.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Autor:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_autor = ttk.Entry(form, width=45)
        self.ent_autor.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Editora:").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_editora = ttk.Entry(form, width=45)
        self.ent_editora.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Exemplares:").grid(row=3, column=0, sticky="w", pady=3)
        self.ent_exemplares = ttk.Spinbox(form, from_=0, to=9999, width=8)
        self.ent_exemplares.grid(row=3, column=1, sticky="w", padx=5, pady=3)
        preencher(self.ent_exemplares, 1)

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
            ("id_livro", "ID", 50, "center"),
            ("titulo", "Título", 230, "w"),
            ("autor", "Autor", 160, "w"),
            ("editora", "Editora", 130, "w"),
            ("exemplares", "Exemplares", 85, "center"),
            ("disponiveis", "Disponíveis", 85, "center"),
        ])
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)
        self.listar()

    def listar(self):
        # Busca também os empréstimos para calcular os exemplares disponíveis.
        self.executar("Carregando livros...",
                      lambda: (api.listar("livros"), api.listar("emprestimos")),
                      self.preencher_tabela)

    def preencher_tabela(self, resultado):
        livros, emprestimos = resultado
        abertos = {}
        for e in emprestimos or []:
            if not e.get("data_devolucao"):
                abertos[e["id_livro"]] = abertos.get(e["id_livro"], 0) + 1

        self.tree.delete(*self.tree.get_children())
        self.livros = {}
        for l in livros or []:
            self.livros[str(l["id_livro"])] = l
            disponiveis = l["exemplares"] - abertos.get(l["id_livro"], 0)
            self.tree.insert("", "end", iid=str(l["id_livro"]), values=(
                l["id_livro"], l["titulo"], l["autor"], l.get("editora") or "",
                l["exemplares"], disponiveis))

    def ao_selecionar(self, _event):
        iid = self.id_selecionado(self.tree)
        if not iid:
            return
        livro = self.livros[iid]
        self.livro_id = iid
        preencher(self.ent_titulo, livro["titulo"])
        preencher(self.ent_autor, livro["autor"])
        preencher(self.ent_editora, livro.get("editora"))
        preencher(self.ent_exemplares, livro["exemplares"])

    def dados(self):
        titulo = self.ent_titulo.get().strip()
        autor = self.ent_autor.get().strip()
        editora = self.ent_editora.get().strip()
        if not titulo or not autor:
            self.aviso("Preencha título e autor")
            return None
        try:
            exemplares = int(self.ent_exemplares.get().strip())
        except ValueError:
            exemplares = -1
        if exemplares < 0:
            self.aviso("Exemplares deve ser um número inteiro maior ou igual a 0")
            return None
        return {"titulo": titulo, "autor": autor,
                "editora": editora or None, "exemplares": exemplares}

    def inserir(self):
        dados = self.dados()
        if not dados:
            return
        self.executar("Salvando livro...", lambda: api.criar("livros", dados),
                      lambda _r: self.sucesso("Livro cadastrado com sucesso"))

    def atualizar(self):
        if not self.livro_id:
            self.aviso("Selecione um livro!")
            return
        dados = self.dados()
        if not dados:
            return
        id_livro = self.livro_id
        self.executar("Atualizando livro...", lambda: api.atualizar("livros", id_livro, dados),
                      lambda _r: self.sucesso("Livro atualizado!"))

    def deletar(self):
        if not self.livro_id:
            self.aviso("Selecione um livro!")
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir este livro?", parent=self):
            return
        id_livro = self.livro_id
        self.executar("Excluindo livro...", lambda: api.deletar("livros", id_livro),
                      lambda _r: self.sucesso())

    def limpar(self):
        self.livro_id = None
        for entry in (self.ent_titulo, self.ent_autor, self.ent_editora):
            entry.delete(0, tk.END)
        preencher(self.ent_exemplares, 1)
        self.tree.selection_remove(self.tree.selection())
