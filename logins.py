import sqlite3
from cryptography.fernet import Fernet

# Gera uma chave para criptografia
key = Fernet.generate_key()
cipher = Fernet(key)

# Conecta ao banco de dados (ou cria um novo)
conn = sqlite3.connect('gerenciador_senhas.db')
cursor = conn.cursor()

# Cria a tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS senhas (
    id INTEGER PRIMARY KEY,
    plataforma TEXT NOT NULL,
    login TEXT NOT NULL,
    senha TEXT NOT NULL,
    descricao TEXT
)
''')
conn.commit()

def adicionar_senha(plataforma, login, senha, descricao):
    senha_criptografada = cipher.encrypt(senha.encode())
    cursor.execute('''
    INSERT INTO senhas (plataforma, login, senha, descricao)
    VALUES (?, ?, ?, ?)
    ''', (plataforma, login, senha_criptografada, descricao))
    conn.commit()
    print("Senha adicionada com sucesso!")

# Exemplo de uso
adicionar_senha('Facebook', 'meu_email@exemplo.com', 'minha_senha_secreta', 'Minha conta pessoal')

# Fecha a conexão
conn.close()
