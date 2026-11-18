from database import obter_conexao


class LivroModel:

    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM livros")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_livro):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM livros WHERE id_livro = %s",
                (id_livro,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, titulo, editora, autor, exemplares):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO livros(titulo, editora, autor, exemplares) "
                "VALUES(%s, %s, %s, %s)",
                (titulo, editora, autor, exemplares)
            )
            conexao.commit()
            return {
                "id_livro": cursor.lastrowid,
                "titulo": titulo,
                "editora": editora,
                "autor": autor,
                "exemplares": exemplares
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def atualizar(cls, id_livro, titulo, editora, autor, exemplares):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE livros SET titulo = %s, editora = %s, autor = %s, "
                "exemplares = %s WHERE id_livro = %s",
                (titulo, editora, autor, exemplares, id_livro)
            )
            conexao.commit()
            return {
                "id_livro": id_livro,
                "titulo": titulo,
                "editora": editora,
                "autor": autor,
                "exemplares": exemplares
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def excluir(cls, id_livro):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM livros WHERE id_livro = %s",
                (id_livro,)
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
