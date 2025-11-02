-- ========================================================
-- Script para remover a coluna objetivo_id da tabela tarefas (MySQL)
-- Data: 2025-11-01
-- Descrição: Tarefas agora são ligadas apenas a hábitos
-- ========================================================

-- IMPORTANTE: Faça backup do banco de dados antes de executar!

-- 1. Verificar dados existentes (opcional - para análise)
SELECT 
    COUNT(*) as total_tarefas,
    COUNT(objetivo_id) as tarefas_com_objetivo,
    COUNT(habito_id) as tarefas_com_habito
FROM tarefas;

-- 2. Verificar se há tarefas sem habito_id (precisam ser corrigidas antes)
SELECT COUNT(*) as tarefas_sem_habito
FROM tarefas 
WHERE habito_id IS NULL;

-- Se houver tarefas sem habito_id, você pode deletá-las ou atribuir um habito_id:
-- DELETE FROM tarefas WHERE habito_id IS NULL;
-- OU
-- UPDATE tarefas SET habito_id = 'algum_habito_id' WHERE habito_id IS NULL;

-- 3. Remover o índice da coluna objetivo_id (se existir)
-- Primeiro, verificar índices:
-- SHOW INDEX FROM tarefas WHERE Column_name = 'objetivo_id';

-- Remover índice (ajuste o nome conforme necessário):
-- DROP INDEX idx_tarefas_objetivo_id ON tarefas;

-- 4. Remover foreign key constraint se existir
-- Primeiro, verificar constraints:
-- SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
-- FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
-- WHERE TABLE_SCHEMA = DATABASE()
-- AND TABLE_NAME = 'tarefas'
-- AND CONSTRAINT_NAME LIKE '%objetivo%';

-- Remover foreign key (ajuste o nome conforme necessário):
-- ALTER TABLE tarefas DROP FOREIGN KEY fk_tarefas_objetivo_id;

-- 5. Remover a coluna objetivo_id
ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- 6. Alterar habito_id para NOT NULL (se ainda não for)
-- Primeiro, garantir que não há tarefas sem habito_id:
DELETE FROM tarefas WHERE habito_id IS NULL;

-- Agora alterar para NOT NULL:
ALTER TABLE tarefas MODIFY COLUMN habito_id VARCHAR(36) NOT NULL;

-- 7. Verificar resultado
SELECT 
    COUNT(*) as total_tarefas,
    COUNT(habito_id) as todas_com_habito
FROM tarefas;

-- 8. Verificar estrutura da tabela
DESCRIBE tarefas;

-- ========================================================
-- IMPORTANTE: ALTERNATIVA MAIS SIMPLES (se você não se importa em perder dados)
-- ========================================================
-- Se você preferir começar do zero com as tarefas:
-- 
-- DELETE FROM tarefas;
-- ALTER TABLE tarefas DROP COLUMN objetivo_id;
-- ALTER TABLE tarefas MODIFY COLUMN habito_id VARCHAR(36) NOT NULL;
-- ========================================================

