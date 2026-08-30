import sqlite3

conn = sqlite3.connect('demandas.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    solicitante TEXT NOT NULL,
    data_criacao TEXT NOT NULL,
    prioridade TEXT NOT NULL DEFAULT 'MÉDIA',
    responsavel TEXT NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_id INTEGER,
    comentario TEXT,
    autor TEXT,
    data TEXT
)''')

cursor.execute("DELETE FROM demandas")
cursor.execute("DELETE FROM comentarios")

demandas = [
    (1, 'Corrigir bug no login', 'Usuários não conseguem fazer login', 'João Silva', '2024-01-15 10:30:00', 'ALTA', 'Tech Team'),
    (2, 'Implementar relatório de vendas', 'Precisamos de um relatório mensal', 'Maria Santos', '2024-01-16 14:20:00', 'MÉDIA', 'Desenvolvedor'),
    (3, 'Melhorar performance', 'Sistema está lento', 'Pedro Costa', '2024-01-17 09:15:00', 'ALTA', 'Tech Team'),
    (4, 'Adicionar filtros', 'Usuários querem filtrar demandas', 'Ana Lima', '2024-01-18 11:00:00', 'BAIXA', 'Desenvolvedor')
]
cursor.executemany('''INSERT INTO demandas
    (id, titulo, descricao, solicitante, data_criacao, prioridade, responsavel)
    VALUES (?, ?, ?, ?, ?, ?, ?)''', demandas)

comentarios = [
    (1, 1, 'Vou investigar esse bug', 'Tech Team', '2024-01-15 11:00:00'),
    (2, 1, 'Bug corrigido na branch develop', 'Desenvolvedor', '2024-01-15 16:30:00')
]
cursor.executemany('''INSERT INTO comentarios
    (id, demanda_id, comentario, autor, data) VALUES (?, ?, ?, ?, ?)''', comentarios)

conn.commit()
conn.close()
print("Banco de dados criado com sucesso!")
