CREATE DATABASE cadastroturmas; 

USE cadastroturmas;

CREATE TABLE aluno (
id_aluno INT AUTO_INCREMENT PRIMARY KEY, 
nome VARCHAR(45) NOT NULL, 
data_nascimento DATE NOT NULL
);  

CREATE TABLE professor(
id_professor INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(45) NOT NULL, 
especializacao VARCHAR(45) NOT NULL
);

CREATE TABLE disciplina(
id_disciplina INT AUTO_INCREMENT PRIMARY KEY,
nome_disciplina VARCHAR(45) NOT NULL,
descricao TEXT NOT NULL
);

CREATE TABLE turma(
id_turma INT AUTO_INCREMENT PRIMARY KEY, 
nome_turma VARCHAR(45) NOT NULL, 
id_aluno INT NOT NULL, 
id_professor INT NOT NULL, 
id_disciplina INT NOT NULL,
CONSTRAINT fk_aluno FOREIGN KEY (id_aluno) REFERENCES aluno (id_aluno) ON DELETE CASCADE, 
CONSTRAINT fk_professor FOREIGN KEY (id_professor) REFERENCES professor (id_professor) ON DELETE CASCADE,
CONSTRAINT fk_disciplina FOREIGN KEY (id_disciplina) REFERENCES disciplina (id_disciplina) ON DELETE CASCADE
); 

CREATE TABLE nota(
id_nota INT AUTO_INCREMENT PRIMARY KEY, 
nota DECIMAL(3,2) NOT NULL, 
id_aluno INT NOT NULL, 
id_disciplina INT NOT NULL, 
FOREIGN KEY (id_aluno) REFERENCES aluno (id_aluno) ON DELETE CASCADE, 
FOREIGN KEY (id_disciplina) REFERENCES disciplina (id_disciplina) ON DELETE CASCADE
);