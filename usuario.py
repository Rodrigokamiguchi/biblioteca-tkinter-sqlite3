import sqlite3
import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import re

# Nome do arquivo do banco de dados e da planilha Excel
db_file = 'usuarios.db'
excel_file = 'usuarios.xlsx'

# Funções para manipulação do banco de dados
def create_table():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            cpf TEXT NOT NULL
        )''')
        conn.commit()

def add_user(nome, email, telefone, cpf):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM usuarios WHERE cpf = ?''', (cpf,))
        if cursor.fetchone():
            messagebox.showerror("Erro", "Já existe um usuário com esse cpf.")
        else:
            cursor.execute('''INSERT INTO usuarios (nome, email, telefone, cpf)
                            VALUES (?, ?, ?, ?)''', (nome, email, telefone, cpf))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso.")
            update_user_list()  # Atualizar a lista de usuários
            export_to_excel()

def update_user(user_id, new_name, new_email, new_phone):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE usuarios SET nome = ?, email = ?, telefone = ? WHERE id = ?''', 
                       (new_name, new_email, new_phone, user_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso.")
        update_user_list()  # Atualizar a lista de usuários
        export_to_excel()

def remove_user(user_id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM usuarios WHERE id = ?''', (user_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário removido com sucesso.")
        update_user_list()  # Atualizar a lista de usuários
        export_to_excel()

def export_to_excel():
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql_query("SELECT * FROM usuarios", conn)
    df.to_excel(excel_file, index=False, engine='openpyxl')

def validar_cpf(cpf):
    # Remover caracteres não numéricos e espaços extras
    cpf = re.sub(r'\D', '', cpf).strip()

    # Verificar se tem exatamente 11 dígitos
    if len(cpf) != 11:
        return False

    # Verificar se todos os dígitos são iguais, o que torna o CPF inválido
    if cpf == cpf[0] * 11:
        return False

    # Função auxiliar para calcular cada dígito verificador
    def calcular_digito(cpf, peso_inicial):
        soma = sum(int(cpf[i]) * (peso_inicial - i) for i in range(peso_inicial - 1))
        digito = (soma * 10) % 11
        return 0 if digito == 10 else digito

    # Verificar primeiro dígito verificador
    if calcular_digito(cpf, 10) != int(cpf[9]):
        return False

    # Verificar segundo dígito verificador
    if calcular_digito(cpf, 11) != int(cpf[10]):
        return False

    return True

def buscar_usuario(cpf):
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"O arquivo {db_file} não foi encontrado.")

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))
        return cursor.fetchone()
    
# Funções para a interface gráfica
def add_user_gui():
    nome = simpledialog.askstring("Nome", "Digite o nome do usuário:")
    email = simpledialog.askstring("Email", "Digite o email do usuário:")
    telefone = simpledialog.askstring("Telefone", "Digite o telefone do usuário:")
    cpf = simpledialog.askstring("CPF", "Digite o cpf do usuário:")
    if nome and email and telefone:
        add_user(nome, email, telefone, cpf)

def update_user_gui():
    user_id = simpledialog.askinteger("ID do Usuário", "Digite o ID do usuário:")
    if user_id:
        new_name = simpledialog.askstring("Novo Nome", "Digite o novo nome do usuário:")
        new_email = simpledialog.askstring("Novo Email", "Digite o novo email do usuário:")
        new_phone = simpledialog.askstring("Novo Telefone", "Digite o novo telefone do usuário:")
        if new_name and new_email and new_phone:
            update_user(user_id, new_name, new_email, new_phone)

def remove_user_gui():
    user_id = simpledialog.askinteger("ID do Usuário", "Digite o ID do usuário:")
    if user_id:
        remove_user(user_id)

def export_to_excel_gui():
    export_to_excel()

def update_user_list():
    # Limpa a lista existente
    for row in tree.get_children():
        tree.delete(row)
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
def return_to_main():
    root.destroy()
    import main  # Importa a função main apenas quando necessário
    main.main()  # Chama a função para iniciar a tela principal


# Interface gráfica com tkinter
def main_gui():
    global tree, root  # Global para atualizar a lista de usuários

    root = tk.Tk()
    root.title("Gerenciador de Usuários")

    # Definindo as colunas antes de usar
    columns = ("id", "nome", "email", "telefone", "cpf")
    
    # Botões
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)

    tk.Button(frame_buttons, text="Adicionar Usuário", command=add_user_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="Atualizar Usuário", command=update_user_gui).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_buttons, text="Remover Usuário", command=remove_user_gui).pack(side=tk.LEFT, padx=5)

    # Botão de Retorno
    tk.Button(frame_buttons, text="Voltar para Tela Principal", command=return_to_main).pack(side=tk.LEFT, padx=5)
              
    # Exibição de usuários com scrollbar
    scrollbar = tk.Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(root, columns=columns, show='headings', yscrollcommand=scrollbar.set)
    scrollbar.config(command=tree.yview)
    tree.pack(expand=True, fill=tk.BOTH)

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=150)

    update_user_list()  # Atualiza a lista de usuários ao iniciar

    root.mainloop()


if __name__ == "__main__":
    create_table()
    main_gui()
