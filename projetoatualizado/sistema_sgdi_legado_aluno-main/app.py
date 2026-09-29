from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = '123456'
PAGE_SIZE = 10

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

def solicitante_label(demanda):
    return demanda['solicitante_nome'] or demanda['solicitante'] or 'Solicitante legado'

@app.route('/')
def index():
    conn = get_db()
    ensure_schema(conn)
    solicitantes = get_solicitantes(conn)
    solicitante_id = request.args.get('solicitante_id', type=int)
    prioridade = request.args.get('prioridade', '')
    departamento = request.args.get('departamento', '').strip()
    termo = request.args.get('q', '').strip()
    data_inicial = request.args.get('data_inicial', '').strip()
    data_final = request.args.get('data_final', '').strip()
    pagina = max(request.args.get('page', 1, type=int), 1)

    datas_validas = True
    for valor in (data_inicial, data_final):
        if valor:
            try:
                date.fromisoformat(valor)
            except ValueError:
                datas_validas = False
                break
    if not datas_validas:
        flash('Informe datas válidas para filtrar o período.')
        data_inicial = ''
        data_final = ''
    if data_inicial and data_final and data_inicial > data_final:
        flash('A data inicial não pode ser posterior à data final.')
        data_inicial = ''
        data_final = ''

    where = []
    params = []
    if solicitante_id:
        where.append('d.solicitante_id = ?')
        params.append(solicitante_id)
    if prioridade in ('ALTA', 'MÉDIA', 'BAIXA'):
        where.append('d.prioridade = ?')
        params.append(prioridade)
    if departamento:
        where.append('s.departamento = ?')
        params.append(departamento)
    if data_inicial:
        where.append('date(d.data_criacao) >= date(?)')
        params.append(data_inicial)
    if data_final:
        where.append('date(d.data_criacao) <= date(?)')
        params.append(data_final)
    if termo:
        where.append('(d.titulo LIKE ? OR d.descricao LIKE ?)')
        params.extend((f'%{termo}%', f'%{termo}%'))
    clause = 'WHERE ' + ' AND '.join(where) if where else ''
    total_query = f'''SELECT COUNT(*)
        FROM demandas d LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        {clause}'''
    total_demandas = conn.execute(total_query, params).fetchone()[0]
    total_paginas = max((total_demandas + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * PAGE_SIZE
    demandas = conn.execute(f'''SELECT d.*, s.nome AS solicitante_nome,
            s.email AS solicitante_email, s.departamento AS solicitante_departamento
        FROM demandas d LEFT JOIN solicitantes s ON s.id = d.solicitante_id
        {clause}
        ORDER BY CASE d.prioridade WHEN "ALTA" THEN 1 WHEN "MÉDIA" THEN 2 ELSE 3 END,
            d.id DESC LIMIT ? OFFSET ?''', params + [PAGE_SIZE, offset]).fetchall()
    resumo = conn.execute('''SELECT s.id, s.nome, s.email, s.departamento,
            COUNT(d.id) AS total_demandas
        FROM solicitantes s LEFT JOIN demandas d ON d.solicitante_id = s.id
        GROUP BY s.id ORDER BY s.nome''').fetchall()
    departamentos = conn.execute(
        'SELECT DISTINCT departamento FROM solicitantes ORDER BY departamento'
    ).fetchall()
    conn.close()
    query_params = {key: value for key, value in request.args.to_dict().items() if key != 'page'}
    inicio_exibicao = (pagina - 1) * PAGE_SIZE + 1 if total_demandas else 0
    fim_exibicao = min(pagina * PAGE_SIZE, total_demandas) if total_demandas else 0
    return render_template('index.html', demandas=demandas, solicitantes=solicitantes,
                           departamentos=departamentos, resumo=resumo,
                           filtro_solicitante=solicitante_id,
                           filtro_prioridade=prioridade,
                           filtro_departamento=departamento, termo=termo,
                           data_inicial=data_inicial, data_final=data_final,
                           total_demandas=total_demandas, pagina_atual=pagina,
                           total_paginas=total_paginas, PAGE_SIZE=PAGE_SIZE,
                           inicio_exibicao=inicio_exibicao, fim_exibicao=fim_exibicao,
                           query_params=query_params, solicitante_label=solicitante_label)

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
    return redirect(url_for('index', q=request.args.get('q', '')))

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
