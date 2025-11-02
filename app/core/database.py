"""
Configuração e conexão com banco de dados MySQL
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar engine do SQLAlchemy
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,  # Log SQL queries em modo debug
    echo_pool=False  # Não logar pool de conexões
)

# Habilitar logging detalhado de SQL para debug
if settings.debug:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Configurar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para obter sessão do banco
def get_db():
    """
    Dependency que fornece sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Função para recarregar metadata do banco (resolve problemas de cache)
def refresh_metadata():
    """
    Recarrega o metadata das tabelas diretamente do banco de dados.
    Útil quando a estrutura do banco mudou mas o SQLAlchemy ainda tem cache antigo.
    """
    try:
        # Limpar metadata antigo
        Base.metadata.clear()
        
        # Recarregar todos os modelos para registrar novamente
        from app.models import usuario, objetivo, habito, tarefa, audit_log
        
        # Reflect das tabelas existentes no banco
        Base.metadata.reflect(bind=engine)
        
        logger.info("Metadata do banco recarregado com sucesso")
    except Exception as e:
        logger.warning(f"Erro ao recarregar metadata (pode ser normal se tabelas não existem): {e}")

# Função para inicializar banco de dados
def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    try:
        # Import todos os modelos aqui para registrá-los
        from app.models import usuario, objetivo, habito, tarefa, audit_log
        
        # Recarregar metadata do banco primeiro (resolve cache desatualizado)
        try:
            Base.metadata.reflect(bind=engine)
        except:
            pass  # Se não conseguir refletir, continua normalmente
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

# Função para testar conexão
def test_connection():
    """
    Testa a conexão com o banco de dados
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Conexão com banco de dados estabelecida com sucesso")
            return True
    except Exception as e:
        logger.error(f"Erro ao conectar com banco de dados: {e}")
        return False