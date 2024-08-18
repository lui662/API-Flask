"""
FAZER UMA API PRA CADASTRAR ALUNOS E PROFESSORES
url base - localhost
endpoint:
    CREATE
    READ
    UPDATE
    DELETE
"""
import datetime
from flask import Flask, jsonify, request
import mysql.connector

def conexao_com_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Brasil2021#",
        database="cadastroturmas"
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

app = Flask(__name__)

#-----------------------------------------------------ALUNO-----------------------------------------------------------#

#METODO POST PARA ALUNO 
@app.route('/aluno/cadastrar', methods=['POST'])
def cadastrar_novo_aluno():
    
    data = request.json
    if not data or 'name' not in data or 'date' not in data:
        return jsonify({'error': 'Dados de entrada inválidos'}), 400
    
    conexao = conexao_com_db()
    cursor = conexao.cursor()
    nome = data.get('name')
    data_nascimento = data.get('date')

    try:

        data_nascimento = datetime.datetime.strptime(data_nascimento, '%Y-%m-%d').date()

    except ValueError:
        return jsonify({'ERRO': 'Formato de data invalido, Use YYYY-MM-DD'}), 400

    try:
        comando = f'INSERT INTO aluno (nome, data_nascimento) VALUES (%s, %s)'
        cursor.execute(comando, (nome, data_nascimento))
        conexao.commit()
        cursor.close()
        return jsonify({'SUCESSO': 'Aluno cadastrado com sucesso '}), 201

    except Exception as e:
        return jsonify({'ERRO': str(e)}), 500

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

    conexao = conexao_com_db()
    cursor = conexao.cursor()

    try:
        comando = f'INSERT INTO professor (nome, especializacao) VALUES (%s, %s)'
        cursor.execute(comando, (nome, especializacao))
        conexao.commit()
        return jsonify({'SUCESSO': 'Professor cadastrado com sucesso!'}), 201
    except Exception as e:
        conexao.rollback()
        return jsonify({'ERRO': str(e)}), 500
    finally:
        conexao.close()
        cursor.close()

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

    comando = 'SELECT * FROM dicisplina WHERE id_disciplina = %s'
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

if __name__ == '__main__':
    app.run()