# Issue: Bugs nas APIs de alunos, bibliotecários e autenticação

## Summary
Validações incompletas, erros 500 em entradas comuns, 404 falso no update e vazamento do hash de senha.

## Impact
- Clientes da API (GUI Tkinter) recebem 500 em vez de 400/404.
- `PUT /bibliotecarios/<id>` nunca funcionava.
- Hash da senha dos bibliotecários exposto em `GET /bibliotecarios`, `GET /bibliotecarios/<id>` e no login.
- Severidade: alta para o vazamento de hash e o PUT quebrado; média para o restante.

## Reproduction
1. `POST /biblioteca/alunos` com `{"nome": "Ana"}` → 500 (KeyError), esperado 400.
2. `PUT /biblioteca/alunos/1` com os mesmos dados já salvos → 404 "Aluno não encontrado".
3. `PUT /biblioteca/bibliotecarios/1` com qualquer corpo → 500 (TypeError).
4. `GET /biblioteca/bibliotecarios` → resposta contém o campo `senha`.
5. `POST /biblioteca/bibliotecarios/login` sem corpo → 500.
6. Rota com `@token_obrigatorio` e header `Authorization: Bearer` → 500 (IndexError).

## Investigation
- `API/aluno_controller.py` `validar_dados`: `return None` dentro do `for`; só `nome` era validado.
- `API/aluno_model.py` e `API/model_bibliotecario.py` `atualizar`: usavam `cursor.rowcount == 0` como "não encontrado"; o MySQL retorna 0 quando nenhum valor muda.
- `API/model_bibliotecario.py` `atualizar`: faltava `@classmethod`, deslocando os argumentos.
- `API/controller_bibliotecario.py` `atualizar`: `jsonify({bibliotecario})` cria um set de dict (unhashable); exigia `senha` mas não a gravava.
- `API/controller_bibliotecario.py` `login`: acessava `dados["email"]` sem validar.
- `API/model_bibliotecario.py`: `SELECT *` devolvia a coluna `senha`.
- `API/auth.py`: `startswith("Bearer")` sem espaço e `split(" ",1)[1]` sem checar tamanho.
