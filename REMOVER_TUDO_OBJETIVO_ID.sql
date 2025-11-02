-- ========================================================
-- REMOVER TUDO relacionado a objetivo_id na tabela tarefas
-- Execute este script COMPLETO no MySQL
-- ========================================================

-- IMPORTANTE: Faça backup antes!

-- ====================================================
-- 1. REMOVER TODAS AS FOREIGN KEYS relacionadas
-- ====================================================

-- Listar todas as foreign keys
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Remover cada uma (substitua 'nome_da_fk' pelos nomes encontrados acima)
-- ALTER TABLE tarefas DROP FOREIGN KEY tarefas_ibfk_1;
-- ALTER TABLE tarefas DROP FOREIGN KEY tarefas_ibfk_2;
-- etc...

-- OU remova TODAS as foreign keys de uma vez (CUIDADO!):
-- SET @sql = NULL;
-- SELECT GROUP_CONCAT(CONCAT('ALTER TABLE tarefas DROP FOREIGN KEY ', CONSTRAINT_NAME, ';') SEPARATOR ' ')
-- INTO @sql
-- FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
-- WHERE TABLE_SCHEMA = DATABASE()
-- AND TABLE_NAME = 'tarefas'
-- AND COLUMN_NAME = 'objetivo_id'
-- AND CONSTRAINT_NAME IS NOT NULL;
-- SELECT @sql; -- Veja o SQL gerado
-- PREPARE stmt FROM @sql;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;

-- ====================================================
-- 2. REMOVER TODOS OS ÍNDICES que incluem objetivo_id
-- ====================================================

-- Ver TODOS os índices que incluem objetivo_id (incluindo índices compostos)
SELECT DISTINCT INDEX_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Remover cada índice (substitua 'nome_do_indice' pelos nomes encontrados)
-- DROP INDEX idx_tarefas_objetivo_id ON tarefas;
-- DROP INDEX idx_composto_habito_objetivo ON tarefas; -- se existir
-- etc...

-- ====================================================
-- 3. REMOVER A COLUNA objetivo_id
-- ====================================================

-- Verificar se existe
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Se existir, remover:
ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- ====================================================
-- 4. VERIFICAR TRIGGERS
-- ====================================================

SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Se algum trigger mencionar objetivo_id, remova:
-- DROP TRIGGER nome_do_trigger;

-- ====================================================
-- 5. VERIFICAR VIEWS
-- ====================================================

SELECT TABLE_NAME, VIEW_DEFINITION
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
AND VIEW_DEFINITION LIKE '%tarefas%'
AND VIEW_DEFINITION LIKE '%objetivo_id%';

-- Se houver views, você precisa:
-- DROP VIEW nome_da_view;
-- E recriar sem objetivo_id

-- ====================================================
-- 6. VERIFICAÇÃO FINAL
-- ====================================================

-- Ver estrutura final
DESCRIBE tarefas;

-- Verificar que objetivo_id não existe mais
SELECT COUNT(*) as objetivo_id_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';
-- Deve retornar 0

-- Verificar índices finais
SHOW INDEX FROM tarefas;

