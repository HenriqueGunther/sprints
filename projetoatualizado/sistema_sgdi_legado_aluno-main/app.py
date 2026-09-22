from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'

def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def ensure_schema(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS solicitantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL COLLATE NOCASE UNIQUE,
        email TEXT NOT NULL COLLATE NOCASE UNIQUE,
        departamento TEXT NOT NULL
    )''')
    columns = [row['name'] for row in conn.execute('PRAGMA table_info(demandas)')]
    if 'solicitante_id' not in columns:
        conn.execute('ALTER TABLE demandas ADD COLUMN solicitante_id INTEGER REFERENCES solicitantes(id)')
    conn.commit()

def get_solicitantes(conn):
    return conn.execute(
        'SELECT id, nome, email, departamento FROM solicitantes ORDER BY nome'
    ).fetchall()

def demanda_query(where='', params=()):
    conn = get_db()
    ensure_schema(conn)
    demandas = conn.execute(f'''SELECT d.*, s.nome AS solicitante_nome,
            s.email AS solicitante_email, s.departamento AS solicitante_departamento
        FROM demandas d
        LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        {where}
        ORDER BY CASE d.prioridade WHEN "ALTA" THEN 1
            WHEN "MÉDIA" THEN 2 ELSE 3 END, d.id DESC''', params).fetchall()
    conn.close()
    return demandas

def solicitante_label(demanda):
    return demanda['solicitante_nome'] or demanda['solicitante'] or 'Solicitante legado'

@app.route('/')
def index():
    conn = get_db()
    ensure_schema(conn)
    solicitantes = get_solicitantes(conn)
    solicitante_id = request.args.get('solicitante_id', type=int)
    prioridade = request.args.get('prioridade', '')
    where = []
    params = []
    if solicitante_id:
        where.append('d.solicitante_id = ?')
        params.append(solicitante_id)
    if prioridade in ('ALTA', 'MÉDIA', 'BAIXA'):
        where.append('d.prioridade = ?')
        params.append(prioridade)
    clause = 'WHERE ' + ' AND '.join(where) if where else ''
    demandas = conn.execute(f'''SELECT d.*, s.nome AS solicitante_nome,
            s.email AS solicitante_email, s.departamento AS solicitante_departamento
        FROM demandas d LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        {clause}
        ORDER BY CASE d.prioridade WHEN "ALTA" THEN 1 WHEN "MÉDIA" THEN 2 ELSE 3 END,
            d.id DESC''', params).fetchall()
    resumo = conn.execute('''SELECT s.id, s.nome, s.email, s.departamento,
            COUNT(d.id) AS total_demandas
        FROM solicitantes s LEFT JOIN demandas d ON d.solicitante_id = s.id
        GROUP BY s.id ORDER BY s.nome''').fetchall()
    conn.close()
    return render_template('index.html', demandas=demandas, solicitantes=solicitantes,
                           resumo=resumo, filtro_solicitante=solicitante_id,
                           filtro_prioridade=prioridade, solicitante_label=solicitante_label)

@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    conn = get_db()
    ensure_schema(conn)
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante_id = request.form.get('solicitante_id', type=int)
        prioridade = request.form['prioridade']
        responsavel = request.form['responsavel']
        if not solicitante_id:
            conn.close()
            flash('Selecione um solicitante cadastrado.')
            return redirect('/nova_demanda')
        conn.execute('''INSERT INTO demandas
            (titulo, descricao, solicitante, solicitante_id, data_criacao, prioridade, responsavel)
            VALUES (?, ?, '', ?, ?, ?, ?)''',
            (titulo, descricao, solicitante_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             prioridade, responsavel))
        conn.commit()
        conn.close()
        flash('Demanda criada com sucesso!')
        return redirect('/')
    solicitantes = get_solicitantes(conn)
    conn.close()
    return render_template('nova_demanda.html', solicitantes=solicitantes)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    ensure_schema(conn)
    if request.method == 'POST':
        solicitante_id = request.form.get('solicitante_id', type=int)
        if not solicitante_id:
            conn.close()
            flash('Selecione um solicitante cadastrado.')
            return redirect(f'/editar/{id}')
        conn.execute('''UPDATE demandas SET titulo=?, descricao=?, solicitante=?,
            solicitante_id=?, prioridade=?, responsavel=? WHERE id=?''',
            (request.form['titulo'], request.form['descricao'],
             '', solicitante_id, request.form['prioridade'],
             request.form['responsavel'], id))
        conn.commit()
        conn.close()
        flash('Demanda atualizada com sucesso!')
        return redirect('/')
    demanda = conn.execute('''SELECT d.*, s.nome AS solicitante_nome
        FROM demandas d LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        WHERE d.id=?''', (id,)).fetchone()
    solicitantes = get_solicitantes(conn)
    conn.close()
    return render_template('editar.html', demanda=demanda, solicitantes=solicitantes,
                           solicitante_label=solicitante_label)

@app.route('/deletar/<int:id>')
def deletar(id):
    conn = get_db()
    conn.execute('DELETE FROM demandas WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Demanda deletada!')
    return redirect('/')

@app.route('/buscar')
def buscar():
    termo = request.args.get('q', '')
    resultados = demanda_query('WHERE d.titulo LIKE ? OR d.descricao LIKE ?',
                               (f'%{termo}%', f'%{termo}%'))
    return render_template('index.html', demandas=resultados, termo=termo,
                           solicitantes=[], resumo=[], solicitante_label=solicitante_label)

@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()
    ensure_schema(conn)
    demanda = conn.execute('''SELECT d.*, s.nome AS solicitante_nome,
        s.email AS solicitante_email, s.departamento AS solicitante_departamento
        FROM demandas d LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        WHERE d.id=?''', (id,)).fetchone()
    comentarios = conn.execute(
        'SELECT * FROM comentarios WHERE demanda_id=? ORDER BY id DESC', (id,)).fetchall()
    conn.close()
    return render_template('detalhes.html', demanda=demanda,
                           comentarios=comentarios, solicitante_label=solicitante_label)

@app.route('/solicitantes', methods=['GET', 'POST'])
def solicitantes():
    conn = get_db()
    ensure_schema(conn)
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        departamento = request.form['departamento'].strip()
        try:
            conn.execute('INSERT INTO solicitantes (nome, email, departamento) VALUES (?, ?, ?)',
                         (nome, email, departamento))
            conn.commit()
            flash('Solicitante cadastrado com sucesso!')
        except sqlite3.IntegrityError:
            flash('Já existe um solicitante com esse nome ou e-mail.')
        conn.close()
        return redirect('/solicitantes')
    cadastrados = get_solicitantes(conn)
    conn.close()
    return render_template('solicitantes.html', solicitantes=cadastrados)

@app.route('/adicionar_comentario/<int:demanda_id>', methods=['POST'])
def adicionar_comentario(demanda_id):
    conn = get_db()
    conn.execute('''INSERT INTO comentarios (demanda_id, comentario, autor, data)
        VALUES (?, ?, ?, ?)''',
        (demanda_id, request.form['comentario'], request.form['autor'],
         datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return redirect(f'/detalhes/{demanda_id}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
