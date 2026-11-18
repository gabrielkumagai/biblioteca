from flask import request,jsonify
from mysql.connector.errors import IntegrityError
from aluno_model import AlunoModel

def validar_dados(dados):
    if not isinstance(dados, dict):
        return "Corpo da requisição vazio ou inválido"
    for campo in("nome","email","curso"):
        valor = dados.get(campo)
        if not valor or not str(valor).strip():
            return f"O campo '{campo}' é obrigatório"
    return None

class AlunoController:
    @staticmethod
    def listar():
        alunos = AlunoModel.listar()
        return jsonify(alunos),200
    
    @staticmethod
    def buscar(id_aluno):
        aluno = AlunoModel.buscar_por_id(id_aluno)
        if not aluno:
            return jsonify({"erro":"Aluno não encontrado"}),404
        return jsonify(aluno),200
    
    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro":erro}),400
        
        try:
            aluno = AlunoModel.criar(
                str(dados["nome"]).strip(),
                str(dados["email"]).strip(),
                str(dados["curso"]).strip()
            )
        except IntegrityError:
            return jsonify({"erro":"Email já cadastrado"}),409
        return jsonify(aluno),201
    
    @staticmethod
    def atualizar(id_aluno):
        dados = request.get_json(silent=True)
        erro = validar_dados(dados)
        if erro:
            return jsonify({"erro":erro}),400

        if not AlunoModel.buscar_por_id(id_aluno):
            return jsonify({"erro":"Aluno não encontrado"}),404

        try:
            aluno = AlunoModel.atualizar(
                id_aluno,
                str(dados["nome"]).strip(),
                str(dados["email"]).strip(),
                str(dados["curso"]).strip()
            )
        except IntegrityError:
            return jsonify({"erro":"Email já cadastrado"}),409
        return jsonify(aluno),200
    
    @staticmethod
    def excluir(id_aluno):
        try:
            excluido = AlunoModel.excluir(id_aluno)
        except IntegrityError:
            return jsonify({"erro": "Não é possível excluir: o aluno possui empréstimos registrados"}),409
        if not excluido:
            return jsonify({"erro":"Aluno não encontrado"}),404
        return jsonify({"mensagem":"Aluno excluido com sucesso"}),200