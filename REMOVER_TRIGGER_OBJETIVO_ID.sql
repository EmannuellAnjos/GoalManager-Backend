-- ====================================================
-- REMOVER/CORRIGIR TRIGGER COM objetivo_id
-- Execute este script diretamente no MySQL
-- ====================================================

-- 1. Ver TODOS os triggers da tabela tarefas
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas';

-- 2. Ver triggers que mencionam objetivo_id
SELECT 
    TRIGGER_NAME,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas'
AND ACTION_STATEMENT LIKE '%objetivo_id%';

-- 3. REMOVER TODOS OS TRIGGERS DA TABELA tarefas
-- Execute estes comandos para cada trigger encontrado acima:

-- Exemplo (substitua 'nome_do_trigger' pelo nome real encontrado):
-- DROP TRIGGER IF EXISTS nome_do_trigger;

-- Ou remova todos de uma vez:
DROP TRIGGER IF EXISTS trg_tarefas_after_update;
DROP TRIGGER IF EXISTS trg_tarefas_before_update;
DROP TRIGGER IF EXISTS trg_tarefas_after_insert;
DROP TRIGGER IF EXISTS trg_tarefas_before_insert;

-- 4. CRIAR TRIGGER CORRIGIDO (sem objetivo_id)
-- ATENCAO: Pode precisar de permissao SUPER ou configurar log_bin_trust_function_creators
DELIMITER $$

CREATE TRIGGER trg_tarefas_after_update
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Se status mudou para concluida, definir progresso como 100
    IF NEW.status = 'concluida' AND OLD.status != 'concluida' THEN
        UPDATE tarefas SET progresso = 100.00 WHERE id = NEW.id;
    END IF;
    
    -- NOTA: O recalculamento de progresso do habito agora e feito no codigo Python
    -- (app/services/progress.py), nao mais no trigger.
    -- Isso evita problemas com stored procedures e oferece mais controle.
    
    -- REMOVIDO: Nao ha mais objetivo_id na tabela tarefas
    -- IF NEW.objetivo_id IS NOT NULL THEN
    --     CALL sp_recalcular_progresso_objetivo(NEW.objetivo_id);
    -- END IF;
END$$

DELIMITER ;

-- 5. VERIFICAR se o trigger foi criado corretamente
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- 6. Se der erro de permissoes, configure (como root/admin):
-- SET GLOBAL log_bin_trust_function_creators = 1;

