from flask import Blueprint
from .controller_livros import LivroController

livros_bp = Blueprint("livros", __name__)


@livros_bp.get("/livros")
def listar_livros():
    return LivroController.listar()


@livros_bp.get("/livros/<int:id_livro>")
def buscar_livro(id_livro):
    return LivroController.buscar(id_livro)


@livros_bp.post("/livros")
def criar_livro():
    return LivroController.criar()


@livros_bp.put("/livros/<int:id_livro>")
def atualizar_livro(id_livro):
    return LivroController.atualizar(id_livro)


@livros_bp.delete("/livros/<int:id_livro>")
def excluir_livro(id_livro):
    return LivroController.excluir(id_livro)
