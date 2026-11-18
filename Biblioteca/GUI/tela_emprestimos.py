import tkinter as tk
from tkinter import ttk, messagebox
import api_client as api
from tela_base import TelaBase, formatar_data


class TelaEmprestimo(TelaBase):
    """Registro de empréstimos e devoluções.

    O bibliotecário responsável é o que está logado (master.bibliotecario).
    """

    def __init__(self, master):
        super().__init__(master, "Empréstimos", "900x580")
        self.bibliotecario = master.bibliotecario
        self.emprestimos = {}
        self.ids_alunos = []
        self.ids_livros = []

        form = ttk.LabelFrame(self, text="Novo empréstimo", padding=10)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Aluno:").grid(row=0, column=0, sticky="w", pady=3)
        self.cmb_aluno = ttk.Combobox(form, state="readonly", width=60)
        self.cmb_aluno.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Livro:").grid(row=1, column=0, sticky="w", pady=3)
        self.cmb_livro = ttk.Combobox(form, state="readonly", width=60)
        self.cmb_livro.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(form, text="Responsável:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(form, text=self.bibliotecario["nome"]).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", padx=10)
        self.botoes = [
            ttk.Button(botoes, text="Emprestar", command=self.emprestar),
            ttk.Button(botoes, text="Registrar devolução", command=self.devolver),
            ttk.Button(botoes, text="Excluir", command=self.excluir),
            ttk.Button(botoes, text="Limpar", command=self.limpar),
            ttk.Button(botoes, text="Recarregar", command=self.listar),
        ]
        for b in self.botoes:
            b.pack(side="left", padx=3)

        self.somente_abertos = tk.BooleanVar(value=False)
        ttk.Checkbutton(botoes, text="Somente em aberto", variable=self.somente_abertos,
                        command=self.mostrar_emprestimos).pack(side="right", padx=3)

        self.criar_status()
        self.tree = self.criar_tabela([
            ("id_emprestimo", "ID", 45, "center"),
            ("aluno", "Aluno", 190, "w"),
            ("livro", "Livro", 230, "w"),
            ("bibliotecario", "Bibliotecário", 150, "w"),
            ("data", "Emprestado em", 120, "center"),
            ("devolucao", "Devolução", 110, "center"),
        ])
        self.tree.tag_configure("aberto", foreground="#b00000")
        self.listar()

    def listar(self):
        self.executar("Carregando empréstimos...",
                      lambda: (api.listar("alunos"), api.listar("livros"), api.listar("emprestimos")),
                      self.preencher)

    def preencher(self, resultado):
        alunos, livros, emprestimos = resultado
        self.emprestimos = {str(e["id_emprestimo"]): e for e in emprestimos or []}

        abertos = {}
        for e in self.emprestimos.values():
            if not e.get("data_devolucao"):
                abertos[e["id_livro"]] = abertos.get(e["id_livro"], 0) + 1

        self.ids_alunos = [a["id_aluno"] for a in alunos or []]
        self.cmb_aluno["values"] = [f"{a['id_aluno']} - {a['nome']} ({a['email']})" for a in alunos or []]

        self.ids_livros = [l["id_livro"] for l in livros or []]
        self.cmb_livro["values"] = [
            f"{l['id_livro']} - {l['titulo']} ({l['exemplares'] - abertos.get(l['id_livro'], 0)} disponíveis)"
            for l in livros or []]

        self.mostrar_emprestimos()

    def mostrar_emprestimos(self):
        """Redesenha a tabela aplicando o filtro "Somente em aberto"."""
        self.tree.delete(*self.tree.get_children())
        for iid, e in self.emprestimos.items():
            aberto = not e.get("data_devolucao")
            if self.somente_abertos.get() and not aberto:
                continue
            self.tree.insert("", "end", iid=iid, tags=("aberto",) if aberto else (), values=(
                e["id_emprestimo"], e["nome_aluno"], e["titulo_livro"], e["nome_bibliotecario"],
                formatar_data(e["data"], com_hora=True),
                "Em aberto" if aberto else formatar_data(e["data_devolucao"])))

    def emprestar(self):
        i_aluno, i_livro = self.cmb_aluno.current(), self.cmb_livro.current()
        if i_aluno < 0 or i_livro < 0:
            self.aviso("Selecione o aluno e o livro")
            return
        dados = {"id_aluno": self.ids_alunos[i_aluno],
                 "id_livro": self.ids_livros[i_livro],
                 "id_bibliotecario": self.bibliotecario["id_bibliotecario"]}
        self.executar("Registrando empréstimo...", lambda: api.criar("emprestimos", dados),
                      lambda _r: self.sucesso("Empréstimo registrado!"))

    def selecionado(self):
        iid = self.id_selecionado(self.tree)
        if not iid:
            self.aviso("Selecione um empréstimo na tabela!")
        return iid

    def devolver(self):
        iid = self.selecionado()
        if not iid:
            return
        if self.emprestimos[iid].get("data_devolucao"):
            self.aviso("Este empréstimo já foi devolvido")
            return
        e = self.emprestimos[iid]
        if not messagebox.askyesno("Confirmar",
                                   f"Registrar a devolução de \"{e['titulo_livro']}\" por {e['nome_aluno']}?",
                                   parent=self):
            return
        self.executar("Registrando devolução...", lambda: api.devolver_emprestimo(iid),
                      lambda _r: self.sucesso("Devolução registrada!"))

    def excluir(self):
        iid = self.selecionado()
        if not iid:
            return
        if not messagebox.askyesno("Confirmar", "Deseja excluir este registro de empréstimo?", parent=self):
            return
        self.executar("Excluindo empréstimo...", lambda: api.deletar("emprestimos", iid),
                      lambda _r: self.sucesso())

    def limpar(self):
        self.cmb_aluno.set("")
        self.cmb_livro.set("")
        self.tree.selection_remove(self.tree.selection())
