# 🔧 Solução Final - Erro objetivo_id no MySQL

## 🔍 Diagnóstico

O erro `Unknown column 'objetivo_id' in 'where clause'` ocorre mesmo quando o SQL não mostra `objetivo_id` porque:

1. **Índices compostos** podem incluir `objetivo_id`
2. **Triggers** podem estar tentando usar `objetivo_id`
3. **Views** podem estar referenciando `objetivo_id`
4. **SQLAlchemy cache** pode ter metadata desatualizado

---

## ✅ SOLUÇÃO PASSO A PASSO

### Passo 1: Verificar o que ainda existe no MySQL

Execute no MySQL:

```sql
-- Ver estrutura
DESCRIBE tarefas;

-- Ver TODOS os índices (incluindo compostos)
SHOW INDEX FROM tarefas;

-- Ver foreign keys
SELECT 
    CONSTRAINT_NAME,
    COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas';

-- Ver triggers
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Ver views que usam tarefas
SELECT TABLE_NAME, VIEW_DEFINITION
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
AND VIEW_DEFINITION LIKE '%tarefas%';
```

### Passo 2: Remover TUDO relacionado a objetivo_id

Execute estes comandos na ordem:

```sql
-- 1. Remover foreign keys relacionadas a objetivo_id
SELECT CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Para cada constraint encontrada, execute:
-- ALTER TABLE tarefas DROP FOREIGN KEY nome_da_constraint;

-- 2. Remover TODOS os índices que incluem objetivo_id
-- (Pode haver índices compostos como: INDEX idx_composto (habito_id, objetivo_id))
SELECT INDEX_NAME, COLUMN_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';

-- Para cada índice encontrado, execute:
-- DROP INDEX nome_do_indice ON tarefas;

-- 3. Remover a coluna objetivo_id (se ainda existir)
ALTER TABLE tarefas DROP COLUMN objetivo_id;

-- 4. Verificar se há triggers
SHOW TRIGGERS FROM goalmanager WHERE `Table` = 'tarefas';

-- Se houver triggers que mencionam objetivo_id, remova:
-- DROP TRIGGER nome_do_trigger;
```

### Passo 3: Limpar cache do SQLAlchemy

```bash
python limpar_cache_sqlalchemy.py
```

### Passo 4: Reiniciar servidor

```bash
# Parar o servidor (Ctrl+C)
# Depois reiniciar:
python run.py
```

---

## 🚨 SOLUÇÃO RÁPIDA (Se você tem certeza que removeu objetivo_id)

Se você já removeu a coluna e índices, mas o erro persiste:

1. **Parar o servidor completamente**
2. **Limpar cache Python:**
   ```bash
   # Windows
   del __pycache__ /s /q
   del app\**\__pycache__ /s /q
   
   # Linux/Mac
   find . -type d -name __pycache__ -exec rm -r {} +
   ```
3. **Executar script de limpeza:**
   ```bash
   python limpar_cache_sqlalchemy.py
   ```
4. **Reiniciar servidor**

---

## 🔍 Comando SQL COMPLETO para Diagnosticar

Execute este SQL para ver TUDO relacionado a objetivo_id:

```sql
-- Verificar coluna
SELECT 'COLUNA' as tipo, COLUMN_NAME as nome
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id'

UNION ALL

-- Verificar índices
SELECT 'INDICE' as tipo, INDEX_NAME as nome
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id'

UNION ALL

-- Verificar foreign keys
SELECT 'FOREIGN_KEY' as tipo, CONSTRAINT_NAME as nome
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';
```

Se retornar qualquer linha, você ainda tem algo relacionado a `objetivo_id` que precisa ser removido!

---

## ✅ Verificação Final

Depois de tudo, execute:

```sql
-- Deve retornar 0 linhas
SELECT COUNT(*) 
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'tarefas'
AND COLUMN_NAME = 'objetivo_id';
```

Se retornar 0, está limpo! 🎉

