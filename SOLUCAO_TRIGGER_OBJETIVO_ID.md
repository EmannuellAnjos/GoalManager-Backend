# 🔧 Solução: Erro objetivo_id no Trigger

## 🔍 Problema Identificado

O erro `Unknown column 'objetivo_id' in 'where clause'` estava ocorrendo porque existe um **trigger** na tabela `tarefas` que ainda referencia a coluna `objetivo_id`, que foi removida.

## ✅ Solução

### Opção 1: Executar SQL direto no MySQL (RECOMENDADO)

1. Abra o MySQL Workbench ou cliente MySQL de sua preferência
2. Conecte-se ao banco `goalmanager`
3. Execute o script `REMOVER_TRIGGER_SIMPLES.sql`:

```sql
-- Ver triggers problemáticos
SELECT 
    TRIGGER_NAME,
    ACTION_STATEMENT
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = DATABASE()
AND EVENT_OBJECT_TABLE = 'tarefas'
AND ACTION_STATEMENT LIKE '%objetivo_id%';

-- Remover todos os triggers da tabela tarefas
DROP TRIGGER IF EXISTS trg_tarefas_after_update;
DROP TRIGGER IF EXISTS trg_tarefas_before_update;
DROP TRIGGER IF EXISTS trg_tarefas_after_insert;
DROP TRIGGER IF EXISTS trg_tarefas_before_insert;
```

### Opção 2: Usar o script Python

Se tiver permissões adequadas no MySQL, execute:

```bash
python corrigir_trigger_tarefas.py
```

**Nota:** Se você receber erro de permissão `SUPER privilege`, use a Opção 1 (SQL direto).

## 📝 Por que remover o trigger?

O trigger antigo tinha esta lógica:

```sql
IF NEW.objetivo_id IS NOT NULL THEN
    CALL sp_recalcular_progresso_objetivo(NEW.objetivo_id);
END IF;
```

Como `objetivo_id` não existe mais na tabela `tarefas`, isso causa o erro.

**Agora**, o recálculo de progresso é feito no **código Python** (`app/services/progress.py`), que é mais seguro e flexível:

- ✅ Não depende de stored procedures
- ✅ Mais fácil de debugar
- ✅ Mais controle sobre quando recalcular
- ✅ Funciona corretamente com a nova estrutura (tarefas → hábitos → objetivos)

## 🧪 Como testar

Após remover o trigger, tente editar uma tarefa pelo frontend. O erro `Unknown column 'objetivo_id'` não deve mais aparecer.

## ⚠️ Importante

Não é necessário criar um novo trigger para recálculo de progresso, pois isso já é feito automaticamente no código Python quando você:
- Cria uma tarefa
- Atualiza uma tarefa
- Deleta uma tarefa
- Marca hábito como feito

Tudo isso já está implementado em `app/services/progress.py` e `app/api/tarefas.py`.

