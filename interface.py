import sqlite3
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os

# ----------------------------------------------------------------------------------------

# Função para gerar chave de criptografia
def gerar_chave():
    """Gera uma nova chave de criptografia e a salva em um arquivo."""
    chave = Fernet.generate_key()
    with open("chave.key", "wb") as chave_arquivo:
        chave_arquivo.write(chave)

# Função para carregar a chave de criptografia
def carregar_chave():
    """Carrega a chave de criptografia a partir do arquivo."""
    return open("chave.key", "rb").read()

# Verifica se a chave já existe, caso contrário gera uma nova
if not os.path.exists("chave.key"):
    gerar_chave()

# Conectar ao banco de dados
conn = sqlite3.connect("senhas.db")
c = conn.cursor()

# Criar tabela se não existir
c.execute('''CREATE TABLE IF NOT EXISTS senhas (
                id INTEGER PRIMARY KEY,
                plataforma TEXT NOT NULL,
                login TEXT NOT NULL,
                senha TEXT NOT NULL)''')

# Adicionar senha ao banco de dados
def adicionar_senha():
    """Adiciona uma nova senha ao banco de dados."""
    plataforma = plataforma_entry.get()
    login = login_entry.get()
    senha = senha_entry.get()

    if plataforma and login and senha:
        chave = carregar_chave()
        fernet = Fernet(chave)
        senha_encriptada = fernet.encrypt(senha.encode())

        c.execute("INSERT INTO senhas (plataforma, login, senha) VALUES (?, ?, ?)", 
                  (plataforma, login, senha_encriptada))
        conn.commit()
        messagebox.showinfo("Sucesso", "Senha adicionada com sucesso!")
        atualizar_visualizador()
    else:
        messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")

# Atualiza o visualizador com as senhas do banco de dados
def atualizar_visualizador():
    """Atualiza a tabela de senhas exibida."""
    for row in tree.get_children():
        tree.delete(row)
    
    c.execute("SELECT * FROM senhas")
    for row in c.fetchall():
        tree.insert("", "end", values=row)

# Função para exibir a senha da linha selecionada
def exibir_senha_selecionada():
    """Exibe a senha da linha selecionada em uma mensagem."""
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        senha_encriptada = item['values'][3]

        chave = carregar_chave()
        fernet = Fernet(chave)
        senha = fernet.decrypt(senha_encriptada).decode()

        messagebox.showinfo("Senha", f"A senha é: {senha}")
    else:
        messagebox.showwarning("Atenção", "Selecione uma linha para exibir a senha.")

# Função para abrir a janela de edição
def abrir_janela_edicao(id_senha, plataforma, login, senha_encriptada):
    """Abre uma nova janela para editar uma senha existente."""
    def confirmar_edicao():
        nova_plataforma = plataforma_entry.get()
        novo_login = login_entry.get()
        nova_senha = senha_entry.get()

        if nova_plataforma and novo_login and nova_senha:
            chave = carregar_chave()
            fernet = Fernet(chave)
            senha_encriptada = fernet.encrypt(nova_senha.encode())

            c.execute("UPDATE senhas SET plataforma=?, login=?, senha=? WHERE id=?", 
                      (nova_plataforma, novo_login, senha_encriptada, id_senha))
            conn.commit()
            messagebox.showinfo("Sucesso", "Senha editada com sucesso!")
            atualizar_visualizador()
            janela_edicao.destroy()
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")

    # Criar nova janela
    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Editar Senha")

    tk.Label(janela_edicao, text="Plataforma:").pack()
    plataforma_entry = tk.Entry(janela_edicao)
    plataforma_entry.pack()
    plataforma_entry.insert(0, plataforma)  # Preencher com o valor existente

    tk.Label(janela_edicao, text="Login:").pack()
    login_entry = tk.Entry(janela_edicao)
    login_entry.pack()
    login_entry.insert(0, login)  # Preencher com o valor existente

    tk.Label(janela_edicao, text="Senha:").pack()
    senha_entry = tk.Entry(janela_edicao, show="*")
    senha_entry.pack()
    # Removida a linha que exibia a senha

    tk.Button(janela_edicao, text="Confirmar", command=confirmar_edicao).pack()
    tk.Button(janela_edicao, text="Cancelar", command=janela_edicao.destroy).pack()

# Editar senha
def editar_senha():
    """Inicia o processo de edição de uma senha selecionada."""
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id_senha = item['values'][0]
        plataforma = item['values'][1]
        login = item['values'][2]
        senha_encriptada = item['values'][3]
        
        # Exibir janela de edição
        abrir_janela_edicao(id_senha, plataforma, login, senha_encriptada)
    else:
        messagebox.showwarning("Atenção", "Selecione uma senha para editar.")

# Função para excluir senha
def excluir_senha():
    """Exclui a senha selecionada do banco de dados."""
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id_senha = item['values'][0]

        # Confirmar exclusão
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir esta senha?")
        if resposta:
            c.execute("DELETE FROM senhas WHERE id=?", (id_senha,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Senha excluída com sucesso!")
            atualizar_visualizador()
    else:
        messagebox.showwarning("Atenção", "Selecione uma senha para excluir.")

# Configuração da interface
root = tk.Tk()
root.title("Gerenciador de Senhas")
root.configure(bg="#1e1e1e")  # Fundo cinza escuro

# Estilo moderno (Dark Mode)
style = ttk.Style()
style.theme_use("clam")

# Estilizando o Treeview
style.configure("Treeview",
                background="#2b2b2b",  # Fundo da tabela
                foreground="white",    # Texto da tabela
                fieldbackground="#2b2b2b",  # Fundo das células
                rowheight=30)

style.configure("Treeview.Heading",
                background="#1a1a1a",  # Fundo do cabeçalho
                foreground="white",    # Cor do texto do cabeçalho
                font=("Arial", 10, "bold"))

style.map('Treeview', background=[('selected', '#1a73e8')])  # Cor da seleção

# Estilizando a moldura das entradas com cinza escuro
style.configure('TEntry', fieldbackground="#333", foreground="white", padding=5, relief="flat")

# Botões arredondados com cinza claro
style.configure('TButton',
                background="#b0b0b0",  # Botões cinza claro
                foreground="black",    # Texto preto
                font=("Arial", 10, "bold"),
                borderwidth=0,
                relief="flat")

# Layout para entradas na horizontal
form_frame = ttk.Frame(root)
form_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

plataforma_label = ttk.Label(form_frame, text="Plataforma:")
plataforma_label.grid(row=0, column=0, padx=5, pady=5)
plataforma_entry = ttk.Entry(form_frame)
plataforma_entry.grid(row=0, column=1, padx=5, pady=5)

login_label = ttk.Label(form_frame, text="Login:")
login_label.grid(row=0, column=2, padx=5, pady=5)
login_entry = ttk.Entry(form_frame)
login_entry.grid(row=0, column=3, padx=5, pady=5)

senha_label = ttk.Label(form_frame, text="Senha:")
senha_label.grid(row=0, column=4, padx=5, pady=5)
senha_entry = ttk.Entry(form_frame, show="*")
senha_entry.grid(row=0, column=5, padx=5, pady=5)

# Botões
botao_frame = ttk.Frame(root)
botao_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

adicionar_button = ttk.Button(botao_frame, text="Adicionar", command=adicionar_senha)
adicionar_button.grid(row=0, column=0, padx=5, pady=5)

editar_button = ttk.Button(botao_frame, text="Editar", command=editar_senha)
editar_button.grid(row=0, column=1, padx=5, pady=5)

excluir_button = ttk.Button(botao_frame, text="Excluir", command=excluir_senha)
excluir_button.grid(row=0, column=2, padx=5, pady=5)

exibir_button = ttk.Button(botao_frame, text="Exibir Senha", command=exibir_senha_selecionada)
exibir_button.grid(row=0, column=3, padx=5, pady=5)

# Treeview para exibir senhas
tree = ttk.Treeview(root, columns=("ID", "Plataforma", "Login", "Senha"), show="headings")
tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Configurando as colunas da Treeview
tree.heading("ID", text="ID")
tree.heading("Plataforma", text="Plataforma")
tree.heading("Login", text="Login")
tree.heading("Senha", text="Senha")

tree.column("ID", width=30)
tree.column("Plataforma", width=150)
tree.column("Login", width=150)
tree.column("Senha", width=150)

# Atualiza visualizador na inicialização
atualizar_visualizador()

# Inicia o loop da interface
root.mainloop()

# Fecha a conexão com o banco de dados
conn.close()
