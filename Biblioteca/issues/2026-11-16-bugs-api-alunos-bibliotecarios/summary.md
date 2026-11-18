# Resolution: Bugs nas APIs de alunos, bibliotecários e autenticação

## Root Cause
- Indentação errada em `validar_dados` (alunos).
- Uso de `rowcount` do UPDATE para detectar registro inexistente.
- `@classmethod` ausente em `BibliotecarioModel.atualizar`.
- `jsonify` recebendo um set.
- Falta de validação de entrada no login.
- `SELECT *` em consultas cujo resultado vai para o cliente.
- Parsing frágil do header `Authorization`.

## Fix Applied
- `API/aluno_controller.py`: `return None` fora do loop; corpo precisa ser dict; `atualizar` checa existência com `buscar_por_id` antes do UPDATE; chave `"Erro"` → `"erro"`; removido import `Blueprint` sem uso.
- `API/aluno_model.py`: `atualizar` não usa mais `rowcount`.
- `API/model_bibliotecario.py`: `listar`/`buscar_por_id` selecionam só `id_bibliotecario, nome, email, data_cadastro`; `atualizar` com `@classmethod`, sem `rowcount`, e parâmetro opcional `senha_hash`.
- `API/controller_bibliotecario.py`: senha opcional no update (troca só se enviada); `jsonify(bibliotecario)`; existência checada antes do UPDATE; `login` valida email/senha (400) e devolve o bibliotecário sem `senha`; `@staticmethod` em `listar`; chave `"Erro"` → `"erro"`.
- `API/auth.py`: header lido com `partition(" ")`; exige tipo `Bearer` e token não vazio.

## Prevention
- Todos os cenários do report foram executados com o test client do Flask contra um MariaDB temporário criado a partir de `API/banco.sql` (alunos, bibliotecários, login, exclusão com empréstimo, header de token).
- Pendente: transformar esse roteiro em testes automatizados (`pytest`) no repositório.

## Status
RESOLVED
