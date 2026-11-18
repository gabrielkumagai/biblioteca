- **API** (`API/`): Flask, com os dados guardados no MySQL. Roda em `http://127.0.0.1:5000/biblioteca`.
- **Interface** (`GUI/`): Tkinter. Conversa com a API e exige login de bibliotecário.

## Requisitos

- Python 3.14
- MySQL/MariaDB. MySQL do XAMPP (`/opt/lampp`), com usuário `root` sem senha.


## Instalação

Na pasta do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Ligar o MySQL

```bash
sudo systemctl stop mariadb
sudo /opt/lampp/lampp startmysql
```

Para conferir se ele subiu, rode `ls /opt/lampp/var/mysql/mysql.sock`. Se o arquivo existir, o servidor está no ar.

## 2. Criar o banco

```bash
/opt/lampp/bin/mysql -u root < API/banco.sql
```

## 3. Ligar a API (terminal 1)

```bash
source .venv/bin/activate
cd API
python app.py
```

Deixe esse terminal aberto. A API está pronta quando aparecer `Running on http://127.0.0.1:5000`.

## 4. Abrir a interface (terminal 2)

```bash
source .venv/bin/activate
cd GUI
python main.py
```

## 5. Primeiro acesso

Na tela de login, clique em **Criar conta**, cadastre um bibliotecário e entre com o email e a senha dele.

## Configuração do banco

A conexão fica em `API/database.py`:

```python
host="localhost", user="root", password="", database="biblioteca"
```

Se usar outro servidor ou usuário, altere esse arquivo.

## Rotas da API

Todas começam com `/biblioteca`.

| Método | Rota | Descrição |
|---|---|---|
| GET, POST | `/alunos` | Listar / criar aluno (`nome`, `email`, `curso`) |
| GET, PUT, DELETE | `/alunos/<id>` | Buscar / atualizar / excluir aluno |
| GET, POST | `/livros` | Listar / criar livro (`titulo`, `autor`, `editora`, `exemplares`) |
| GET, PUT, DELETE | `/livros/<id>` | Buscar / atualizar / excluir livro |
| GET, POST | `/bibliotecarios` | Listar / criar bibliotecário (`nome`, `email`, `senha`) |
| GET, PUT, DELETE | `/bibliotecarios/<id>` | Buscar / atualizar / excluir (no PUT a senha é opcional) |
| POST | `/bibliotecarios/login` | Login (`email`, `senha`), devolve um token e os dados do bibliotecário |
| GET, POST | `/emprestimos` | Listar / registrar empréstimo (`id_aluno`, `id_livro`, `id_bibliotecario`) |
| GET, DELETE | `/emprestimos/<id>` | Buscar / excluir empréstimo |
| PUT | `/emprestimos/<id>/devolucao` | Registrar a devolução com a data de hoje |

Exemplo:

```bash
curl -X POST http://127.0.0.1:5000/biblioteca/livros \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Dom Casmurro", "autor": "Machado de Assis", "exemplares": 2}'
```
