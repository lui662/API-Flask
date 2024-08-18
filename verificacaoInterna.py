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

