-- ========================================================
-- Script para remover a coluna objetivo_id da tabela tarefas
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
-- SQLite não suporta DROP INDEX IF EXISTS com nome implícito, então vamos verificar primeiro
-- No MySQL/PostgreSQL, você usaria algo como:
-- DROP INDEX IF EXISTS idx_tarefas_objetivo_id ON tarefas;

-- Para SQLite, precisamos listar os índices primeiro:
-- SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tarefas';

-- Exemplo de remoção de índice (ajuste o nome conforme necessário):
-- DROP INDEX IF EXISTS idx_tarefas_objetivo_id;

-- 4. Alterar habito_id para NOT NULL (já que agora é obrigatório)
-- ATENÇÃO: SQLite não suporta ALTER COLUMN diretamente
-- Para SQLite, precisamos recriar a tabela:

-- Passo 4.1: Criar tabela temporária sem objetivo_id e com habito_id NOT NULL
CREATE TABLE tarefas_new (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    habito_id VARCHAR(36) NOT NULL,  -- Agora obrigatório
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    prioridade VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'backlog',
    estimativa_horas DECIMAL(6, 2),
    horas_gastas DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    prazo DATE,
    progresso DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    posicao INTEGER,
    tags TEXT,  -- JSON armazenado como TEXT no SQLite
    anexos TEXT,  -- JSON armazenado como TEXT no SQLite
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Passo 4.2: Copiar dados da tabela antiga (apenas tarefas com habito_id)
INSERT INTO tarefas_new (
    id, usuario_id, habito_id, titulo, descricao, prioridade, 
    status, estimativa_horas, horas_gastas, prazo, progresso, 
    posicao, tags, anexos, created_at, updated_at
)
SELECT 
    id, usuario_id, habito_id, titulo, descricao, prioridade,
    status, estimativa_horas, horas_gastas, prazo, progresso,
    posicao, tags, anexos, created_at, updated_at
FROM tarefas
WHERE habito_id IS NOT NULL;  -- Apenas tarefas com habito_id válido

-- Passo 4.3: Remover tabela antiga
DROP TABLE tarefas;

-- Passo 4.4: Renomear tabela nova
ALTER TABLE tarefas_new RENAME TO tarefas;

-- Passo 4.5: Recriar índices
CREATE INDEX idx_tarefas_usuario_id ON tarefas(usuario_id);
CREATE INDEX idx_tarefas_habito_id ON tarefas(habito_id);
CREATE INDEX idx_tarefas_prioridade ON tarefas(prioridade);
CREATE INDEX idx_tarefas_status ON tarefas(status);
CREATE INDEX idx_tarefas_prazo ON tarefas(prazo);
CREATE INDEX idx_tarefas_progresso ON tarefas(progresso);
CREATE INDEX idx_tarefas_posicao ON tarefas(posicao);
CREATE INDEX idx_tarefas_created_at ON tarefas(created_at);

-- 5. Verificar resultado
SELECT 
    COUNT(*) as total_tarefas,
    COUNT(habito_id) as todas_com_habito
FROM tarefas;

-- 6. Testar se a aplicação ainda funciona
-- Execute a aplicação e verifique se as tarefas são listadas corretamente

-- ========================================================
-- IMPORTANTE: ALTERNATIVA MAIS SIMPLES (se você não se importa em perder dados)
-- ========================================================
-- Se você preferir começar do zero com as tarefas:
-- 
-- DELETE FROM tarefas;
-- 
-- E então executar apenas os passos 4.1 a 4.5 acima
-- ========================================================

COMMIT;

