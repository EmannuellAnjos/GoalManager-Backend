# 🔄 Migração: Remover objetivo_id de Tarefas

## 📋 Resumo

Esta migração remove a ligação de tarefas com objetivos. A partir de agora, **tarefas são ligadas apenas a hábitos**.

## 🎯 Alterações

### Backend (Python)

✅ **Alterado:**
- `app/schemas/tarefa.py` - Removido `objetivo_id`, `habito_id` agora é obrigatório
- `app/models/tarefa.py` - Removida coluna `objetivo_id`, `habito_id` agora é NOT NULL

### Banco de Dados (SQLite)

🔄 **Será alterado:**
- Tabela `tarefas` - Coluna `objetivo_id` será removida
- Tabela `tarefas` - Coluna `habito_id` será NOT NULL (obrigatória)

## 🚀 Como Executar a Migração

### Opção 1: Script Python (RECOMENDADO)

```bash
# No diretório raiz do projeto
python migrar_remover_objetivo_tarefas.py
```

**O script irá:**
1. ✅ Verificar os dados existentes
2. 📦 Criar backup automático do banco
3. ⚠️ Alertar sobre tarefas sem `habito_id`
4. 🔄 Executar a migração
5. ✔️ Verificar o resultado

### Opção 2: SQL Manual

```bash
# Conectar ao banco
sqlite3 goalmanager.db

# Executar o script SQL
.read remove_objetivo_id_from_tarefas.sql
```

## ⚠️ IMPORTANTE - Antes de Migrar

### 1. Fazer Backup

```bash
# Backup manual
cp goalmanager.db goalmanager.db.backup
```

O script Python faz isso automaticamente, mas é bom ter um backup extra!

### 2. Verificar Tarefas Sem Hábito

```sql
SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;
```

Se houver tarefas sem `habito_id`, você tem 3 opções:

**Opção A: Deletar tarefas sem hábito**
```sql
DELETE FROM tarefas WHERE habito_id IS NULL;
```

**Opção B: Atribuir um hábito padrão**
```sql
-- Primeiro, crie um hábito padrão ou use um existente
SELECT id FROM habitos LIMIT 1;

-- Depois, atribua às tarefas
UPDATE tarefas 
SET habito_id = 'id_do_habito_aqui' 
WHERE habito_id IS NULL;
```

**Opção C: Cancelar a migração**
- Não execute a migração até resolver manualmente

## 📊 Impacto

### ✅ O que continuará funcionando:
- Listar tarefas por hábito
- Criar novas tarefas (agora sempre ligadas a um hábito)
- Editar tarefas existentes
- Deletar tarefas
- Visualização Kanban por hábito

### ❌ O que NÃO funcionará mais:
- Criar tarefas sem especificar um hábito
- Filtrar tarefas por objetivo (campo removido)
- APIs que retornam `objetivo_id` nas tarefas

## 🔍 Verificar Sucesso da Migração

### 1. Verificar Estrutura

```sql
PRAGMA table_info(tarefas);
```

Você **NÃO** deve ver `objetivo_id` na lista de colunas.

### 2. Verificar Dados

```sql
-- Todas as tarefas devem ter habito_id
SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;
-- Resultado esperado: 0

-- Contar tarefas migradas
SELECT COUNT(*) FROM tarefas;
```

### 3. Testar API

```bash
# Reiniciar servidor
python run.py

# Testar criação de tarefa (deve funcionar)
curl -X POST http://localhost:8000/api/v1/tarefas \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "habitoId": "id_do_habito",
    "titulo": "Teste",
    "status": "backlog"
  }'
```

## 🔙 Reverter Migração (Se Necessário)

Se algo der errado, você pode restaurar o backup:

```bash
# Parar o servidor primeiro!

# Restaurar backup
cp goalmanager.db.backup_TIMESTAMP goalmanager.db

# Ou se usou o script Python
cp goalmanager.db.backup_20251101_123456 goalmanager.db
```

Depois, reverta as alterações no código:
```bash
git restore app/schemas/tarefa.py app/models/tarefa.py
```

## 📝 Checklist Pós-Migração

- [ ] Backup criado e guardado em local seguro
- [ ] Migração executada sem erros
- [ ] Estrutura da tabela verificada (sem objetivo_id)
- [ ] Dados verificados (todas tarefas com habito_id)
- [ ] Servidor reiniciado
- [ ] API testada (criar, listar, editar, deletar)
- [ ] Frontend testado (formulário de tarefa)
- [ ] Nenhum erro no console/logs

## 🆘 Problemas Comuns

### Erro: "tarefas sem habito_id"
**Solução:** Siga a seção "Verificar Tarefas Sem Hábito" acima

### Erro: "table tarefas already exists"
**Solução:** A migração foi interrompida. Restaure o backup e tente novamente

### Erro: "column objetivo_id ainda existe"
**Solução:** A migração não foi concluída. Execute novamente ou use o SQL manual

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do script de migração
2. Confira se o backup foi criado corretamente
3. Reverta para o backup se necessário
4. Documente o erro encontrado

---

**Data da Migração:** 2025-11-01  
**Versão:** 1.0  
**Responsável:** Sistema de Migração Automática

