from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = "secreto"

# Inicializa SocketIO
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulador')
def simulador():
    if 'user_id' in session:
        return render_template('simulador.html')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['usuario']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        session['user_id'] = user_id
        session['user'] = nombre
        return redirect('/simulador')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/registrar_disparo', methods=['POST'])
def registrar_disparo():
    data = request.get_json()
    x = data['x']
    y = data['y']
    puntos = data['puntos']
    usuario_id = session.get('user_id', 1)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO disparos (usuario_id, x, y, puntos) VALUES (?, ?, ?, ?)",
        (usuario_id, x, y, puntos)
    )
    conn.commit()
    conn.close()

    # Emitir evento para que el cliente actualice el canvas en tiempo real
    socketio.emit('nuevo_disparo', {'x': x, 'y': y, 'puntos': puntos})

    return jsonify({'status': 'ok'})

@app.route('/estadisticas')
def estadisticas():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    rows = conn.execute("SELECT puntos, timestamp FROM disparos WHERE usuario_id = ? ORDER BY timestamp DESC LIMIT 10",
                        (session['user_id'],)).fetchall()
    conn.close()
    return render_template('estadisticas.html', disparos=rows)

if __name__ == '__main__':
    # Usa socketio.run en vez de app.run para activar SocketIO
    socketio.run(app, debug=True)
