import sqlite3

def create_db_and_table():
    # Conectar ao banco de daods (ou criar se não existir)
    connection = sqlite3.connect('libary.db')

    # Criar um cursor para executar comandos SQL
    cursor = connection.cursor()

    # Criação da tabela books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Disponível'
        )
    ''')
    
    # Executar um comando SQL para vizualizar as tabelas existentes
    cursor.execute( "SELECT name FROM sqlite_master WHERE type='table'; ")
    tables = cursor.fetchall()
    print("Tabela no banco de dados: ")
    for table in tables:
        print(table[0])

    # Se desejar visualizar o conteudo de uma tabela específica
    cursor.execute("SELECT * FROM books;")
    rows = cursor.fetchall()
    print("\nConteudo da tabela 'books': ")
    for row in rows:
        print(row)

    # Fechar a conexão com o banco de dados
    connection.commit()
    connection.close()

create_db_and_table()
print("Banco de dados e tabela criados com sucesso")