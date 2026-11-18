from flask import request, jsonify
from .model_emprestimo import EmprestimoModel, RegraEmprestimoError


def validar_dados(dados):
    if not isinstance(dados, dict):
        return "Corpo da requisição vazio ou inválido"
    for campo in ("id_aluno", "id_livro", "id_bibliotecario"):
        valor = dados.get(campo)
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            return f"O campo '{campo}' é obrigatório e deve ser um número inteiro positivo"
    return None


class EmprestimoController:
    @staticmethod
    def listar():
        return jsonify(EmprestimoModel.listar()), 200

    @staticmethod
    def buscar(id_emprestimo):
        emprestimo = EmprestimoModel.buscar_por_id(id_emprestimo)
        if not emprestimo:
            return jsonify({"erro": "Empréstimo não encontrado"}), 404
        return jsonify(emprestimo), 200

    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro": erro}), 400
        try:
            id_emprestimo = EmprestimoModel.criar(
                dados["id_aluno"],
                dados["id_livro"],
                dados["id_bibliotecario"]
            )
        except RegraEmprestimoError as e:
            return jsonify({"erro": e.mensagem}), e.status
        return jsonify(EmprestimoModel.buscar_por_id(id_emprestimo)), 201

    @staticmethod
    def devolver(id_emprestimo):
        try:
            EmprestimoModel.devolver(id_emprestimo)
        except RegraEmprestimoError as e:
            return jsonify({"erro": e.mensagem}), e.status
        return jsonify(EmprestimoModel.buscar_por_id(id_emprestimo)), 200

    @staticmethod
    def excluir(id_emprestimo):
        if not EmprestimoModel.excluir(id_emprestimo):
            return jsonify({"erro": "Empréstimo não encontrado"}), 404
        return jsonify({"mensagem": "Empréstimo excluído com sucesso"}), 200
