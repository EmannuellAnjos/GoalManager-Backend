"""
Aplicação principal FastAPI - GoalManager Backend
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.database import init_db, test_connection
from app.api import objetivos
from app.api import habitos, tarefas, auth

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função de inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Inicializando GoalManager API...")
    
    # Testar conexão com banco de dados
    if not test_connection():
        logger.error("Falha ao conectar com banco de dados")
        raise Exception("Não foi possível conectar com o banco de dados")
    
    # Inicializar banco de dados (criar tabelas se necessário)
    try:
        init_db()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise
    
    logger.info("API inicializada com sucesso!")
    yield
    
    # Shutdown
    logger.info("Finalizando GoalManager API...")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    debug=settings.debug,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manipulador de exceções global
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Erro interno do servidor",
                "type": "InternalServerError"
            }
        }
    )

# Rotas básicas
@app.get("/")
async def root():
    return {
        "message": "GoalManager API",
        "version": settings.version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    db_status = test_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "timestamp": "2025-10-29T10:00:00Z",
        "version": settings.version
    }

# Incluir routers das APIs
app.include_router(objetivos.router, prefix="/api/v1")
app.include_router(habitos.router, prefix="/api/v1")
app.include_router(tarefas.router, prefix="/api/v1")
app.include_router(auth.auth_router, prefix="/api/v1")
app.include_router(auth.user_router, prefix="/api/v1")
app.include_router(auth.dashboard_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )