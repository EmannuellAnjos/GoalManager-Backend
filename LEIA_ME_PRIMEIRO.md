# 🚀 LEIA-ME PRIMEIRO - Migração Tarefas

## ✅ O QUE FOI FEITO

### Backend (✅ COMPLETO)
- Código atualizado: tarefas agora são ligadas **apenas a hábitos**
- Campo `objetivo_id` removido dos schemas e modelos
- Campo `habito_id` agora é **obrigatório**
- Suporte a camelCase (frontend) ↔ snake_case (backend) configurado

### Scripts de Migração (✅ PRONTOS)
- Script Python automatizado criado
- Script SQL manual criado
- Documentação completa gerada

---

## 📋 O QUE VOCÊ PRECISA FAZER

### 1️⃣ **BACKEND - Migrar o Banco de Dados**

```bash
# Execute o script de migração
python migrar_remover_objetivo_tarefas.py
```

**O script vai:**
- ✅ Criar backup automático
- ✅ Verificar dados
- ✅ Remover coluna `objetivo_id`
- ✅ Tornar `habito_id` obrigatório (NOT NULL)
- ✅ Validar resultado

Depois, reinicie o servidor:
```bash
python run.py
```

### 2️⃣ **FRONTEND - Ajustar Interface**

**Copie este prompt para o desenvolvedor frontend:**

Arquivo: `PROMPT_COPIAR_FRONTEND.txt` (abra e copie todo o conteúdo)

**OU use a documentação completa em:** `PROMPT_FRONTEND_TAREFAS.md`

**Principais mudanças no frontend:**
- ❌ Remover campo "Objetivo"
- ✅ Tornar campo "Hábito" **obrigatório**
- ✅ Atualizar tipos TypeScript
- ✅ Adicionar validação

---

## 📁 ARQUIVOS CRIADOS

### Para Backend
| Arquivo | Uso |
|---------|-----|
| `migrar_remover_objetivo_tarefas.py` | ⭐ Execute este script! |
| `remove_objetivo_id_from_tarefas.sql` | Alternativa SQL manual |
| `MIGRACAO_TAREFAS.md` | Documentação completa da migração |
| `RESUMO_ALTERACOES.md` | Detalhes técnicos das mudanças |
| `EXEMPLOS_API_TAREFAS.md` | Exemplos de uso da API |

### Para Frontend
| Arquivo | Uso |
|---------|-----|
| `PROMPT_COPIAR_FRONTEND.txt` | ⭐ Copie e use este prompt! |
| `PROMPT_FRONTEND_TAREFAS.md` | Documentação completa frontend |

### Geral
| Arquivo | Uso |
|---------|-----|
| `LEIA_ME_PRIMEIRO.md` | Este arquivo (guia rápido) |

---

## 🎯 ORDEM DE EXECUÇÃO

```
1. Backend: python migrar_remover_objetivo_tarefas.py
2. Backend: python run.py (reiniciar servidor)
3. Backend: Testar API (opcional)
4. Frontend: Aplicar alterações do PROMPT_COPIAR_FRONTEND.txt
5. Frontend: Testar interface
6. ✅ Concluído!
```

---

## ⚠️ IMPORTANTE

### Antes de Migrar
- ✅ Faça backup do banco (`cp goalmanager.db goalmanager.db.backup`)
- ✅ Pare o servidor durante a migração
- ✅ Verifique se há tarefas sem `habito_id`

### Depois de Migrar
- ✅ Reinicie o servidor
- ✅ Teste criar uma tarefa (API)
- ✅ Teste o frontend após alterações

---

## 🔍 COMO VALIDAR

### Backend
```bash
# 1. Executar migração
python migrar_remover_objetivo_tarefas.py

# 2. Verificar banco
sqlite3 goalmanager.db
> PRAGMA table_info(tarefas);
> SELECT COUNT(*) FROM tarefas WHERE habito_id IS NULL;

# 3. Reiniciar servidor
python run.py
```

### Frontend
1. Abrir formulário de Nova Tarefa
2. Campo "Objetivo" **não deve existir**
3. Campo "Hábito" deve ter **asterisco (*)** e ser obrigatório
4. Criar tarefa deve funcionar
5. Listar tarefas deve funcionar

---

## 🆘 PROBLEMAS COMUNS

### "Tarefas sem habito_id"
**Solução:** O script vai perguntar o que fazer (deletar ou cancelar)

### "Campo objetivoId não encontrado"
**Solução:** Frontend ainda não foi atualizado. Use `PROMPT_COPIAR_FRONTEND.txt`

### "Erro 422 ao criar tarefa"
**Causa:** Frontend não está enviando `habitoId`  
**Solução:** Atualizar frontend conforme o prompt

---

## 📞 PRECISA DE AJUDA?

1. **Migração do banco:** Consulte `MIGRACAO_TAREFAS.md`
2. **Alterações frontend:** Consulte `PROMPT_FRONTEND_TAREFAS.md`
3. **Exemplos de API:** Consulte `EXEMPLOS_API_TAREFAS.md`
4. **Detalhes técnicos:** Consulte `RESUMO_ALTERACOES.md`

---

## ✅ CHECKLIST FINAL

### Backend
- [ ] Script de migração executado sem erros
- [ ] Backup do banco criado
- [ ] Coluna `objetivo_id` removida (verificado)
- [ ] Coluna `habito_id` é NOT NULL (verificado)
- [ ] Servidor reiniciado
- [ ] API testada (criar/listar tarefas)

### Frontend
- [ ] Tipos TypeScript atualizados
- [ ] Campo "Objetivo" removido
- [ ] Campo "Hábito" obrigatório
- [ ] Validação implementada
- [ ] Interface testada
- [ ] Criação de tarefa funciona
- [ ] Listagem de tarefas funciona

---

## 🎉 PRONTO!

Depois de concluir os passos acima, seu sistema estará completamente migrado com **tarefas ligadas apenas a hábitos**.

**Estimativa de tempo:**
- Backend (migração): ~5 minutos
- Frontend (alterações): ~20-30 minutos
- Testes: ~10 minutos

**TOTAL: ~45 minutos**

---

**Data:** 2025-11-01  
**Versão:** 1.0  
**Status:** Aguardando execução

