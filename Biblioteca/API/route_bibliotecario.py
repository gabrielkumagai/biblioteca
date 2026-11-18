from flask import Blueprint
from controller_bibliotecario import BibliotecarioController

bibliotecarios = Blueprint("bibliotecarios",__name__)

@bibliotecarios.get("/bibliotecarios")
def listar_bibliotecarios():
    return BibliotecarioController.listar()

@bibliotecarios.get("/bibliotecarios/<int:id_bibliotecario>")
def buscar_bibliotecario(id_bibliotecario):
    return BibliotecarioController.buscar(id_bibliotecario)

@bibliotecarios.post("/bibliotecarios")
def criar_bibliotecario():
    return BibliotecarioController.criar()

@bibliotecarios.put("/bibliotecarios/<int:id_bibliotecario>")
def atualizar_bibliotecario(id_bibliotecario):
    return BibliotecarioController.atualizar(id_bibliotecario)

@bibliotecarios.delete("/bibliotecarios/<int:id_bibliotecario>")
def excluir_bibliotecario(id_bibliotecario):
    return BibliotecarioController.excluir(id_bibliotecario)

@bibliotecarios.post("/bibliotecarios/login")
def login_bibliotecario():
    return BibliotecarioController.login()