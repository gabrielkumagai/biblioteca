import requests

BASE_URL = "http://127.0.0.1:5000/biblioteca"
TIMEOUT = 5

class ApiError(Exception):
    "Erro amigável"
    pass

def request(method,path,**kwargs):
    try:
        resp = requests.request(method,f"{BASE_URL}{path}",timeout=TIMEOUT,**kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else None
    except requests.exceptions.ConnectionError:
        raise ApiError("Não foi possível conectar a API. Ela está rodando?")
    except requests.exceptions.Timeout:
        raise ApiError("Tempo de resposta esgotado.")
    except requests.exceptions.HTTPError:
        raise ApiError(mensagem_de_erro(resp))
    except ValueError:
        raise ApiError("A API retornou uma resposta inválida")

def mensagem_de_erro(resp):
    """Extrai o campo 'erro' do JSON da API; se não houver, mostra o status."""
    try:
        erro = resp.json().get("erro")
    except (ValueError, AttributeError):
        erro = None
    return erro or f"Erro {resp.status_code}: {resp.text}"

def login(email,senha):
    """Retorna {"token": ..., "bibliotecario": {...}} ou levanta ApiError."""
    return request("POST","/bibliotecarios/login",json={"email":email,"senha":senha})

def listar(recurso):
    return request("GET",f"/{recurso}")

def criar(recurso,dados):
    return request("POST",f"/{recurso}",json=dados)

def atualizar(recurso,id,dados):
    return request("PUT",f"/{recurso}/{id}",json=dados)

def deletar(recurso,id):
    return request("DELETE",f"/{recurso}/{id}")

def devolver_emprestimo(id):
    """Registra a devolução (data de hoje) de um empréstimo em aberto."""
    return request("PUT",f"/emprestimos/{id}/devolucao")