from flask import Flask, request, jsonify, g
import sqlite3
import time
import os

DB_PATH = os.environ.get('DB_PATH', '/data/data.db')
LIMITE_TEMPO = 2 * 60 * 60 # 2 horas em segundos

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.execute(
            'CREATE TABLE IF NOT EXISTS acessos (cliente_src TEXT PRIMARY KEY, primeiro_acesso INTEGER, ultimo_acesso INTEGER, fgt_hostname TEXT)'
        )
        # cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ips'")
        # if cursor.fetchone() is not None:
        #     db.execute('DROP TABLE ips')
        db.commit()
    return db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_database', None)
    if db:
        db.close()

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def novo_dia(ts1, ts2):
    # Testa se é um novo dia
    import datetime
    return datetime.datetime.fromtimestamp(ts1).date() != datetime.datetime.fromtimestamp(ts2).date()


def get_cliente_src():
    return request.args.get('cliente_src') or request.remote_addr


def get_fgt_hostname():
    return request.args.get('fgt_hostname') or ''


@app.route('/status', methods=['GET'])
def status():
    cliente_src = get_cliente_src()
    fgt_hostname = get_fgt_hostname()
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT primeiro_acesso FROM acessos WHERE cliente_src=?', (cliente_src,))
    row = cur.fetchone()
    agora = int(time.time())
    if row is None:
        cur.execute(
            'INSERT INTO acessos(cliente_src, primeiro_acesso, ultimo_acesso, fgt_hostname) VALUES (?,?,?,?)',
            (cliente_src, agora, agora, fgt_hostname)
        )
        permitido = True
        motivo = 'nunca_acessou'
        primeiro_acesso = None
        decorrido = 0
    else:
        primeiro_acesso = row[0]

        if novo_dia(primeiro_acesso, agora):
            cur.execute(
                'UPDATE acessos SET primeiro_acesso=?, ultimo_acesso=?, fgt_hostname=? WHERE cliente_src=?',
                (agora, agora, fgt_hostname, cliente_src)
            )
            permitido = True
            motivo = 'novo_dia'
            decorrido = 0
        else:
            cur.execute('UPDATE acessos SET ultimo_acesso=?, fgt_hostname=? WHERE cliente_src=?', (agora, fgt_hostname, cliente_src))
            decorrido = agora - primeiro_acesso
            permitido = decorrido <= LIMITE_TEMPO
            motivo = 'dentro_limite' if permitido else 'fora_limite'
    db.commit()
    return jsonify({
        'permitido': permitido,
        'motivo': motivo,
        'primeiro_acesso': primeiro_acesso,
        'decorrido': decorrido,
        'tempo_limite': LIMITE_TEMPO,
        'cliente_src': cliente_src,
        'fgt_hostname': fgt_hostname,
    }), 200


@app.route('/health', methods=['GET'])
def health():
    return 'ok', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
