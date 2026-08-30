from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = '123456'

def get_db():
    conn = sqlite3.connect('demandas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    demandas = conn.execute('''SELECT * FROM demandas ORDER BY
        CASE prioridade WHEN "ALTA" THEN 1 WHEN "MÉDIA" THEN 2 ELSE 3 END, id DESC''').fetchall()
    conn.close()
    return render_template('index.html', demandas=demandas)

@app.route('/nova_demanda', methods=['GET', 'POST'])
def nova_demanda():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        solicitante = request.form['solicitante']
        prioridade = request.form['prioridade']
        responsavel = request.form['responsavel']
        conn = get_db()
        conn.execute('''INSERT INTO demandas
            (titulo, descricao, solicitante, data_criacao, prioridade, responsavel)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (titulo, descricao, solicitante, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             prioridade, responsavel))
        conn.commit()
        conn.close()
        flash('Demanda criada com sucesso!')
        return redirect('/')
    return render_template('nova_demanda.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute('''UPDATE demandas SET titulo=?, descricao=?, solicitante=?,
            prioridade=?, responsavel=? WHERE id=?''',
            (request.form['titulo'], request.form['descricao'],
             request.form['solicitante'], request.form['prioridade'],
             request.form['responsavel'], id))
        conn.commit()
        conn.close()
        flash('Demanda atualizada com sucesso!')
        return redirect('/')
    demanda = conn.execute('SELECT * FROM demandas WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('editar.html', demanda=demanda)

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
    conn = get_db()
    resultados = conn.execute('''SELECT * FROM demandas
        WHERE titulo LIKE ? OR descricao LIKE ?
        ORDER BY CASE prioridade WHEN "ALTA" THEN 1 WHEN "MÉDIA" THEN 2 ELSE 3 END, id DESC''',
        (f'%{termo}%', f'%{termo}%')).fetchall()
    conn.close()
    return render_template('index.html', demandas=resultados, termo=termo)

@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()
    demanda = conn.execute('SELECT * FROM demandas WHERE id=?', (id,)).fetchone()
    comentarios = conn.execute(
        'SELECT * FROM comentarios WHERE demanda_id=? ORDER BY id DESC', (id,)).fetchall()
    conn.close()
    return render_template('detalhes.html', demanda=demanda, comentarios=comentarios)

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
