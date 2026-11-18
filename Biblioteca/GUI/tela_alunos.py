import tkinter as tk
import threading
from tkinter import ttk,messagebox
import api_client as api

class TelaAluno(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Cadastro de Alunos")
        self.geometry("700x530")
        self.resizable(False,False)
        self.aluno_id = None

        form = ttk.LabelFrame(self,text="Dados do Aluno",padding=10)
        form.pack(fill="x",padx=10,pady=10)
        
        ttk.Label(form,text="Nome:").grid(row=0,column=0,sticky="w",pady=3)
        self.ent_nome = ttk.Entry(form,width=50)
        self.ent_nome.grid(row=0,column=1,padx=5,pady=3)

        ttk.Label(form,text="Email:").grid(row=1,column=0,sticky="w",pady=3)
        self.ent_email = ttk.Entry(form,width=55)
        self.ent_email.grid(row=1,column=1,padx=5,pady=3)

        ttk.Label(form,text="Curso:").grid(row=2,column=0,sticky="w",pady=3)
        self.ent_curso = ttk.Entry(form,width=30)
        self.ent_curso.grid(row=2,column=1,padx=5,pady=3)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x",pady=10)
        self.botoes = [
            ttk.Button(botoes,text="Inserir",command=self.inserir),
            ttk.Button(botoes,text="Atualizar",command=self.atualizar),
            ttk.Button(botoes,text="Deletar",command=self.deletar),
            ttk.Button(botoes,text="Limpar",command=self.limpar),
            ttk.Button(botoes,text="Recarregar",command=self.listar)
        ]

        for b in self.botoes:
            b.pack(side="left",padx=3)
        
        self.lbl_status = ttk.Label(self,text="")
        self.lbl_status.pack(anchor="w",padx=10,pady=(8,0))
        self.loading = ttk.Progressbar(self,mode="indeterminate",length=300)

        frame_tabela = ttk.Frame(self)
        frame_tabela.pack(fill="both",expand=True,padx=10,pady=10)

        colunas = ("id_aluno","nome","email","curso")
        self.tree = ttk.Treeview(frame_tabela,columns=colunas,show="headings",height=14)
        self.tree.heading("id_aluno",text="ID")
        self.tree.heading("nome",text="Nome")
        self.tree.heading("email",text="Email")
        self.tree.heading("curso",text="Curso")
        self.tree.column("id_aluno",width="50",anchor="center")
        self.tree.column("nome",width="220")
        self.tree.column("email",width="250")
        self.tree.column("curso",width="170")

        scroll = ttk.Scrollbar(frame_tabela,orient="vertical",command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left",fill="both",expand=True)
        scroll.pack(side="right",fill="y")
        self.tree.bind("<<TreeviewSelect>>",self.ao_selecionar)
        self.listar()

    def iniciar_loading(self,text="Carregando..."):
            self.lbl_status.config(text=text)
            self.loading.pack(after=self.lbl_status,anchor="w",padx=10,pady=2)
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

    def executar(self,texto,tarefa,ao_concluir):
            self.iniciar_loading(texto)

            def worker():
                try:
                    resultado = tarefa()
                    erro = None
                except api.ApiError as e:
                    resultado, erro = None, str(e)
                except Exception as e:
                    resultado, erro = None, f"Erro inesperado: {e}"

                try:
                    self.after(0, lambda: self.finalizar(resultado, erro, ao_concluir))
                except RuntimeError:
                    pass
            threading.Thread(target=worker,daemon=True).start()

    def finalizar(self,resultado,erro,ao_concluir):
            if not self.winfo_exists():
                return
            self.parar_loading()
            if erro:
                messagebox.showerror("Erro",erro,parent=self)
                return
            ao_concluir(resultado)    

    def listar(self):
        self.executar("Carregando Alunos...",lambda:api.listar("alunos"),self.preencher_tabela)

    def preencher_tabela(self,alunos):
        self.tree.delete(*self.tree.get_children())
        for a in alunos or []:
            self.tree.insert("","end",values=(a.get("id_aluno"),a.get("nome"),a.get("email"),a.get("curso")))
    
    def ao_selecionar(self,_event):
        sel = self.tree.selection()
        if not sel:
            return
        id,nome,email,curso = self.tree.item(sel[0],"values")
        self.aluno_id = id
        for entry, valor in ((self.ent_nome,nome),
                             (self.ent_email,email),
                             (self.ent_curso,curso)):
            entry.delete(0,tk.END)
            entry.insert(0,valor)
    
    def dados(self):
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()
        curso = self.ent_curso.get().strip()
        if not nome or not email or not curso:
            messagebox.showwarning("Atenção","Preencha todos os campos")
            return None
        return {"nome":nome,"email":email,"curso":curso}
    
    def inserir(self):
        dados = self.dados()
        if not dados:
            return
        self.executar("Salvando aluno...",lambda:api.criar("alunos",dados),lambda resultado: self.sucesso("Aluno cadastrado com sucesso"))

    def atualizar(self):
        if not self.aluno_id:
            messagebox.showwarning("Atenção","Selecione um aluno!")
            return
        dados = self.dados()
        if not dados:
            return
        id = self.aluno_id
        self.executar("Atualizando aluno...",lambda:api.atualizar("alunos",id,dados),lambda resultado: self.sucesso("Aluno atualizado!"))

    def deletar(self):
        if not self.aluno_id:
            messagebox.showwarning("Atenção","Selecione um aluno!")
            return
        if not messagebox.askyesno("confirmar","Deseja excluir este aluno?",parent=self):
            return
        id = self.aluno_id
        self.executar("Excluindo aluno...",lambda:api.deletar("alunos",id),lambda resultado: self.sucesso())
    
    def sucesso(self,mensagem=None):
        if mensagem:
            messagebox.showinfo("Sucesso",mensagem,parent=self)
        self.limpar()
        self.listar()

    def limpar(self):
        self.aluno_id = None
        self.ent_nome.delete(0,tk.END)
        self.ent_email.delete(0,tk.END)
        self.ent_curso.delete(0,tk.END)
        self.tree.selection_remove(self.tree.selection())