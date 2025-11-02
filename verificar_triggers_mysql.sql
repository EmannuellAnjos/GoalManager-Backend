-- Verificar triggers na tabela tarefas
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- OU de forma mais detalhada:
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas';

-- Se algum trigger mencionar objetivo_id, remova:
-- DROP TRIGGER nome_do_trigger;

