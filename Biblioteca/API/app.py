from flask import Flask
from route_alunos import alunos
from route_bibliotecario import bibliotecarios
from livros.route_livros import livros_bp
from emprestimo.route_emprestimo import emprestimos_bp

app = Flask(__name__)

PREFIXO = "/biblioteca"

app.register_blueprint(alunos,url_prefix=PREFIXO)
app.register_blueprint(bibliotecarios,url_prefix=PREFIXO)
app.register_blueprint(livros_bp,url_prefix=PREFIXO)
app.register_blueprint(emprestimos_bp,url_prefix=PREFIXO)

if __name__ == "__main__":
    app.run(debug=True)