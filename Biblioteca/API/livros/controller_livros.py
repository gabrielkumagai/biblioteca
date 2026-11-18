from flask import request, jsonify
from mysql.connector.errors import IntegrityError
from .model_livros import LivroModel


def validar_dados(dados):
    if not isinstance(dados, dict):
        return "Corpo da requisição vazio ou inválido", None

    for campo in ("titulo", "autor"):
        valor = dados.get(campo)
        if not valor or not str(valor).strip():
            return f"O campo '{campo}' é obrigatório", None

    editora = dados.get("editora")
    editora = str(editora).strip() if editora else None

    exemplares = dados.get("exemplares", 1)
    if isinstance(exemplares, bool) or not isinstance(exemplares, int) or exemplares < 0:
        return "O campo 'exemplares' deve ser um número inteiro maior ou igual a 0", None

    livro = {
        "titulo": str(dados["titulo"]).strip(),
        "editora": editora or None,
        "autor": str(dados["autor"]).strip(),
        "exemplares": exemplares
    }
    return None, livro


class LivroController:
    @staticmethod
    def listar():
        livros = LivroModel.listar()
        return jsonify(livros), 200

    @staticmethod
    def buscar(id_livro):
        livro = LivroModel.buscar_por_id(id_livro)
        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify(livro), 200

    @staticmethod
    def criar():
        erro, livro = validar_dados(request.get_json(silent=True))
        if erro:
            return jsonify({"erro": erro}), 400

        novo = LivroModel.criar(
            livro["titulo"],
            livro["editora"],
            livro["autor"],
            livro["exemplares"]
        )
        return jsonify(novo), 201

    @staticmethod
    def atualizar(id_livro):
        erro, livro = validar_dados(request.get_json(silent=True))
        if erro:
            return jsonify({"erro": erro}), 400

        if not LivroModel.buscar_por_id(id_livro):
            return jsonify({"erro": "Livro não encontrado"}), 404

        atualizado = LivroModel.atualizar(
            id_livro,
            livro["titulo"],
            livro["editora"],
            livro["autor"],
            livro["exemplares"]
        )
        return jsonify(atualizado), 200

    @staticmethod
    def excluir(id_livro):
        try:
            excluido = LivroModel.excluir(id_livro)
        except IntegrityError:
            return jsonify({"erro": "Não é possível excluir: o livro possui empréstimos registrados"}), 409
        if not excluido:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify({"mensagem": "Livro excluído com sucesso"}), 200
