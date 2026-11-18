from flask import request,jsonify
from mysql.connector.errors import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash
from auth import gerar_token
from model_bibliotecario import BibliotecarioModel

def campo_preenchido(dados, campo):
    valor = dados.get(campo)
    return bool(valor) and bool(str(valor).strip())

class BibliotecarioController:
    @staticmethod
    def validar_dados(dados, senha_obrigatoria=True):
        """Valida nome, email e senha. No update a senha é opcional."""
        if not isinstance(dados, dict):
            return "Corpo da requisição vazio ou inválido"
        campos = ("nome","email","senha") if senha_obrigatoria else ("nome","email")
        for campo in campos:
            if not campo_preenchido(dados, campo):
                return f"O campo '{campo}' é obrigatório"
        return None

    @staticmethod
    def listar():
        bibliotecarios = BibliotecarioModel.listar()
        return jsonify(bibliotecarios),200
    
    @staticmethod
    def buscar(id_bibliotecario):
        bibliotecario = BibliotecarioModel.buscar_por_id(id_bibliotecario)
        if not bibliotecario:
            return jsonify({"erro":"Bibliotecario não encontrado!"}),404
        return jsonify(bibliotecario),200
    
    @staticmethod
    def criar():
        dados = request.get_json(silent=True)
        erro = BibliotecarioController.validar_dados(dados)
        if erro:
            return jsonify({"erro":erro}),400
        try:
            bibliotecario = BibliotecarioModel.criar(
                str(dados["nome"]).strip(),
                str(dados["email"]).strip(),
                generate_password_hash(str(dados["senha"]))
            )
        except IntegrityError:
            return jsonify({"erro":"Email já cadastrado!"}),409
        return jsonify(bibliotecario),201
    
    @staticmethod
    def atualizar(id_bibliotecario):
        """Atualiza nome e email. Se 'senha' vier no corpo, troca a senha também."""
        dados = request.get_json(silent=True)
        erro = BibliotecarioController.validar_dados(dados, senha_obrigatoria=False)
        if erro:
            return jsonify({"erro":erro}),400

        if not BibliotecarioModel.buscar_por_id(id_bibliotecario):
            return jsonify({"erro":"Bibliotecario não encontrado!"}),404

        senha_hash = None
        if campo_preenchido(dados, "senha"):
            senha_hash = generate_password_hash(str(dados["senha"]))
        try:
            bibliotecario = BibliotecarioModel.atualizar(
                id_bibliotecario,
                str(dados["nome"]).strip(),
                str(dados["email"]).strip(),
                senha_hash
            )
        except IntegrityError:
            return jsonify({"erro":"Email já cadastrado!"}),409
        return jsonify(bibliotecario),200

    @staticmethod
    def excluir(id_bibliotecario):
        try:
            excluido = BibliotecarioModel.excluir(id_bibliotecario)
        except IntegrityError:
            return jsonify({"erro": "Não é possível excluir: o bibliotecário possui empréstimos registrados"}),409
        if not excluido:
            return jsonify({"erro":"Bibliotecario não encontrado"}),404
        return jsonify({"mensagem":"Bibliotecario excluido com sucesso"}),200
    
    @staticmethod
    def login():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict) or not campo_preenchido(dados, "email") or not campo_preenchido(dados, "senha"):
            return jsonify({"erro":"Informe email e senha"}),400

        bibliotecario = BibliotecarioModel.buscar_por_email(str(dados["email"]).strip())

        if not bibliotecario or not check_password_hash(bibliotecario["senha"],str(dados["senha"])):
            return jsonify({"erro":"Email ou senha inválidos!"}),401
        token = gerar_token(bibliotecario["id_bibliotecario"],bibliotecario["email"])
        return jsonify({
            "token" : token,
            "bibliotecario": {
                "id_bibliotecario": bibliotecario["id_bibliotecario"],
                "nome": bibliotecario["nome"],
                "email": bibliotecario["email"]
            }
        }),200
