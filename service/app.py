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
            'CREATE TABLE IF NOT EXISTS ips (ip TEXT PRIMARY KEY, primeiro_acesso INTEGER, ultimo_acesso INTEGER)'
        )
        db.commit()
    return db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_database', None)
    if db:
        db.close()

def novo_dia(ts1, ts2):
    # Testa se é um novo dia
    import datetime
    return datetime.datetime.fromtimestamp(ts1).date() != datetime.datetime.fromtimestamp(ts2).date()


def get_client_ip():
    return request.args.get('ip') or request.remote_addr


@app.route('/status', methods=['GET'])
def status():
    client_ip = get_client_ip()
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT primeiro_acesso FROM ips WHERE ip=?', (client_ip,))
    row = cur.fetchone()
    agora = int(time.time())
    if row is None:
        cur.execute(
            'INSERT INTO ips(ip, primeiro_acesso, ultimo_acesso) VALUES (?,?,?)', (client_ip, agora, agora)
        )
        permitido = True
        motivo = 'nunca_acessou'
        primeiro_acesso = None
        decorrido = 0
    else:
        primeiro_acesso = row[0]

        if novo_dia(primeiro_acesso, agora):
            cur.execute('UPDATE ips SET primeiro_acesso=?, ultimo_acesso=? WHERE ip=?', (agora, agora, client_ip))
            permitido = True
            motivo = 'novo_dia'
            decorrido = 0
        else:
            cur.execute('UPDATE ips SET ultimo_acesso=? WHERE ip=?', (agora, client_ip))
            decorrido = agora - primeiro_acesso
            permitido = decorrido <= LIMITE_TEMPO
            motivo = 'dentro_limite' if permitido else 'fora_limite'
    db.commit()
    return jsonify({'permitido': permitido, 'motivo': motivo, 'primeiro_acesso': primeiro_acesso, 'decorrido': decorrido, 'tempo_limite': LIMITE_TEMPO}), 200


@app.route('/health', methods=['GET'])
def health():
    return 'ok', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
