# 📚 Exemplos de Uso - API de Tarefas (Após Migração)

## 🔑 Autenticação

Todos os exemplos assumem que você tem um token JWT válido:

```bash
TOKEN="seu_token_jwt_aqui"
```

---

## ✨ Criar Tarefa

### ✅ **CORRETO** - Com habitoId obrigatório

```bash
curl -X POST http://localhost:8000/api/v1/tarefas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "habitoId": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Fazer exercício matinal",
    "descricao": "30 minutos de corrida",
    "prioridade": "alta",
    "status": "backlog",
    "estimativaHoras": 0.5,
    "prazo": "2025-11-05",
    "tags": ["saude", "fitness"]
  }'
```

**Resposta:**
```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuarioId": "550e8400-e29b-41d4-a716-446655440000",
    "habitoId": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Fazer exercício matinal",
    "descricao": "30 minutos de corrida",
    "prioridade": "alta",
    "status": "backlog",
    "estimativaHoras": 0.5,
    "horasGastas": 0,
    "prazo": "2025-11-05",
    "progresso": 0,
    "posicao": null,
    "tags": ["saude", "fitness"],
    "anexos": null,
    "createdAt": "2025-11-01T20:30:00",
    "updatedAt": "2025-11-01T20:30:00"
  }
}
```

### ❌ **ERRO** - Sem habitoId (não funciona mais)

```bash
curl -X POST http://localhost:8000/api/v1/tarefas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Tarefa sem hábito"
  }'
```

**Resposta de Erro:**
```json
{
  "error": {
    "code": 422,
    "message": "Erro de validação dos dados",
    "type": "ValidationError",
    "details": [
      {
        "field": "body -> habito_id",
        "message": "Field required",
        "type": "missing"
      }
    ]
  }
}
```

---

## 📋 Listar Tarefas

### Por Hábito

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas/habito/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "habitoId": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Fazer exercício matinal",
      "status": "backlog",
      ...
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "habitoId": "550e8400-e29b-41d4-a716-446655440001",
      "titulo": "Alongamento pós-treino",
      "status": "fazendo",
      ...
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 2,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

### Todas as Tarefas (Com Filtros)

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas?page=1&limit=20&orderBy=createdAt&orderDir=desc" \
  -H "Authorization: Bearer $TOKEN"
```

### Filtrar por Status

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas?statusKanban=fazendo&statusKanban=backlog" \
  -H "Authorization: Bearer $TOKEN"
```

### Buscar por Texto

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas?busca=exercicio" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Obter Tarefa Específica

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuarioId": "550e8400-e29b-41d4-a716-446655440000",
    "habitoId": "550e8400-e29b-41d4-a716-446655440001",
    "titulo": "Fazer exercício matinal",
    ...
  }
}
```

---

## ✏️ Atualizar Tarefa

### Atualizar Campos Específicos

```bash
curl -X PUT "http://localhost:8000/api/v1/tarefas/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Exercício matinal - 45min",
    "estimativaHoras": 0.75,
    "status": "fazendo"
  }'
```

### Mudar Status

```bash
curl -X PATCH "http://localhost:8000/api/v1/tarefas/123e4567-e89b-12d3-a456-426614174000/status?statusKanban=feito" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "feito",
    "progresso": 100,
    "updatedAt": "2025-11-01T21:00:00"
  }
}
```

---

## 🗑️ Deletar Tarefa

```bash
curl -X DELETE "http://localhost:8000/api/v1/tarefas/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:** Status 204 (No Content)

---

## 📊 Visualização Kanban

### Obter Tarefas Agrupadas por Status

```bash
curl -X GET "http://localhost:8000/api/v1/tarefas/kanban/habito/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "data": {
    "backlog": [
      {
        "id": "...",
        "titulo": "Tarefa 1",
        ...
      }
    ],
    "fazendo": [
      {
        "id": "...",
        "titulo": "Tarefa 2",
        ...
      }
    ],
    "feito": [
      {
        "id": "...",
        "titulo": "Tarefa 3",
        ...
      }
    ]
  }
}
```

---

## 🎨 Exemplo Frontend - Criar Tarefa

### React/TypeScript

```typescript
// Tipo atualizado
interface TarefaCreate {
  habitoId: string;      // OBRIGATÓRIO ✅
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status?: 'backlog' | 'a_fazer' | 'fazendo' | 'bloqueada' | 'concluida';
  estimativaHoras?: number;
  prazo?: string;
  tags?: string[];
  anexos?: string[];
}

// Função para criar tarefa
async function criarTarefa(data: TarefaCreate) {
  const response = await fetch('http://localhost:8000/api/v1/tarefas', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  return response.json();
}

// Exemplo de uso
const novaTarefa: TarefaCreate = {
  habitoId: '550e8400-e29b-41d4-a716-446655440001', // ✅ Obrigatório
  titulo: 'Fazer exercício',
  descricao: '30 minutos de corrida',
  prioridade: 'alta',
  status: 'backlog',
  estimativaHoras: 0.5,
  prazo: '2025-11-05',
  tags: ['saude', 'fitness'],
};

criarTarefa(novaTarefa)
  .then(result => console.log('Tarefa criada:', result))
  .catch(error => console.error('Erro:', error));
```

---

## 🔄 Comparação: Antes vs Depois

### Antes da Migração ❌

```json
{
  "objetivoId": "...",  // Opcional
  "habitoId": "...",    // Opcional
  "titulo": "Tarefa"
}
```

### Depois da Migração ✅

```json
{
  "habitoId": "...",    // OBRIGATÓRIO
  "titulo": "Tarefa"
}
```

---

## ⚠️ Erros Comuns

### 1. Campo habitoId ausente

**Erro:**
```json
{
  "error": {
    "code": 422,
    "message": "Erro de validação dos dados",
    "details": [{"field": "body -> habito_id", "message": "Field required"}]
  }
}
```

**Solução:** Sempre incluir `habitoId` ao criar tarefa

### 2. Hábito não existe

**Erro:**
```json
{
  "error": {
    "code": 400,
    "message": "Erro ao criar tarefa: FOREIGN KEY constraint failed"
  }
}
```

**Solução:** Verificar se o `habitoId` existe no banco

---

## 📝 Notas Importantes

1. ✅ **habitoId é OBRIGATÓRIO** - Sempre forneça ao criar tarefa
2. ✅ **camelCase aceito** - Pode usar `habitoId` ou `habito_id`
3. ✅ **Resposta em camelCase** - API retorna em camelCase
4. ❌ **objetivoId não existe mais** - Não tente usar
5. ✅ **Campos extras ignorados** - Backend ignora campos desconhecidos

---

**Última Atualização:** 2025-11-01  
**Versão da API:** 1.0 (Pós-migração)

