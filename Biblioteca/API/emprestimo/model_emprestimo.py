from database import obter_conexao


class RegraEmprestimoError(Exception):

    def __init__(self, mensagem, status):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


SELECT_EMPRESTIMO = (
    "SELECT e.id_emprestimo, e.data, e.data_devolucao, "
    "e.id_aluno, a.nome AS nome_aluno, "
    "e.id_livro, l.titulo AS titulo_livro, "
    "e.id_bibliotecario, b.nome AS nome_bibliotecario "
    "FROM emprestimo e "
    "JOIN alunos a ON a.id_aluno = e.id_aluno "
    "JOIN livros l ON l.id_livro = e.id_livro "
    "JOIN bibliotecarios b ON b.id_bibliotecario = e.id_bibliotecario"
)


class EmprestimoModel:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(SELECT_EMPRESTIMO + " ORDER BY e.id_emprestimo")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_emprestimo):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                SELECT_EMPRESTIMO + " WHERE e.id_emprestimo = %s",
                (id_emprestimo,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, id_aluno, id_livro, id_bibliotecario):
        """Registra um empréstimo se houver exemplar disponível.

        Levanta RegraEmprestimoError (404) se aluno, livro ou bibliotecário
        não existirem, e (409) se todos os exemplares estiverem emprestados.
        Retorna o id do empréstimo criado.
        """
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()

            cursor.execute("SELECT 1 FROM alunos WHERE id_aluno = %s", (id_aluno,))
            if not cursor.fetchone():
                raise RegraEmprestimoError("Aluno não encontrado", 404)

            cursor.execute(
                "SELECT 1 FROM bibliotecarios WHERE id_bibliotecario = %s",
                (id_bibliotecario,)
            )
            if not cursor.fetchone():
                raise RegraEmprestimoError("Bibliotecário não encontrado", 404)

            # FOR UPDATE trava a linha do livro até o commit, evitando que
            # dois empréstimos simultâneos usem o último exemplar.
            cursor.execute(
                "SELECT exemplares FROM livros WHERE id_livro = %s FOR UPDATE",
                (id_livro,)
            )
            livro = cursor.fetchone()
            if not livro:
                raise RegraEmprestimoError("Livro não encontrado", 404)

            cursor.execute(
                "SELECT COUNT(*) FROM emprestimo "
                "WHERE id_livro = %s AND data_devolucao IS NULL",
                (id_livro,)
            )
            emprestados = cursor.fetchone()[0]
            if emprestados >= livro[0]:
                raise RegraEmprestimoError("Não há exemplares disponíveis deste livro", 409)

            cursor.execute(
                "INSERT INTO emprestimo(id_aluno, id_bibliotecario, id_livro) "
                "VALUES(%s, %s, %s)",
                (id_aluno, id_bibliotecario, id_livro)
            )
            conexao.commit()
            return cursor.lastrowid
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def devolver(cls, id_emprestimo):
        """Marca o empréstimo como devolvido hoje.

        Levanta RegraEmprestimoError (404) se não existir e (409) se já
        tiver sido devolvido.
        """
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT data_devolucao FROM emprestimo "
                "WHERE id_emprestimo = %s FOR UPDATE",
                (id_emprestimo,)
            )
            emprestimo = cursor.fetchone()
            if not emprestimo:
                raise RegraEmprestimoError("Empréstimo não encontrado", 404)
            if emprestimo[0] is not None:
                raise RegraEmprestimoError("Este empréstimo já foi devolvido", 409)

            cursor.execute(
                "UPDATE emprestimo SET data_devolucao = CURDATE() "
                "WHERE id_emprestimo = %s",
                (id_emprestimo,)
            )
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def excluir(cls, id_emprestimo):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM emprestimo WHERE id_emprestimo = %s",
                (id_emprestimo,)
            )
            conexao.commit()
            return cursor.rowcount > 0
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()
