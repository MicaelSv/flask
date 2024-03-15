from flask import Flask, request, jsonify
from flask_cors import CORS
from model import create_db
from datetime import datetime 
from queue import Queue
import sqlite3, json

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

create_db()

# Fila de espera
fila_espera = Queue()

#ENTRADA APENAS PARA TESTES
usuario7 = {
        "cpf": "12345678900",
        "birthDate": "1990-01-01",
        "consultas": [
            {
                "Médico": "Dr. João",
                "crm": "12345",
                "data": "2024-03-14",
                "tipo de consulta": "Consulta de Rotina",
                "tipo de pagamento": "Dinheiro"
            },
        ]
}

usuario8 = {
        "cpf": "12345678908",
        "birthDate": "1980-01-01",
        "consultas": [
            {
                "Médico": "Dr. Bruno",
                "crm": "22222",
                "data": "2024-03-14",
                "tipo de consulta": "Consulta de Rotina",
                "tipo de pagamento": "Pix"
            },
        ]
}



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


@app.route('/filas', methods=['POST'])
def verificar_cpf():

    cpf = request.get_json()  #recebendo o cpf do front
    #cpf = data['cpf']


    # Verifica se o CPF já está na fila
    position_in_queue = 0
    for index, (user_type, user_cpf) in enumerate(fila_espera.queue, start=1):
        if user_cpf == cpf:
            return jsonify({'message': 'Usuário já está na fila.',
                            'position': index}), 400
        position_in_queue = index
    
    #response = requests.get_json('') #recebendo os dados do banco do grupo de marcacao - qlqr coisa utilizar requests
    #usuarios = response.json()
    
    usuarios = [usuario7, usuario8]


    for usuario in usuarios:
        if usuario['cpf'] == cpf: #verificando se o cpf digitado existe no banco de dados
            consulta_data = datetime.strptime(usuario['consultas'][0]['data'], '%Y-%m-%d').date()
            if consulta_data == datetime.today().date():
                # Calcula a idade do usuário
                birth_date = datetime.strptime(usuario['birthDate'], '%Y-%m-%d').date()
                idade = (datetime.today().date() - birth_date).days // 365
                if idade >= 60:
                    fila_espera.put(('preferencial', cpf))
                else:
                    fila_espera.put(('normal', cpf))
                
                return jsonify({'message': 'Usuário adicionado à fila.', 
                                'position': fila_espera.qsize()})
    
    return jsonify({'error': 'CPF não encontrado ou data da consulta não corresponde ao dia atual.'}), 400


@app.route('/add_medico', methods=['POST'])
def addpaciente():
    conn = sqlite3.connect('atendimento.db')
    cursor = conn.cursor()

    data = request.get_json()

    print(data)

    # Verificar se o CRM já existe no banco de dados
    cursor.execute('SELECT crm FROM medico WHERE crm = ?', (data['crm'],))
    existing_patient = cursor.fetchone()

    if existing_patient:
        conn.close()
        return jsonify({'error': 'CRM já cadastrado. Por favor, insira um CRM diferente.'}), 400
        # Retorna um erro HTTP 400 (Bad Request) indicando a duplicação do CRM

    # Inserir o medico apenas se o CRM não estiver duplicado
    cursor.execute('INSERT INTO medico (nome, crm, especialidade, senha) VALUES (?, ?, ?, ?)',
                   (data['nome'], data['crm'], data['especialidade'], data['senha']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Médico adicionado com sucesso!'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
