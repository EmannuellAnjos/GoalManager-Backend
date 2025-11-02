# 📝 Resumo das Alterações - Tarefas Ligadas Apenas a Hábitos

## 🎯 Objetivo
Remover a ligação de tarefas com objetivos. Agora **tarefas são ligadas exclusivamente a hábitos**.

---

## ✅ Alterações Realizadas

### 1. **Schemas Atualizados** (`app/schemas/tarefa.py`)

#### `TarefaCreate`
- ❌ Removido: `objetivo_id: Optional[str]`
- ✅ Alterado: `habito_id: str` (agora obrigatório, não mais opcional)

#### `TarefaResponse`
- ❌ Removido: `objetivo_id: Optional[str]`
- ✅ Alterado: `habito_id: str` (não mais opcional)

#### `TarefaCompleta`
- ❌ Removido: `objetivo_titulo` e `objetivo_cor`
- ✅ Mantido: `habito_titulo` e `habito_frequencia`

#### `TarefaFilters`
- ❌ Removido: `objetivo_id` do filtro
- ✅ Mantido: `habito_id` para filtrar por hábito

### 2. **Modelo Atualizado** (`app/models/tarefa.py`)

```python
# ANTES:
objetivo_id = Column(String(36), nullable=True, index=True)
habito_id = Column(String(36), nullable=True, index=True)

# DEPOIS:
# objetivo_id removido - tarefas agora são ligadas apenas a hábitos
habito_id = Column(String(36), nullable=False, index=True)
```

### 3. **Scripts de Migração Criados**

#### 📄 `remove_objetivo_id_from_tarefas.sql`
- Script SQL puro para executar manualmente
- Inclui todos os comandos SQL necessários
- Com comentários explicativos

#### 🐍 `migrar_remover_objetivo_tarefas.py` ⭐ **RECOMENDADO**
- Script Python automatizado
- Cria backup automático
- Verifica dados antes e depois
- Interface interativa
- Tratamento de erros

#### 📖 `MIGRACAO_TAREFAS.md`
- Documentação completa da migração
- Guia passo a passo
- Checklist de verificação
- Solução de problemas comuns

---

## 🚀 Próximos Passos

### 1️⃣ **Executar a Migração do Banco**

```bash
# OPÇÃO RECOMENDADA: Script Python
python migrar_remover_objetivo_tarefas.py
```

OU

```bash
# OPÇÃO MANUAL: SQL direto
sqlite3 goalmanager.db < remove_objetivo_id_from_tarefas.sql
```

### 2️⃣ **Reiniciar o Servidor**

```bash
python run.py
```

### 3️⃣ **Testar o Frontend**

Ao criar/editar uma tarefa no frontend:
- ✅ O campo "Objetivo" não deve mais aparecer
- ✅ O campo "Hábito" é agora **obrigatório**
- ✅ Deve funcionar normalmente após a migração

---

## 📊 Impacto nas APIs

### ✅ Endpoints que continuam funcionando:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/tarefas` | GET | Listar tarefas (por hábito) |
| `/api/v1/tarefas` | POST | Criar tarefa (requer `habitoId`) |
| `/api/v1/tarefas/{id}` | GET | Obter tarefa específica |
| `/api/v1/tarefas/{id}` | PUT | Atualizar tarefa |
| `/api/v1/tarefas/{id}` | DELETE | Deletar tarefa |
| `/api/v1/tarefas/habito/{habitoId}` | GET | Listar tarefas por hábito |
| `/api/v1/tarefas/kanban/habito/{habitoId}` | GET | Visualização Kanban |

### ❌ Mudanças nos parâmetros:

**Antes:**
```json
{
  "objetivoId": "...",  // Opcional
  "habitoId": "...",    // Opcional
  "titulo": "Tarefa"
}
```

**Agora:**
```json
{
  "habitoId": "...",    // OBRIGATÓRIO ✅
  "titulo": "Tarefa"
}
```

---

## ⚠️ IMPORTANTE - Checklist Antes de Migrar

- [ ] **Backup criado** (`cp goalmanager.db goalmanager.db.backup`)
- [ ] **Servidor parado** (nenhuma requisição durante migração)
- [ ] **Verificar tarefas sem hábito:**
  ```sql
  SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;
  ```
- [ ] Se houver tarefas sem hábito, decidir o que fazer com elas

---

## 🔍 Validação Pós-Migração

### Banco de Dados:
```sql
-- 1. Verificar que objetivo_id foi removido
PRAGMA table_info(tarefas);

-- 2. Verificar que todas tarefas têm habito_id
SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;
-- Resultado esperado: 0

-- 3. Contar tarefas
SELECT COUNT(*) FROM tarefas;
```

### Backend:
```bash
# Reiniciar servidor
python run.py

# Ver logs - não deve ter erros relacionados a objetivo_id
```

### Frontend:
1. Abrir o formulário de Nova Tarefa
2. Verificar que campo "Objetivo" não existe mais
3. Verificar que campo "Hábito" é obrigatório
4. Criar uma tarefa de teste
5. Editar a tarefa criada
6. Verificar listagem de tarefas

---

## 🔙 Rollback (Se Necessário)

Se algo der errado:

### 1. Restaurar Banco:
```bash
# Parar servidor
cp goalmanager.db.backup goalmanager.db
```

### 2. Reverter Código:
```bash
git restore app/schemas/tarefa.py app/models/tarefa.py
```

### 3. Reiniciar:
```bash
python run.py
```

---

## 📁 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `remove_objetivo_id_from_tarefas.sql` | Script SQL para migração |
| `migrar_remover_objetivo_tarefas.py` | Script Python automatizado ⭐ |
| `MIGRACAO_TAREFAS.md` | Documentação completa |
| `RESUMO_ALTERACOES.md` | Este arquivo |

---

## 🎉 Benefícios

✅ **Modelo de dados mais simples**  
✅ **Menos ambiguidade** (tarefa só pode pertencer a um hábito)  
✅ **Validação mais forte** (habito_id obrigatório)  
✅ **Código mais limpo** (menos campos opcionais)  
✅ **Frontend mais intuitivo** (um campo a menos no formulário)

---

## 📞 Problemas?

Se encontrar qualquer problema:
1. Verifique os logs do servidor
2. Confira se o backup existe
3. Leia `MIGRACAO_TAREFAS.md` para soluções
4. Em caso de dúvida, **RESTAURE O BACKUP**

---

**Data:** 2025-11-01  
**Versão:** 1.0  
**Status:** ✅ Código atualizado | ⏳ Aguardando migração do banco

