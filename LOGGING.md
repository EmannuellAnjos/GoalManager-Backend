# Sistema de Logging de Requisições - GoalManager Backend

Este documento descreve o sistema de logging implementado para registrar todas as requisições HTTP realizadas na API, incluindo informações detalhadas do usuário.

## 📋 Funcionalidades

### ✅ O que é registrado

**Para cada requisição:**
- 🌐 **Informações básicas**: Método HTTP, URL, IP do cliente, User-Agent
- 👤 **Dados do usuário**: ID, nome, email, status (quando autenticado)
- 📦 **Corpo da requisição**: Resumo do payload (sem dados sensíveis)
- ⏱️ **Tempo de processamento**: Duração da requisição
- 📊 **Status da resposta**: Código HTTP de retorno
- ❌ **Erros**: Detalhes de exceções quando ocorrem

### 🔒 Segurança

- **Dados sensíveis protegidos**: Senhas, tokens e outros campos sensíveis não são logados
- **Cache inteligente**: Informações do usuário são cacheadas por 5 minutos para otimização
- **Fallback gracioso**: Em caso de erro ao buscar dados do usuário, informações básicas são mantidas

## 📝 Formato dos Logs

### Requisição Recebida
```
🌐 REQUISIÇÃO RECEBIDA | Método: POST | URL: http://localhost:8000/api/v1/auth/login | IP: 127.0.0.1 | User-Agent: PostmanRuntime/7.28.0 | Usuário: Anônimo | Body: JSON com dados sensíveis (45 bytes)
```

### Resposta Enviada
```
✅ RESPOSTA ENVIADA | Status: 200 | Tempo: 0.234s | Método: POST | URL: http://localhost:8000/api/v1/auth/login | Usuário: ID:123 | Nome:João Silva | Email:joao@example.com | Ativo:True
```

### Erro na Requisição
```
❌ ERRO NA REQUISIÇÃO | Erro: Token inválido | Tempo: 0.045s | Método: GET | URL: http://localhost:8000/api/v1/user/profile | Usuário: Anônimo
```

## 🚀 Como Usar

### 1. Configuração Automática
O middleware é automaticamente configurado quando a aplicação inicia. Não é necessária configuração adicional.

### 2. Visualizar Logs
Os logs são exibidos no console onde o servidor está rodando:

```bash
# Iniciar servidor
python run.py

# Os logs aparecerão automaticamente para cada requisição
```

### 3. Teste do Sistema
Use o script de teste incluído:

```bash
# Em um terminal separado (com o servidor rodando)
python test_logging.py
```

## ⚙️ Configurações

### Configurar Nível de Log
No arquivo `app/main.py`, você pode ajustar o nível de logging:

```python
# Para logs mais detalhados
logging.basicConfig(level=logging.DEBUG)

# Para logs apenas de erro
logging.basicConfig(level=logging.ERROR)
```

### Cache de Usuário
O sistema mantém um cache simples das informações do usuário:

- **TTL (Time To Live)**: 5 minutos
- **Localização**: `app/middleware/logging.py`
- **Variável**: `_cache_ttl`

Para alterar o tempo de cache:

```python
_cache_ttl = timedelta(minutes=10)  # Cache por 10 minutos
```

## 🔧 Personalização

### Adicionar Campos ao Log
Para incluir mais informações no log, edite o método `dispatch` em `app/middleware/logging.py`:

```python
# Exemplo: adicionar informação de referer
referer = request.headers.get("referer", "none")

logger.info(
    f"🌐 REQUISIÇÃO RECEBIDA | "
    f"Método: {method} | "
    f"URL: {url} | "
    f"IP: {client_ip} | "
    f"Referer: {referer} | "  # Nova informação
    f"Usuário: {self._format_user_info(user_info)}"
)
```

### Filtrar Rotas
Para excluir certas rotas do logging (como health checks), adicione filtros:

```python
async def dispatch(self, request: Request, call_next):
    # Pular logging para rotas de health check
    if request.url.path in ["/health", "/api/v1/dashboard/health"]:
        return await call_next(request)
    
    # Continue com o logging normal...
```

### Alterar Formato de Saída
Para modificar o formato dos logs, edite os métodos:

- `_format_user_info()`: Formato das informações do usuário
- `_get_request_body_info()`: Formato das informações do corpo da requisição

## 🐛 Troubleshooting

### Logs não aparecem
1. Verifique se o nível de logging está correto (`INFO` ou superior)
2. Confirme se o middleware está registrado em `app/main.py`
3. Verifique se não há conflitos de logger

### Performance lenta
1. Aumente o tempo de cache do usuário
2. Considere implementar um cache mais robusto (Redis, Memcached)
3. Desabilite logging de corpo da requisição para payloads grandes

### Erro ao buscar dados do usuário  
1. Verifique a conexão com o banco de dados
2. O sistema usa fallback automático em caso de erro
3. Logs de warning serão exibidos para erros de banco

## 📊 Exemplo de Saída Completa

```
2025-10-29 14:30:15 - app.middleware.logging - INFO - 🌐 REQUISIÇÃO RECEBIDA | Método: POST | URL: http://localhost:8000/api/v1/auth/register | IP: 127.0.0.1 | User-Agent: curl/7.68.0 | Usuário: Anônimo | Body: JSON: {"nome":"João Silva","email":"joao@example.com"}

2025-10-29 14:30:15 - app.middleware.logging - INFO - ✅ RESPOSTA ENVIADA | Status: 201 | Tempo: 0.156s | Método: POST | URL: http://localhost:8000/api/v1/auth/register | Usuário: Anônimo

2025-10-29 14:30:20 - app.middleware.logging - INFO - 🌐 REQUISIÇÃO RECEBIDA | Método: GET | URL: http://localhost:8000/api/v1/user/profile | IP: 127.0.0.1 | User-Agent: curl/7.68.0 | Usuário: ID:123 | Nome:João Silva | Email:joao@example.com | Ativo:True | Body: não aplicável

2025-10-29 14:30:20 - app.middleware.logging - INFO - ✅ RESPOSTA ENVIADA | Status: 200 | Tempo: 0.089s | Método: GET | URL: http://localhost:8000/api/v1/user/profile | Usuário: ID:123 | Nome:João Silva | Email:joao@example.com | Ativo:True
```

## 🎯 Benefícios

- **Auditoria completa**: Rastrea todas as ações dos usuários
- **Debugging facilitado**: Informações detalhadas para resolução de problemas
- **Monitoramento**: Acompanhamento de uso e performance
- **Segurança**: Detecção de tentativas de acesso não autorizado
- **Analytics**: Base para análise de comportamento dos usuários