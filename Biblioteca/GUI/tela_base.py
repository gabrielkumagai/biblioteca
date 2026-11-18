import tkinter as tk
import threading
from email.utils import parsedate_to_datetime
from tkinter import ttk, messagebox
import api_client as api


def formatar_data(valor, com_hora=False):
    """Converte a data da API ("Mon, 16 Nov 2026 16:23:21 GMT") para dd/mm/aaaa."""
    if not valor:
        return ""
    try:
        data = parsedate_to_datetime(valor)
    except (TypeError, ValueError):
        return str(valor)
    return data.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")


def preencher(entry, valor):
    """Substitui o texto de um Entry/Spinbox."""
    entry.delete(0, tk.END)
    entry.insert(0, "" if valor is None else str(valor))


class TelaBase(tk.Toplevel):
    """Janela com barra de carregamento e chamadas à API fora da thread da interface.

    As subclasses colocam seus botões em self.botoes (são desabilitados
    durante as chamadas) e chamam criar_status() e criar_tabela().
    """

    def __init__(self, master, titulo, geometria):
        super().__init__(master)
        self.title(titulo)
        self.geometry(geometria)
        self.resizable(False, False)
        self.botoes = []

    def criar_status(self):
        self.lbl_status = ttk.Label(self, text="")
        self.lbl_status.pack(anchor="w", padx=10, pady=(8, 0))
        self.loading = ttk.Progressbar(self, mode="indeterminate", length=300)

    def criar_tabela(self, colunas, altura=12):
        """colunas: lista de (chave, título, largura, alinhamento)."""
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        tree = ttk.Treeview(frame, columns=[c[0] for c in colunas],
                            show="headings", height=altura, selectmode="browse")
        for chave, titulo, largura, alinhamento in colunas:
            tree.heading(chave, text=titulo)
            tree.column(chave, width=largura, anchor=alinhamento)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def id_selecionado(self, tree):
        """Retorna o iid (id do registro) da linha selecionada ou None."""
        sel = tree.selection()
        return sel[0] if sel else None

    def iniciar_loading(self, texto):
        self.lbl_status.config(text=texto)
        self.loading.pack(after=self.lbl_status, anchor="w", padx=10, pady=2)
        self.loading.start(10)
        for b in self.botoes:
            b.state(["disabled"])
        self.config(cursor="watch")

    def parar_loading(self):
        self.loading.stop()
        self.loading.pack_forget()
        self.lbl_status.config(text="")
        for b in self.botoes:
            b.state(["!disabled"])
        self.config(cursor="")

    def executar(self, texto, tarefa, ao_concluir):
        """Roda tarefa() em outra thread e chama ao_concluir(resultado) se der certo."""
        self.iniciar_loading(texto)

        def worker():
            try:
                resultado, erro = tarefa(), None
            except api.ApiError as e:
                resultado, erro = None, str(e)
            except Exception as e:
                resultado, erro = None, f"Erro inesperado: {e}"
            try:
                self.after(0, lambda: self.finalizar(resultado, erro, ao_concluir))
            except RuntimeError:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def finalizar(self, resultado, erro, ao_concluir):
        if not self.winfo_exists():
            return
        self.parar_loading()
        if erro:
            messagebox.showerror("Erro", erro, parent=self)
            return
        ao_concluir(resultado)

    def aviso(self, mensagem):
        messagebox.showwarning("Atenção", mensagem, parent=self)

    def sucesso(self, mensagem=None):
        if mensagem:
            messagebox.showinfo("Sucesso", mensagem, parent=self)
        self.limpar()
        self.listar()
