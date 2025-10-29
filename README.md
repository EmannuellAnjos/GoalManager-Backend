# GoalManager Backend API

API completa para o sistema de gerenciamento de objetivos, hábitos e tarefas pessoais.

## 🚀 Características

- **FastAPI** - Framework moderno e performático
- **SQLAlchemy** - ORM robusto para Python
- **MySQL** - Banco de dados relacional 
- **JWT Authentication** - Autenticação segura
- **Docker Support** - Containerização completa
- **API Documentation** - Swagger/OpenAPI automático

## 📋 Pré-requisitos

- Python 3.8+
- MySQL 8.0+ (via Docker recomendado)
- pip/pipenv/poetry

## 🛠️ Instalação Rápida

### 1. Clonar e configurar
```bash
cd backend
python run.py  # Script de setup automático
```

### 2. Configuração manual (alternativa)

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar banco de dados (Docker)
cd .. && docker-compose up -d

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🗄️ Estrutura do Projeto

```
backend/
├── app/
│   ├── api/           # Endpoints da API
│   │   ├── auth.py    # Autenticação e usuários
│   │   ├── objetivos.py
│   │   ├── habitos.py
│   │   └── tarefas.py
│   ├── core/          # Configurações centrais
│   │   ├── config.py
│   │   └── database.py
│   ├── models/        # Modelos SQLAlchemy
│   ├── schemas/       # Validação Pydantic
│   ├── services/      # Lógica de negócio
│   └── main.py        # Aplicação FastAPI
├── requirements.txt
├── .env.example
└── run.py            # Script de inicialização
```

## 🔗 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Cadastro de usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Renovar token

### Objetivos
- `GET /api/v1/objetivos` - Listar objetivos
- `POST /api/v1/objetivos` - Criar objetivo
- `PUT /api/v1/objetivos/{id}` - Atualizar objetivo
- `DELETE /api/v1/objetivos/{id}` - Excluir objetivo

### Hábitos
- `GET /api/v1/habitos` - Listar hábitos
- `POST /api/v1/habitos` - Criar hábito
- `POST /api/v1/habitos/{id}/marcar-feito` - Marcar como feito
- `POST /api/v1/habitos/{id}/reset-ciclo` - Resetar contador

### Tarefas
- `GET /api/v1/tarefas` - Listar tarefas
- `POST /api/v1/tarefas` - Criar tarefa
- `PATCH /api/v1/tarefas/{id}/status` - Alterar status Kanban
- `GET /api/v1/tarefas/kanban/habito/{id}` - Visualização Kanban

### Dashboard
- `GET /api/v1/dashboard/stats` - Estatísticas gerais
- `GET /api/v1/dashboard/recent-activity` - Atividade recente

## 🔒 Autenticação

A API usa autenticação JWT Bearer Token:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'

# Usar token nas requisições
curl -X GET "http://localhost:8000/api/v1/objetivos" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 🗃️ Banco de Dados

### Configuração com Docker
```bash
# Subir banco e ferramentas
docker-compose up -d

# Acessar phpMyAdmin: http://localhost:8080
# Acessar Adminer: http://localhost:8081
```

### Schema Principal
- `usuarios` - Dados dos usuários
- `objetivos` - Objetivos principais
- `habitos` - Hábitos vinculados aos objetivos  
- `tarefas` - Tarefas dos hábitos
- `habito_realizacoes` - Histórico de realizações
- `audit_logs` - Logs de auditoria

## ⚙️ Configuração (.env)

```env
# Banco de Dados
DATABASE_URL=mysql://root:123456@localhost:3306/goalmanager

# JWT
JWT_SECRET_KEY=sua_chave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Cobertura
pytest --cov=app

# Health check
curl http://localhost:8000/health
```

## 📚 Documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Desenvolvimento

### Comandos úteis

```bash
# Modo desenvolvimento com reload automático
uvicorn app.main:app --reload

# Verificar imports e sintaxe
python -m py_compile app/main.py

# Formatar código
black app/
isort app/

# Análise estática
flake8 app/
mypy app/
```

### Estrutura de Response

Todas as respostas seguem o padrão:

```json
{
  "success": true,
  "data": { /* dados específicos */ },
  "pagination": { /* apenas em listagens */ },
  "message": "string opcional"
}
```

### Filtros e Paginação

```bash
# Exemplo: listar objetivos com filtros
GET /api/v1/objetivos?busca=exercicio&status=ativo&page=1&limit=10

# Resposta inclui metadados de paginação
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🚀 Deploy

### Usando Docker
```bash
# Build da imagem
docker build -t goalmanager-api .

# Executar container
docker run -p 8000:8000 goalmanager-api
```

### Usando Gunicorn
```bash
# Instalar Gunicorn
pip install gunicorn

# Executar em produção
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- 📧 Email: [seu-email@exemplo.com]
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/goalmanager/issues)
- 📖 Wiki: [Documentação completa](https://github.com/seu-usuario/goalmanager/wiki)

---

⭐ **Se este projeto foi útil, considere dar uma estrela no GitHub!** ⭐