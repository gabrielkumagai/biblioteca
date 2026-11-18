import tkinter as tk
from tkinter import ttk
from tela_alunos import TelaAluno
from tela_livros import TelaLivro
from tela_emprestimos import TelaEmprestimo
from tela_bibliotecarios import TelaBibliotecario
from tela_login import TelaLogin

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Biblioteca")
        self.geometry("500x430")
        # Bibliotecário logado: {"id_bibliotecario", "nome", "email"}
        self.bibliotecario = None

        self.criar_menu()

        ttk.Label(self,text="Sistema de Biblioteca",font=("Arial",20,"bold")).pack(pady=(30,10))
        self.lbl_usuario = ttk.Label(self,text="")
        self.lbl_usuario.pack(pady=(0,15))
        ttk.Label(self,text="Use o menu superior ou os botões abaixo").pack(pady=(0,10))

        for texto,comando in (("Empréstimos",self.abrir_emprestimos),
                              ("Cadastro de Alunos",self.abrir_alunos),
                              ("Cadastro de Livros",self.abrir_livros),
                              ("Cadastro de Bibliotecários",self.abrir_bibliotecarios)):
            ttk.Button(self,text=texto,command=comando,width=28).pack(pady=6,ipady=5)

        self.pedir_login()

    def criar_menu(self):
        barra = tk.Menu(self)

        menu_cadastros = tk.Menu(barra,tearoff=0)
        menu_cadastros.add_command(label="Alunos",command=self.abrir_alunos)
        menu_cadastros.add_command(label="Livros",command=self.abrir_livros)
        menu_cadastros.add_command(label="Bibliotecários",command=self.abrir_bibliotecarios)
        barra.add_cascade(label="Cadastros",menu=menu_cadastros)

        menu_mov = tk.Menu(barra,tearoff=0)
        menu_mov.add_command(label="Empréstimos",command=self.abrir_emprestimos)
        barra.add_cascade(label="Movimentação",menu=menu_mov)

        menu_conta = tk.Menu(barra,tearoff=0)
        menu_conta.add_command(label="Sair",command=self.sair)
        barra.add_cascade(label="Conta",menu=menu_conta)

        self.config(menu=barra)

    def pedir_login(self):
        """Esconde a janela principal e abre a tela de login."""
        self.withdraw()
        TelaLogin(self,ao_logar=self.ao_logar,ao_fechar=self.destroy)

    def definir_usuario(self,bibliotecario):
        """Guarda o bibliotecário logado e mostra o nome dele."""
        self.bibliotecario = bibliotecario
        self.lbl_usuario.config(text=f"Logado como: {bibliotecario['nome']}")

    def ao_logar(self,bibliotecario):
        self.definir_usuario(bibliotecario)
        self.deiconify()

    def sair(self):
        """Faz logout: fecha as telas abertas e volta para o login."""
        for janela in self.winfo_children():
            if isinstance(janela,tk.Toplevel):
                janela.destroy()
        self.bibliotecario = None
        self.lbl_usuario.config(text="")
        self.pedir_login()

    def abrir_alunos(self):
        TelaAluno(self)

    def abrir_livros(self):
        TelaLivro(self)

    def abrir_emprestimos(self):
        TelaEmprestimo(self)

    def abrir_bibliotecarios(self):
        TelaBibliotecario(self)

if __name__ == "__main__":
    App().mainloop()
