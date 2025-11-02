-- ========================================================
-- Verificar TUDO que pode estar causando o erro objetivo_id
-- Execute este script completo no MySQL
-- ========================================================

-- 1. Verificar estrutura da tabela (já sabemos que não tem objetivo_id)
DESCRIBE tarefas;

-- 2. Verificar TODOS os índices (incluindo definições)
SHOW INDEX FROM tarefas;

-- 3. Verificar se há TRIGGERS (PODE SER ISSO!)
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Ver triggers em detalhes
SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas';

-- 4. Verificar se há VIEWS que usam tarefas
SHOW FULL TABLES WHERE Table_type = 'VIEW';

SELECT 
    TABLE_NAME,
    VIEW_DEFINITION
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
AND VIEW_DEFINITION LIKE '%tarefas%';

-- 5. Verificar STORED PROCEDURES
SHOW PROCEDURE STATUS WHERE Db = DATABASE();

SELECT 
    ROUTINE_NAME,
    ROUTINE_DEFINITION
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = DATABASE()
AND ROUTINE_DEFINITION LIKE '%tarefas%'
AND ROUTINE_DEFINITION LIKE '%objetivo_id%';

-- 6. Verificar se há algum CHECK constraint que mencione objetivo_id
SELECT 
    CONSTRAINT_NAME,
    CHECK_CLAUSE
FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas';

-- 7. Tentar executar UPDATE manualmente para ver o erro exato
-- DESCOMENTE E EXECUTE:
-- UPDATE tarefas 
-- SET estimativa_horas = 1, horas_gastas = 1, updated_at = NOW()
-- WHERE id = 'tar-6' AND usuario_id = '550e8400-e29b-41d4-a716-446655440000';

