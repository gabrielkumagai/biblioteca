from flask import Blueprint
from .controller_emprestimo import EmprestimoController

emprestimos_bp = Blueprint("emprestimos", __name__)


@emprestimos_bp.get("/emprestimos")
def listar_emprestimos():
    return EmprestimoController.listar()


@emprestimos_bp.get("/emprestimos/<int:id_emprestimo>")
def buscar_emprestimo(id_emprestimo):
    return EmprestimoController.buscar(id_emprestimo)


@emprestimos_bp.post("/emprestimos")
def criar_emprestimo():
    return EmprestimoController.criar()


@emprestimos_bp.put("/emprestimos/<int:id_emprestimo>/devolucao")
def devolver_emprestimo(id_emprestimo):
    return EmprestimoController.devolver(id_emprestimo)


@emprestimos_bp.delete("/emprestimos/<int:id_emprestimo>")
def excluir_emprestimo(id_emprestimo):
    return EmprestimoController.excluir(id_emprestimo)
