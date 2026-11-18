from database import obter_conexao

# Colunas públicas: nunca devolver o hash da senha para o cliente.
COLUNAS_PUBLICAS = "id_bibliotecario, nome, email, data_cadastro"


class BibliotecarioModel:
    @classmethod
    def listar(cls):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(f"SELECT {COLUNAS_PUBLICAS} FROM bibliotecarios")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_id(cls, id_bibliotecario):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                f"SELECT {COLUNAS_PUBLICAS} FROM bibliotecarios WHERE id_bibliotecario = %s",
                (id_bibliotecario,)
            )
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def buscar_por_email(cls, email):
        """Busca incluindo o hash da senha. Uso interno (login) apenas."""
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM bibliotecarios WHERE email = %s", (email,))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def criar(cls, nome, email, senha_hash):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO bibliotecarios(nome, email, senha) VALUES(%s, %s, %s)",
                (nome, email, senha_hash)
            )
            conexao.commit()
            return {
                "id_bibliotecario": cursor.lastrowid,
                "nome": nome,
                "email": email
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def atualizar(cls, id_bibliotecario, nome, email, senha_hash=None):
        """Atualiza nome e email; a senha só muda se senha_hash for informado."""
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            if senha_hash:
                cursor.execute(
                    "UPDATE bibliotecarios SET nome = %s, email = %s, senha = %s "
                    "WHERE id_bibliotecario = %s",
                    (nome, email, senha_hash, id_bibliotecario)
                )
            else:
                cursor.execute(
                    "UPDATE bibliotecarios SET nome = %s, email = %s "
                    "WHERE id_bibliotecario = %s",
                    (nome, email, id_bibliotecario)
                )
            conexao.commit()
            return {
                "id_bibliotecario": id_bibliotecario,
                "nome": nome,
                "email": email
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conexao.close()

    @classmethod
    def excluir(cls, id_bibliotecario):
        conexao = obter_conexao()
        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM bibliotecarios WHERE id_bibliotecario = %s",
                (id_bibliotecario,)
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
