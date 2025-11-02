-- ========================================================
-- Script RÁPIDO para remover objetivo_id de tarefas (MySQL)
-- Execute este SQL diretamente no MySQL
-- ========================================================

-- IMPORTANTE: Faça backup antes!

-- 1. Verificar estrutura atual
DESCRIBE tarefas;

-- 2. Verificar se objetivo_id existe
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- 3. Verificar foreign keys relacionadas
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND CONSTRAINT_TYPE = 'FOREIGN KEY'
AND CONSTRAINT_NAME LIKE '%objetivo%';

-- 4. Remover foreign keys (se existirem - substitua 'nome_da_fk' pelo nome real)
-- ALTER TABLE tarefas DROP FOREIGN KEY nome_da_fk;

-- 5. Verificar índices
SHOW INDEX FROM tarefas WHERE Column_name = 'objetivo_id';

-- 6. Remover índices (se existirem - substitua 'nome_do_indice' pelo nome real)
-- DROP INDEX nome_do_indice ON tarefas;

-- 7. REMOVER A COLUNA (execute apenas se objetivo_id existir!)
ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- 8. Tornar habito_id NOT NULL (se ainda não for)
-- Primeiro, verificar se há tarefas sem habito_id
SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;

-- Se houver, você precisa deletá-las ou atribuir um habito_id:
-- DELETE FROM tarefas WHERE habito_id IS NULL;
-- OU
-- UPDATE tarefas SET habito_id = 'id_do_habito' WHERE habito_id IS NULL;

-- Depois, tornar NOT NULL:
ALTER TABLE tarefas MODIFY COLUMN habito_id VARCHAR(36) NOT NULL;

-- 9. Verificar resultado
DESCRIBE tarefas;

-- 10. Verificar dados
SELECT COUNT(*) as total_tarefas FROM tarefas;
SELECT COUNT(*) as tarefas_sem_habito FROM tarefas WHERE habito_id IS NULL;

