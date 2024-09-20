import json
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from usuario import buscar_usuario


# Nome do arquivo do banco de dados e da planilha Excel
db_file = 'biblioteca.db'
excel_file = 'livros.xlsx'

# Adicionar a coluna 'borrower' manualmente, se ainda não existir
def add_borrower_column():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE books ADD COLUMN alugado TEXT DEFAULT NULL")
            conn.commit()
            print("Coluna 'alugado' adicionada com sucesso.")
        except sqlite3.OperationalError as e:
            print(f"Erro ao adicionar a coluna: {e}")

add_borrower_column()

# Funções para manipulação do banco de dados
def create_table():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'Não especificado',
            status TEXT NOT NULL DEFAULT 'Disponível',
            borrower TEXT DEFAULT NULL
        )''')
        conn.commit()

def add_book(title, author, year, category):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM books WHERE title = ? AND author = ?''', (title, author))
        if cursor.fetchone():
            messagebox.showerror("Erro", "Já existe um livro com o mesmo título e autor.")
        else:
            cursor.execute('''INSERT INTO books (title, author, year, category, status)
                            VALUES (?, ?, ?, ?, ?)''', (title, author, year, category, "Disponível"))
            conn.commit()
            messagebox.showinfo("Sucesso", "Livro adicionado com sucesso.")
            update_book_list()  # Atualizar a lista de livros
            export_to_excel()

def update_book_status(book_id, new_status, borrower=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        if new_status.lower() == 'alugado' and borrower:
            cursor.execute('''UPDATE books SET status = ?, borrower = ? WHERE id = ?''', (new_status, borrower, book_id))
        elif new_status.lower() == 'disponível':
            cursor.execute('''UPDATE books SET status = ?, borrower = NULL WHERE id = ?''', (new_status, book_id))
        else:
            cursor.execute('''UPDATE books SET status = ? WHERE id = ?''', (new_status, book_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Status do livro atualizado com sucesso.")
        update_book_list()  # Atualizar a lista de livros
        export_to_excel()

def remove_book(book_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM books WHERE id = ?''', (book_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Livro removido com sucesso.")
        update_book_list()  # Atualizar a lista de livros
        export_to_excel()

# Pesquisar o livro
def search_books():
    search_term = search_entry.get()
    if search_term:
        # Limpa a lista existente
        for row in tree.get_children():
            tree.delete(row)

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                           ('%' + search_term + '%', '%' + search_term + '%'))
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)

    else:
        update_book_list()  # Se a pesquisa estiver vazia, atualiza a lista completa

def export_to_excel():
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql_query("SELECT * FROM books", conn)
    df.to_excel(excel_file, index=False, engine='openpyxl')

# Funções para a interface gráfica
def add_book_gui():
    title = simpledialog.askstring("Título", "Digite o título do livro:")
    author = simpledialog.askstring("Autor", "Digite o nome do autor:")
    year = simpledialog.askinteger("Ano", "Digite o ano do livro:")
    category = simpledialog.askstring("Categoria", "Digite a categoria do livro:")
    if title and author and year and category:
        add_book(title, author, year, category)

def update_book_status_gui():
    book_id = simpledialog.askinteger("ID do Livro", "Digite o ID do livro:")
    
    if book_id:
        # Cria uma janela de diálogo para selecionar o status
        status_window = tk.Toplevel(root)
        status_window.title("Atualizar Status")
        
        # Lista de opções para o status
        status_options = ["Disponível", "Alugado"]
        
        # Cria um Combobox para selecionar o status
        status_label = tk.Label(status_window, text="Selecione o status do livro:")
        status_label.pack(padx=10, pady=5)
        status_combobox = ttk.Combobox(status_window, values=status_options)
        status_combobox.pack(padx=10, pady=5)
        
        # Adiciona um campo para o nome do emprestador
        borrower_label = tk.Label(status_window, text="CPF do locatário (deixe em branco se disponível):")
        borrower_label.pack(padx=10, pady=5)
        borrower_entry = tk.Entry(status_window)
        borrower_entry.pack(padx=10, pady=5)

        def on_update():
            new_status = status_combobox.get()
            borrower_cpf = borrower_entry.get()
            
            # Buscar informações do locatário
            if new_status.lower() == 'emprestado' and borrower_cpf:
                usuario_info = buscar_usuario(int(borrower_cpf))
                borrower = usuario_info[1] if usuario_info else 'Desconhecido'
                print("*"*50)
                print(borrower)
                print(usuario_info)
                print(json.dumps(usuario_info))
                print(json.dumps(usuario_info)[1])
            else:
                borrower = None
            
            if new_status:
                update_book_status(book_id, new_status, borrower)
                status_window.destroy()

        update_button = tk.Button(status_window, text="Atualizar", command=on_update)
        update_button.pack(padx=10, pady=10)

def remove_book_gui():
    book_id = simpledialog.askinteger("ID do Livro", "Digite o ID do livro:")
    if book_id:
        remove_book(book_id)

def export_to_excel_gui():
    export_to_excel()

def update_book_list():
    # Limpa a lista existente
    for row in tree.get_children():
        tree.delete(row)
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

def main_gui():
    global tree, root, search_entry   # Global para atualizar a lista de livros
    
    root = tk.Tk()
    root.title("Gerenciador de Livros")

    # Estilo
    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#0078D7", foreground="white")
    style.map("TButton", background=[("active", "#0056A3")])

    # Frame para Pesquisa
    frame_search = tk.Frame(root)
    frame_search.pack(pady=10)

    search_label = tk.Label(frame_search, text="Pesquisar Livro:")
    search_label.pack(side=tk.LEFT)

    search_entry = tk.Entry(frame_search)
    search_entry.pack(side=tk.LEFT, padx=5)

    
    # Frame para Botões
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)

    tk.Label(root, text="Gerenciador de Livros", font=("Arial", 16)).pack(pady=10)

    tk.Button(frame_buttons, text="Adicionar Livro", command=add_book_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="Atualizar Status", command=update_book_status_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="Remover Livro", command=remove_book_gui).pack(side=tk.LEFT, padx=5)
    search_button = tk.Button(frame_search, text="Buscar", command=search_books)
    search_button.pack(side=tk.LEFT, padx=5)


    # Exibição de livros com scrollbar
    frame_tree = tk.Frame(root)
    frame_tree.pack(expand=True, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(frame_tree)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    columns = ("id", "title", "author", "year", "category", "status", "borrower")
    tree = ttk.Treeview(frame_tree, columns=columns, show='headings', yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)
    tree.pack(expand=True, fill=tk.BOTH)

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100)

    update_book_list()  # Atualiza a lista de livros ao iniciar
    
    root.mainloop()

if __name__ == "__main__":
    create_table()
    main_gui()
