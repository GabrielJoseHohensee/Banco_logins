import tkinter as tk
from tkinter import ttk

def aplicar_estilo():
    # Exemplo de customização de estilo
    style = ttk.Style()

    # Definir tema
    style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic' são opções comuns

    # Customizar botões
    style.configure('TButton', background='lightblue', foreground='black', font=('Arial', 10, 'bold'))

    # Customizar labels
    style.configure('TLabel', background='lightgray', font=('Arial', 10))

    # Customizar Entry (campos de texto)
    style.configure('TEntry', padding=5, background='white')