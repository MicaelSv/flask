from flask import Flask, request, jsonify
from flask_cors import CORS
from model import create_db
from datetime import datetime 
from queue import Queue
from queue import PriorityQueue
import sqlite3, json

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

create_db()

# Fila de espera
fila_espera = PriorityQueue()
contador = 0

#ENTRADA APENAS PARA TESTES
usuario7 = {
        "cpf": "12345678900",
        "birthDate": "1980-01-01",
        "consultas": [
            {
                "Médico": "Dr. João",
                "crm": "12345",
                "data": "2024-03-25",
                "tipo de consulta": "Consulta de Rotina",
                "tipo de pagamento": "Dinheiro"
            },
        ]
}

usuario8 = {
        "cpf": "12345678908",
        "birthDate": "1960-01-01",
        "consultas": [
            {
                "Médico": "Dr. Bruno",
                "crm": "22222",
                "data": "2024-03-25",
                "tipo de consulta": "Consulta de Rotina",
                "tipo de pagamento": "Pix"
            },
        ]
}

usuario9 = {
    "cpf": "12345678916",
    "birthDate": "1975-05-20",
    "consultas": [
        {
            "Médico": "Dra. Maria",
            "crm": "54321",
            "data": "2024-03-25",
            "tipo de consulta": "Consulta de Emergência",
            "tipo de pagamento": "Cartão de Crédito"
        },
    ]
}

usuario10 = {
    "cpf": "12345678924",
    "birthDate": "1960-11-10",
    "consultas": [
        {
            "Médico": "Dr. Pedro",
            "crm": "67890",
            "data": "2024-03-25",
            "tipo de consulta": "Exame de Sangue",
            "tipo de pagamento": "Boleto Bancário"
        },
    ]
}


global total_users
total_users = [usuario7, usuario8, usuario8, usuario9, usuario10]



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
    global contador
    data = request.get_json()  #recebendo o cpf do front
    cpf = data['cpf']
    #print(cpf)

    # Verifica se o CPF já está na fila
    for _, _, user_cpf in fila_espera.queue:
        if user_cpf == cpf:
            return jsonify({'message': 'Usuário já está na fila.'}), 401

    for usuario in total_users:
        if usuario['cpf'] == cpf: # Verificando se o CPF digitado existe no banco de dados
            consulta_data = datetime.strptime(usuario['consultas'][0]['data'], '%Y-%m-%d').date()
            print(consulta_data)
            if consulta_data == datetime.today().date():
                # Calcula a idade do usuário
                birth_date = datetime.strptime(usuario['birthDate'], '%Y-%m-%d').date()
                idade = (datetime.today().date() - birth_date).days // 365
                if idade >= 60:
                    prioridade = 0
                else:
                    prioridade = 1
                fila_espera.put((prioridade, contador, cpf))
                contador += 1
                
                return jsonify({'message': 'Usuário adicionado à fila.', 'position': fila_espera.qsize()})
    
    return jsonify({'error': 'CPF não encontrado ou data da consulta não corresponde ao dia atual.'}), 402


@app.route('/paci', methods=['GET'])
def obter_fila():
    pacientes_na_fila = [{'position': index, 'cpf': cpf} for index, (_, _, cpf) in enumerate(fila_espera.queue, start=1)]
    return jsonify({'patients': pacientes_na_fila})

#12345678916 - 12345678900 - 12345678924 - 12345678908

@app.route('/chamar', methods=['GET'])
def chamar_paciente():
    if not fila_espera.empty():
        _, _, cpf = fila_espera.get()
        pacientes_na_fila = [{'position': index, 'cpf': cpf} for index, (_, cpf) in enumerate(fila_espera.queue, start=1)]
        return jsonify({'message': f'Paciente {cpf} chamado.', 'patients': pacientes_na_fila})
    else:
        return jsonify({'error': 'A fila está vazia.'}), 400


@app.route('/add_medico', methods=['POST'])
def addpaciente():
    conn = sqlite3.connect('atendimento.db')
    cursor = conn.cursor()

    data = request.get_json()

    #print(data)

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



@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    return jsonify({'usuarios': [usuario7, usuario8, usuario9, usuario10]})



if __name__ == '__main__':
    app.run(debug=True, port=5000)
