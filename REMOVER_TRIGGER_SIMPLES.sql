-- ====================================================
-- REMOVER TRIGGER COM objetivo_id (SIMPLES)
-- Execute este script diretamente no MySQL
-- ====================================================

-- 1. Ver triggers que mencionam objetivo_id
SELECT 
    TRIGGER_NAME,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas'
AND ACTION_STATEMENT LIKE '%objetivo_id%';

-- 2. REMOVER TODOS OS TRIGGERS DA TABELA tarefas
-- Isso remove qualquer trigger que possa estar causando problema

DROP TRIGGER IF EXISTS trg_tarefas_after_update;
DROP TRIGGER IF EXISTS trg_tarefas_before_update;
DROP TRIGGER IF EXISTS trg_tarefas_after_insert;
DROP TRIGGER IF EXISTS trg_tarefas_before_insert;

-- Verificar se foram removidos
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- NOTA: O recalculamento de progresso agora e feito no codigo Python
-- (app/services/progress.py), entao nao e necessario criar um novo trigger.

