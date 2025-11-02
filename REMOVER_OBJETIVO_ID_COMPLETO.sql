-- ========================================================
-- Script COMPLETO para remover objetivo_id de tarefas (MySQL)
-- Resolve problema de Foreign Key que impede NOT NULL
-- ========================================================

-- IMPORTANTE: Faça backup antes de executar!

-- ====================================================
-- PASSO 1: Verificar estrutura atual
-- ====================================================

DESCRIBE tarefas;

-- ====================================================
-- PASSO 2: Verificar Foreign Keys existentes
-- ====================================================

SELECT 
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME,
    DELETE_RULE,
    UPDATE_RULE
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ====================================================
-- PASSO 3: Remover Foreign Key que usa SET NULL em habito_id
-- ====================================================

-- Verificar se existe a constraint tarefas_ibfk_3
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND CONSTRAINT_NAME = 'tarefas_ibfk_3';

-- Remover a foreign key (se existir)
ALTER TABLE tarefas DROP FOREIGN KEY tarefas_ibfk_3;

-- OU se tiver outro nome, verifique todas as FKs em habito_id:
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'habito_id'
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- E remova todas elas:
-- ALTER TABLE tarefas DROP FOREIGN KEY nome_da_constraint;

-- ====================================================
-- PASSO 4: Remover coluna objetivo_id (se existir)
-- ====================================================

-- Verificar se objetivo_id existe
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Se existir, remover foreign keys relacionadas primeiro
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND CONSTRAINT_TYPE = 'FOREIGN KEY'
AND CONSTRAINT_NAME LIKE '%objetivo%';

-- Remover cada foreign key de objetivo_id:
-- ALTER TABLE tarefas DROP FOREIGN KEY nome_da_constraint;

-- Remover índices de objetivo_id
SHOW INDEX FROM tarefas WHERE Column_name = 'objetivo_id';

-- Remover cada índice:
-- DROP INDEX nome_do_indice ON tarefas;

-- Agora remover a coluna objetivo_id
ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- ====================================================
-- PASSO 5: Garantir que todas tarefas têm habito_id
-- ====================================================

-- Verificar tarefas sem habito_id
SELECT COUNT(*) as tarefas_sem_habito FROM tarefas WHERE habito_id IS NULL;

-- Se houver tarefas sem habito_id, você precisa:
-- Opção A: Deletar
-- DELETE FROM tarefas WHERE habito_id IS NULL;

-- Opção B: Atribuir um habito_id válido
-- UPDATE tarefas SET habito_id = 'id_do_habito_aqui' WHERE habito_id IS NULL;

-- ====================================================
-- PASSO 6: Modificar habito_id para NOT NULL
-- ====================================================

ALTER TABLE tarefas MODIFY COLUMN habito_id VARCHAR(36) NOT NULL;

-- ====================================================
-- PASSO 7: Recriar Foreign Key corretamente (opcional)
-- ====================================================

-- Se você quiser manter a integridade referencial, recrie a FK sem SET NULL:
-- ALTER TABLE tarefas 
-- ADD CONSTRAINT tarefas_habito_fk 
-- FOREIGN KEY (habito_id) REFERENCES habitos(id) 
-- ON DELETE RESTRICT 
-- ON UPDATE CASCADE;

-- Ou se preferir CASCADE:
-- ALTER TABLE tarefas 
-- ADD CONSTRAINT tarefas_habito_fk 
-- FOREIGN KEY (habito_id) REFERENCES habitos(id) 
-- ON DELETE CASCADE 
-- ON UPDATE CASCADE;

-- ====================================================
-- PASSO 8: Verificar resultado
-- ====================================================

DESCRIBE tarefas;

-- Verificar se objetivo_id foi removido
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';
-- Deve retornar 0 linhas

-- Verificar se habito_id é NOT NULL
SELECT 
    COLUMN_NAME,
    IS_NULLABLE,
    COLUMN_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'habito_id';
-- IS_NULLABLE deve ser 'NO'

-- Verificar dados
SELECT COUNT(*) as total_tarefas FROM tarefas;
SELECT COUNT(*) as tarefas_sem_habito FROM tarefas WHERE habito_id IS NULL;
-- Deve ser 0 tarefas sem habito_id

