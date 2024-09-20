import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from biblioteca import main_gui as biblioteca_gui
from usuario import main_gui as usuario_gui

def open_biblioteca():
    root.destroy()  # Fecha a janela principal
    biblioteca_gui()  # Abre a janela da biblioteca

def open_usuario():
    root.destroy()  # Fecha a janela principal
    usuario_gui()  # Abre a janela de criação de usuários

def main():
    global root
    root = tk.Tk()
    root.title("Tela Principal")
    root.geometry("500x400")  # Aumentando o tamanho da janela
    root.configure(bg="#f0f0f0")

    # Carregar imagem de fundo
    background_image = Image.open("biblioteca.jpg")  # Altere para o nome da sua imagem
    background_image = background_image.resize((500, 400), Image.LANCZOS)  # Use LANCZOS para manter a qualidade
    background_photo = ImageTk.PhotoImage(background_image)

    # Label para a imagem de fundo
    background_label = tk.Label(root, image=background_photo)
    background_label.image = background_photo  # Manter uma referência da imagem
    background_label.place(relwidth=1, relheight=1)  # Preencher toda a janela

    # Estilo
    style = ttk.Style()
    style.configure("TButton", padding=10, relief="flat", background="#0078D7", foreground="white")
    style.map("TButton", background=[("active", "#0056A3")])

    # Título
    title_label = tk.Label(background_label, text="Bem-vindo ao Sistema de Biblioteca", font=("Arial", 16), bg="#f0f0f0")
    title_label.pack(pady=20)

    # Frame para os botões
    button_frame = tk.Frame(background_label, bg="#f0f0f0")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Abrir Biblioteca", command=open_biblioteca).pack(pady=5, padx=20, side=tk.LEFT)
    tk.Button(button_frame, text="Abrir Criação de Usuários", command=open_usuario).pack(pady=5, padx=20, side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    main()
