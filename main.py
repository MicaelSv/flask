from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from model import create_db

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

create_db()

@app.route('/medicos', methods=['GET'])
def getpacientes():
    conn = sqlite3.connect('atendimento.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM medico')
    medicos = cursor.fetchall()

    list_medicos = list()

    for medico in medicos:
        list_medicos.append(
            {
                'id': medico[0],
                'nome': medico[1],
                'crm': medico[2],
                'especialidade': medico[3],
                'senha': medico[4]
            }
        )

    #print(list_medicos)
    conn.close()

    return jsonify(list_medicos)


@app.route('/add_medico', methods=['POST'])
def addpaciente():
    conn = sqlite3.connect('atendimento.db')
    cursor = conn.cursor()

    data = request.get_json()

    # Verificar se o CRM já existe no banco de dados
    cursor.execute('SELECT crm FROM medico WHERE crm = %s', (data['crm'],))
    existing_patient = cursor.fetchone()

    if existing_patient:
        conn.close()
        return jsonify({'error': 'CRM já cadastrado. Por favor, insira um CRM diferente.'}), 400
        # Retorna um erro HTTP 400 (Bad Request) indicando a duplicação do CRM

    # Inserir o medico apenas se o CRM não estiver duplicado
    cursor.execute('INSERT INTO medico (nome, crm, especialidade, senha) VALUES (%s, %s, %s, %s)',
                   (data['nome'], data['crm'], data['especialidade'], data['senha']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Médico adicionado com sucesso!'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
