-- ====================================================
-- CORRIGIR TRIGGER DA TABELA TAREFAS
-- Remove referência a objetivo_id que não existe mais
-- ====================================================

-- 1. Verificar triggers existentes
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas';

-- ====================================================
-- 2. DROPAR TRIGGER(S) EXISTENTE(S) QUE REFERENCIAM objetivo_id
-- ====================================================

-- Remover trigger de UPDATE (provavelmente se chama trg_tarefas_after_update ou similar)
-- Execute este comando para cada trigger encontrado acima que menciona objetivo_id:
-- DROP TRIGGER IF EXISTS nome_do_trigger;

-- Exemplo comum:
-- DROP TRIGGER IF EXISTS trg_tarefas_after_update;
-- DROP TRIGGER IF EXISTS trg_tarefas_before_update;

-- ====================================================
-- 3. RECRIAR TRIGGER SEM REFERÊNCIA A objetivo_id
-- ====================================================

-- Trigger AFTER UPDATE (corrigido)
DELIMITER $$

CREATE TRIGGER trg_tarefas_after_update
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Se status mudou para concluida, definir progresso como 100
    IF NEW.status = 'concluida' AND OLD.status != 'concluida' THEN
        UPDATE tarefas SET progresso = 100.00 WHERE id = NEW.id;
    END IF;
    
    -- Recalcular progresso do hábito relacionado (se houver)
    IF NEW.habito_id IS NOT NULL THEN
        -- Note: sp_recalcular_progresso_habito deve existir no banco
        -- Se não existir, você pode remover esta linha ou criar a stored procedure
        -- CALL sp_recalcular_progresso_habito(NEW.habito_id);
        
        -- Alternativamente, se a stored procedure não existir, você pode calcular diretamente:
        -- Mas isso pode ser complexo, então comentado por enquanto
    END IF;
    
    -- REMOVIDO: Não há mais objetivo_id
    -- IF NEW.objetivo_id IS NOT NULL THEN
    --     CALL sp_recalcular_progresso_objetivo(NEW.objetivo_id);
    -- END IF;
END$$

DELIMITER ;

-- ====================================================
-- 4. VERIFICAR SE O TRIGGER FOI CRIADO CORRETAMENTE
-- ====================================================

SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Ver detalhes do trigger criado
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas'
AND TRIGGER_NAME = 'trg_tarefas_after_update';

