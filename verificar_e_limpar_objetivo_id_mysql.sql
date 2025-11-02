-- ========================================================
-- Script para VERIFICAR e LIMPAR completamente objetivo_id
-- Execute este script para diagnosticar o problema
-- ========================================================

-- ====================================================
-- 1. VERIFICAR COLUNA objetivo_id
-- ====================================================
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- ====================================================
-- 2. VERIFICAR TODAS AS FOREIGN KEYS
-- ====================================================
SELECT 
    kcu.CONSTRAINT_NAME,
    kcu.COLUMN_NAME,
    kcu.REFERENCED_TABLE_NAME,
    kcu.REFERENCED_COLUMN_NAME,
    rc.DELETE_RULE,
    rc.UPDATE_RULE
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
LEFT JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
    ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
    AND kcu.TABLE_SCHEMA = rc.CONSTRAINT_SCHEMA
WHERE kcu.TABLE_SCHEMA = DATABASE()
AND kcu.TABLE_NAME = 'tarefas';

-- ====================================================
-- 3. VERIFICAR TODOS OS ÍNDICES (incluindo compostos)
-- ====================================================
SHOW INDEX FROM tarefas;

-- Verificar índices que incluem objetivo_id
SELECT 
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME LIKE '%objetivo%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- ====================================================
-- 4. VERIFICAR TRIGGERS
-- ====================================================
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Verificar se há triggers que referenciam objetivo_id
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas';

-- ====================================================
-- 5. VERIFICAR VIEWS que usam tarefas
-- ====================================================
SELECT 
    TABLE_NAME,
    VIEW_DEFINITION
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
AND VIEW_DEFINITION LIKE '%tarefas%'
AND VIEW_DEFINITION LIKE '%objetivo_id%';

-- ====================================================
-- 6. LIMPAR TUDO RELACIONADO A objetivo_id
-- ====================================================

-- 6.1. Remover todas as foreign keys relacionadas
-- (Execute manualmente baseado nos resultados acima)
-- ALTER TABLE tarefas DROP FOREIGN KEY nome_da_constraint;

-- 6.2. Remover todos os índices que incluem objetivo_id
-- (Execute manualmente baseado nos resultados acima)
-- DROP INDEX nome_do_indice ON tarefas;

-- 6.3. Remover a coluna objetivo_id (se ainda existir)
-- ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- 6.4. Remover triggers (se existirem)
-- DROP TRIGGER nome_do_trigger;

-- ====================================================
-- 7. VERIFICAR ESTRUTURA FINAL
-- ====================================================
DESCRIBE tarefas;

