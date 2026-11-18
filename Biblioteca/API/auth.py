import os
from datetime import datetime,timedelta,timezone
from functools import wraps

import jwt
from flask import request,jsonify,g

SECRET_KEY = os.getenv("SECRET_KEY","BIBLIOTECA-FATEC")
HORAS_EXPIRACAO = 2

def gerar_token(id_bibliotecario,email):
    payload={
        "id_bibliotecario" : id_bibliotecario,
        "email" : email,
        "exp" : datetime.now(timezone.utc)+timedelta(hours=HORAS_EXPIRACAO)
    }
    return jwt.encode(payload,SECRET_KEY,algorithm="HS256")

def token_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args,**kwargs):
        cabecalho = request.headers.get("Authorization","")
        tipo, _, token = cabecalho.partition(" ")
        token = token.strip()
        if tipo != "Bearer" or not token:
            return jsonify({"erro":"Token não informado"}),401
        try:
            g.bibliotecario = jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"erro":"Token Expirado"}),401
        except jwt.InvalidTokenError:
            return jsonify({"erro":"Token inválido"}),401
        return funcao(*args,**kwargs)
    return wrapper