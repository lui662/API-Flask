"""
FAZER UMA API PRA CADASTRAR ALUNOS E PROFESSORES
url base - localhost
endpoint:
    CREATE
    READ
    UPDATE
    DELETE
"""
import datetime, os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app, resources={r'/*':{
    "origins": "http://127.0.0.1:5500",
    "methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"]
}})

DATABASE_HOST = os.getenv("MYSQLHOST")
DATABASE_PORT = os.getenv("MYSQLPORT")
DATABASE_USER = os.getenv("MYSQLUSER")
DATABASE_PASSWORD = os.getenv("MYSQLPASSWORD")
DATABASE_NAME = os.getenv("MYSQL_DATABASE")

def conexao_com_db():
    return mysql.connector.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )

def verificar_se_existe_aluno(conexao, id_aluno):
    cursor = conexao.cursor()    
    comando = f'SELECT id_aluno FROM aluno WHERE id_aluno = %s'
    cursor.execute(comando, (id_aluno,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None

def verificar_se_existe_professor(conexao,id_professor):
    cursor = conexao.cursor()
    comando = f'SELECT id_professor FROM professor WHERE id_professor = %s'
    cursor.execute(comando, (id_professor,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None

def verificar_se_existe_disciplina(conexao, id_disciplina):
    cursor = conexao.cursor()
    comando = f'SELECT id_disciplina FROM disciplina WHERE id_disciplina = %s'
    cursor.execute(comando, (id_disciplina,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'ERRO':'dados não fornecido'}), 400
    
    userId = data.get('id_aluno') or data.get('id_professor')
    userName = data.get('name')

    if not userId or not userName:
        return jsonify({"ERRO": "Campos obrigatorios ausentes"}), 400
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    if 'id_professor' in data:
        comando = 'SELECT id_professor FROM professor WHERE id_professor = %s AND nome = %s'
        cursor.execute(comando, (userId, userName))
    elif 'id_aluno' in data:
        comando = 'SELECT id_aluno FROM aluno WHERE id_aluno = %s AND nome = %s'
        cursor.execute(comando, (userId, userName))
    else:
        conexao.close()
        cursor.close()
        return jsonify({"Erro": "Usuario invalido"}), 400
    
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()

    if resultado:
        return jsonify({"SUCESSO": "login bem-sucedido"}), 200
    else:
        return jsonify({"message": "credenciais invalida"}), 400


#-----------------------------------------------------ALUNO-----------------------------------------------------------#
@app.route('/')
def index():
    return jsonify({"sucesso": "Inicialização da API bem sucessida"})

#METODO POST PARA ALUNO 
@app.route('/aluno/cadastrar', methods=['POST'])
def cadastrar_novo_aluno():
    data = request.json

    # Verificar se os campos necessários estão presentes
    if not data or 'name' not in data or 'date' not in data:
        return jsonify({'error': 'Dados de entrada inválidos'}), 400

    nome = data.get('name')
    data_nascimento = data.get('date')  # Já vem no formato 'YYYY-MM-DD'

    try:
        conexao = conexao_com_db()
        cursor = conexao.cursor()

        comando = 'INSERT INTO aluno (nome, data_nascimento) VALUES (%s, %s)'
        cursor.execute(comando, (nome, data_nascimento))
        conexao.commit()

        return jsonify({'SUCESSO': 'Aluno cadastrado com sucesso'}), 201

    except Exception as e:
        return jsonify({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()

#METODO GET PARA ALUNO 
@app.route('/aluno/listar', methods=['GET'])
def listar_alunos():
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'SELECT * FROM aluno'
    cursor.execute(comando)
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()
    
    return jsonify(resultado)


#METODO GET DE ALUNO POR ID
@app.route('/aluno/listar/<int:id_aluno>', methods=['GET'])
def listar_aluno_por_id(id_aluno):
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'SELECT * FROM aluno WHERE id_aluno = %s'
    cursor.execute(comando, (id_aluno,))
    aluno = cursor.fetchone()
    
    cursor.close()
    conexao.close()

    if aluno:
        return jsonify(aluno)
    else:
        return jsonify({'ERRO': 'Aluno não encontrado'}), 404


#METODO PUT DE ALUNO PELO ID
@app.route('/aluno/alterar/<int:id_aluno>', methods=['PUT'])
def editar_aluno_por_id(id_aluno):
    data = request.json
    if not data or ('name' not in data and 'date' not in data):
        return jsonify({'error': 'Dados de entrada inválidos'}), 400
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    if not verificar_se_existe_aluno(conexao, id_aluno):
        conexao.close()
        cursor.close()
        return jsonify({'ERRO': 'Aluno não encontrado'}), 404
    
    try:

        if 'name' in data:
            novo_nome = data.get('name')
            comando = f'UPDATE aluno SET nome = %s WHERE id_aluno = %s'
            cursor.execute(comando, (novo_nome, id_aluno))

        if 'date' in data:
            nova_data = data.get('date')
            nova_data = datetime.datetime.strptime(nova_data, '%Y-%m-%d').date()
            comando = f'UPDATE aluno SET data_nascimento = %s WHERE id_aluno = %s'
            cursor.execute(comando, (nova_data, id_aluno))

        conexao.commit()
        return jsonify({'SUCESSO': 'Dados do aluno atualizado com sucesso'}), 200

    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()

#METODO DELETE PARA ALUNO POR ID 
@app.route('/aluno/deletar/<int:id_aluno>', methods=['DELETE'])
def deletar_aluno_por_id(id_aluno):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'DELETE FROM aluno WHERE id_aluno = %s'
    cursor.execute(comando, (id_aluno,))
    conexao.commit()

    if cursor.rowcount > 0:
       resultado = {'SUCESSO': 'Aluno excluido com sucesso'}
    else:
        resultado = {'ERRO': 'Aluno não encontrado'}

    cursor.close()
    conexao.close()

    return jsonify(resultado)


#------------------------------------------------------PROFESSOR----------------------------------------------------------#

#METODO POST PARA PROFESSOR
@app.route('/professor/cadastrar', methods=['POST'])
def cadastrar_novo_professor():
    data = request.json
    if not data or ('name' not in data and 'especializacao' not in data):
        return jsonify({'error': 'Dados de entrada inválidos'}), 400

    nome = data.get('name')
    especializacao = data.get('especializacao')
    id_disciplina = data.get('id_disciplina')

    try:
        conexao = conexao_com_db()
        cursor = conexao.cursor()

        comando = f'INSERT INTO professor (nome, especializacao) VALUES (%s, %s)'
        cursor.execute(comando, (nome, especializacao))
        

        id_professor = cursor.lastrowid

        comando_acossiacao = f'INSERT INTO professor_disciplina(id_professor, id_disciplina) VALUES (%s, %s)'
        cursor.execute(comando_acossiacao, (id_professor, id_disciplina))

        conexao.commit()
        return jsonify({'SUCESSO': 'Professor cadastrado com sucesso!'}), 201
    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        conexao.close()
        cursor.close()

#METODO POST PARA VERIFICAR SE PROFESSOR ESTA ASSOCIADO A UMA DISCIPLINA
@app.route('/professor/associardisciplina', methods=['POST'])
def associar_professor_a_uma_disciplina_existente():
    data = request.json

#METODO GET PARA PROFESSOR 
@app.route('/professor/listar', methods=['GET'])
def listar_professores():
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'SELECT * FROM professor'
    cursor.execute(comando)
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()
    return jsonify(resultado)

    
#METODO GET PARA PROFESSOR POR ID
@app.route('/professor/listar/<int:id_professor>', methods=['GET'])
def listar_professor_por_id(id_professor):
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'SELECT * FROM professor WHERE id_professor = %s'
    cursor.execute(comando, (id_professor,))
    professor = cursor.fetchone()

    cursor.close()
    conexao.close()

    if professor:
        return jsonify(professor)
    else:
        return jsonify({'ERRO': 'Professor não encontrado'}), 404


#METODO PUT PARA PROFESSOR POR ID
@app.route('/professor/alterar/<int:id_professor>', methods=['PUT'])
def editar_professor_por_id(id_professor):
    data = request.json

    if not data or ('name' not in data or 'descricao' not in data):
        return jsonify({'ERRO': 'Dados invalidos'}), 400
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    if not verificar_se_existe_professor(conexao, id_professor):
        cursor.close()
        conexao.close()
        return jsonify({'ERRO': 'Professor não encotrado'}), 404
    

    try:
        if 'name' in data:
            novo_nome = data.get('name')
            comando = f'UPDATE professor SET nome = %s WHERE id_professor = %s'
            cursor.execute(comando, (novo_nome, id_professor))
        
        if 'descricao' in data:
            nova_descricao = data.get('descricao')
            comando = f'UPDATE professor SET descricao = %s WHERE id_professor = %s'
            cursor.execute(comando, (nova_descricao, id_professor))
            
        conexao.commit()
        return jsonify({'SUCESSO': 'Professor Alterado com sucesso'}), 200
    
    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()


#METODO DELETE PARA PROFESSOR POR ID
@app.route('/professor/deletar/<int:id_professor>', methods=['DELETE'])
def deletar_professor_por_id(id_professor):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'DELETE FROM professor WHERE id_professor = %s'
    cursor.execute(comando, (id_professor,))
    conexao.commit()

    if cursor.rowcount > 0:
        resultado = {'SUCESSO': 'Professor excluido com sucesso'}
    else:
        resultado = {'ERRO': 'Professor não cadastrado'}

    cursor.close()
    conexao.close()

    return jsonify(resultado)


#-------------------------------------------------------DISCIPLINA---------------------------------------------------------#


#METODO POST PRA DISCIPLINA 
@app.route('/disciplina/cadastrar', methods=['POST'])
def cadastrar_disciplina():
    data = request.json
    nome_disciplina = data.get('name')
    descricao = data.get('descricao')

    conexao = conexao_com_db()
    cursor = conexao.cursor()
    try:
        comando = f'INSERT INTO disciplina (nome_disciplina, descricao) VALUES (%s, %s)'
        cursor.execute(comando, (nome_disciplina, descricao))
        conexao.commit()
        return jsonify({'SUCESSO': 'disciplina cadastrada com sucesso'}), 200
    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        conexao.close()
        cursor.close()

#METODO GET PRA DISCIPLINA 
@app.route("/disciplina/listar", methods=["GET"])
def listar_disciplinas():
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'SELECT * FROM disciplina'
    cursor.execute(comando)
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(resultado)


#METODO GET PARA DISCIPLINA POR ID 
@app.route('/disciplina/listar/<int:id_disciplina>', methods=['GET'])
def listar_disciplina_por_id(id_disciplina):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = comando = 'SELECT * FROM disciplina WHERE id_disciplina = %s'
    cursor.execute(comando, (id_disciplina,))
    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado:
        return jsonify(resultado)
    else:
        return jsonify({'ERRO': 'disciplina não encontrada'})

#METODO PUT PARA DISCIPLINA POR ID
@app.route('/disciplina/alterar/<int:id_disciplina>', methods=['PUT'])
def alterar_disciplina_por_id(id_disciplina):
    data = request.json

    conexao = conexao_com_db()
    cursor = conexao.cursor()

    if not data or ('name' not in data or 'descricao' not in data):
        cursor.close()
        conexao.close()
        return jsonify({'ERRO': 'Dados invalidos'}), 400

    try:
        if 'name' in data:
            novo_nome = data.get('name')
            comando = f'UPDATE disciplina SET nome_disciplina = %s WHERE id_disciplina = %s'
            cursor.execute(comando, (novo_nome, id_disciplina))
        
        if 'descricao' in data:
            nova_descricao = data.get('descricao')
            comando = f'UPDATE disciplina SET descricao = %s WHERE id_disciplina = %s'
            cursor.execute(comando, (nova_descricao, id_disciplina))
        
        conexao.commit()
        return jsonify({'SUCESSO': 'Disciplina altarada com sucesso'}), 200
    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)})
    finally:
        cursor.close()
        conexao.close()


#METODO DELETE PARA DISCIPLINA POR ID 
@app.route('/disciplina/deletar/<int:id_disciplina>', methods=['DELETE'])
def deletar_disciplina_por_id(id_disciplina):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'DELETE FROM disciplina WHERE id_disciplina = %s'
    cursor.execute(comando, (id_disciplina,))
    conexao.commit()

    if cursor.rowcount > 0:
       resultado = {'SUCESSO': 'Disciplina apagada com sucesso'}
    else:
        resultado = {'ERRO': 'Disciplina não encontrada'}
    

    cursor.close()
    conexao.close()

    return jsonify(resultado)


#-------------------------------------------------------TURMA---------------------------------------------------------#

#METODO POST PARA TURMA
@app.route('/turma/cadastrar', methods=['POST'])
def cadastrar_turma():
    data = request.json 
    if not data or not all (key in data for key in['nome_turma', 'id_alunos', 'id_professor', 'id_disciplina']):
        return jsonify({'ERRO': 'Dados Invalidos'}), 400

    nome_turma = data.get('nome_turma')
    id_alunos = data.get('id_alunos')
    id_professor = data.get('id_professor')
    id_disciplina = data.get('id_disciplina')

    if not isinstance(id_alunos, list):
        return jsonify({'ERRO': 'deve conter uma lista de alunos'}), 400

    try:
        id_professor = int(id_professor) 
        id_disciplina = int(id_disciplina)
    except ValueError:
        return jsonify({'ERRO': 'Entrada de de dados invalida'}), 400
    
    for id_aluno in id_alunos:
        try:
            id_aluno = int(id_aluno)
        except ValueError:
            return jsonify({'ERRO': f'ID de aluno inválido: {id_aluno}'}), 400
    
    conexao = conexao_com_db()

    for id_aluno in id_alunos:
        if not verificar_se_existe_aluno(conexao, id_aluno):
            return jsonify({'ERRO': 'Aluno não encontrado'})
    if not verificar_se_existe_disciplina(conexao, id_disciplina):
        return jsonify({'ERRO': 'Disciplina não encontrada'})
    if not verificar_se_existe_professor(conexao, id_professor):
        return jsonify({'ERRO', 'Professor não encontrado'})

    cursor = conexao.cursor()
    
    try:
        comando = f'INSERT INTO turma (nome_turma, id_aluno, id_professor, id_disciplina) VALUES (%s, %s, %s, %s)'
        for id_aluno in id_alunos:
            cursor.execute(comando, (nome_turma, id_aluno, id_professor, id_disciplina))
        conexao.commit()
        return jsonify({'SUCESSO': 'turma cadastrada com sucesso'}), 201
    except mysql.connector.Error as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)})
    finally:
        cursor.close()
        conexao.close()

#METODO GET PARA TURMA POR ID
@app.route('/turma/listar/<int:id_turma>', methods=['GET'])
def listar_turma_por_id(id_turma):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'SELECT * FROM turma WHERE id_turma = %s'
    cursor.execute(comando, (id_turma,))
    turma = cursor.fetchone()

    cursor.close()
    conexao.close()

    if turma:
        return jsonify(turma)
    else:
        return jsonify({'ERRO': 'Turma não encontrada'})


#METODO PUT PARA TURMA POR ID
@app.route('/turma/alterar/<int:id_turma>', methods=['PUT'])
def editar_turma_por_id(id_turma):
    data = request.json
    conexao = conexao_com_db()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute('SELECT nome_turma, id_aluno, id_professor, id_disciplina FROM turma WHERE id_turma = %s', (id_turma,))
    dados_antigos = cursor.fetchone()

    nova_turma = data.get('nova_turma', dados_antigos['nome_turma'])
    id_aluno = data.get('id_aluno', dados_antigos['id_aluno'])
    id_professor = data.get('id_professor', dados_antigos['id_professor'])
    id_disciplina = data.get('id_disciplina', dados_antigos['id_disciplina'])

    try:
        id_aluno = int(id_aluno)
        id_professor = int(id_professor) 
        id_disciplina = int(id_disciplina)
    except ValueError:
        return jsonify({'ERRO': 'Entrada de de dados invalida'}), 400
    
    if not verificar_se_existe_aluno(conexao, id_aluno):
        return jsonify({'ERRO': 'Aluno não encontrado'})
    if not verificar_se_existe_disciplina(conexao, id_disciplina):
        return jsonify({'ERRO': 'Disciplina não encontrada'})
    if not verificar_se_existe_professor(conexao, id_professor):
        return jsonify({'ERRO', 'Professor não encontrado'})
    
    try:
        comando = f'''UPDATE turma SET 
        nome_turma = %s, 
        id_aluno = %s,
        id_professor = %s,
        id_disciplina = %s
        WHERE id_turma = %s'''
        cursor.execute(comando, (nova_turma, id_aluno, id_professor, id_disciplina, id_turma))
        conexao.commit()
        return jsonify({'SUCESSO':'Dado(s) atualizado com sucesso'}), 200
    except mysql.connector.Error as e:
        conexao.rollback()
        return jsonify ({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()


#METODO DELETE PARA TURMA POR ID
@app.route('/turma/deletar/<int:id_turma>', methods=['DELETE'])
def deletar_turma_por_id(id_turma):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = f'DELETE FROM turma WHERE id_turma = %s'
    cursor.execute(comando, (id_turma,))
    conexao.commit()

    if cursor.rowcount > 0:
        resultado = {'SUCESSO': 'Turma apagada com sucesso'}
    else:
        resultado = {'ERRO': 'turma não encontrada'}
    
    cursor.close()
    conexao.close()

    return jsonify(resultado)

@app.route('/nota/cadastrar', methods=['POST'])
def cadastrar_nota():
    data = request.json

    if not data or 'nota' not in data or 'id_aluno' not in data or 'id_disciplina' not in data:
        return jsonify({'ERRO': 'Dados de entrada inválidos'}), 400

    nota = data.get('nota')
    id_aluno = data.get('id_aluno')
    id_disciplina = data.get('id_disciplina')

    try:
        conexao = conexao_com_db()
        cursor = conexao.cursor()

        comando = 'INSERT INTO nota (nota, id_aluno, id_disciplina) VALUES (%s, %s, %s)'
        cursor.execute(comando, (nota, id_aluno, id_disciplina))
        conexao.commit()

        return jsonify({'SUCESSO': 'Nota cadastrada com sucesso!'}), 201
    except mysql.connector.Error as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()

@app.route('/nota/listar', methods=['GET'])
def listar_notas():
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'SELECT * FROM nota'
    cursor.execute(comando)
    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(resultado)

@app.route('/nota/listar/<int:id_nota>', methods=['GET'])
def listar_nota_por_id(id_nota):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'SELECT * FROM nota WHERE id_nota = %s'
    cursor.execute(comando, (id_nota,))
    nota = cursor.fetchone()

    cursor.close()
    conexao.close()

    if nota:
        return jsonify(nota)
    else:
        return jsonify({'ERRO': 'Nota não encontrada'}), 404

@app.route('/nota/alterar/<int:id_nota>', methods=['PUT'])
def editar_nota_por_id(id_nota):
    data = request.json

    if not data or ('nota' not in data):
        return jsonify({'ERRO': 'Dados de entrada inválidos'}), 400

    nota = data.get('nota')

    conexao = conexao_com_db()
    cursor = conexao.cursor()

    try:
        comando = 'UPDATE nota SET nota = %s WHERE id_nota = %s'
        cursor.execute(comando, (nota, id_nota))
        conexao.commit()

        if cursor.rowcount > 0:
            return jsonify({'SUCESSO': 'Nota atualizada com sucesso'}), 200
        else:
            return jsonify({'ERRO': 'Nota não encontrada'}), 404
    except mysql.connector.Error as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        cursor.close()
        conexao.close()

@app.route('/nota/deletar/<int:id_nota>', methods=['DELETE'])
def deletar_nota_por_id(id_nota):
    conexao = conexao_com_db()
    cursor = conexao.cursor()

    comando = 'DELETE FROM nota WHERE id_nota = %s'
    cursor.execute(comando, (id_nota,))
    conexao.commit()

    if cursor.rowcount > 0:
        resultado = {'SUCESSO': 'Nota apagada com sucesso'}
    else:
        resultado = {'ERRO': 'Nota não encontrada'}

    cursor.close()
    conexao.close()

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
