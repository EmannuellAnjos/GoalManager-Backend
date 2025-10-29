"""
Script de inicialização do backend GoalManager
Configura o ambiente, instala dependências e inicia o servidor
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime mensagem com status colorido"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "END": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['END']}")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print_status("Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print_status("Python 3.8+ é necessário", "ERROR")
        return False
    
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_status(f"Python {version} detectado", "SUCCESS")
    return True

def check_venv():
    """Verifica se está em um ambiente virtual"""
    print_status("Verificando ambiente virtual...")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print_status("Ambiente virtual ativo", "SUCCESS")
    else:
        print_status("Recomenda-se usar um ambiente virtual", "WARNING")
    
    return in_venv

def install_dependencies():
    """Instala as dependências do projeto"""
    print_status("Instalando dependências...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_status("Arquivo requirements.txt não encontrado", "ERROR")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print_status("Dependências instaladas com sucesso", "SUCCESS")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Erro ao instalar dependências: {e}", "ERROR")
        print(e.stdout)
        print(e.stderr)
        return False

def check_database_connection():
    """Verifica conexão com o banco de dados"""
    print_status("Verificando conexão com banco de dados...")
    
    try:
        # Importar apenas após instalar dependências
        from app.core.database import test_connection
        
        if test_connection():
            print_status("Conexão com banco de dados OK", "SUCCESS")
            return True
        else:
            print_status("Falha na conexão com banco de dados", "ERROR")
            return False
            
    except ImportError as e:
        print_status(f"Erro ao importar módulos: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Erro inesperado: {e}", "ERROR")
        return False

def create_env_file():
    """Cria arquivo .env se não existir"""
    print_status("Verificando arquivo de configuração...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print_status("Criando arquivo .env a partir do exemplo...")
            env_file.write_text(env_example.read_text())
            print_status("Arquivo .env criado. Configure suas variáveis!", "WARNING")
        else:
            print_status("Criando arquivo .env básico...")
            default_env = """# Configuração do GoalManager Backend
DATABASE_URL=mysql://root:123456@localhost:3306/goalmanager
JWT_SECRET_KEY=sua_chave_secreta_super_segura_aqui_123
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
"""
            env_file.write_text(default_env)
            print_status("Arquivo .env criado com valores padrão", "SUCCESS")
    else:
        print_status("Arquivo .env já existe", "SUCCESS")

def start_server():
    """Inicia o servidor FastAPI"""
    print_status("Iniciando servidor GoalManager...")
    
    try:
        # Usar uvicorn diretamente
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print_status(f"Erro ao iniciar servidor: {e}", "ERROR")
        return False
    except KeyboardInterrupt:
        print_status("Servidor interrompido pelo usuário", "INFO")
        return True

def main():
    """Função principal de inicialização"""
    print_status("=== GoalManager Backend Setup ===", "INFO")
    print_status("Inicializando projeto GoalManager...")
    
    # Verificações básicas
    if not check_python_version():
        sys.exit(1)
    
    check_venv()
    
    # Mudar para o diretório backend se necessário
    backend_dir = Path(__file__).parent
    if backend_dir.name == "backend":
        os.chdir(backend_dir)
        print_status(f"Diretório alterado para: {backend_dir}", "INFO")
    
    # Criar arquivo .env
    create_env_file()
    
    # Instalar dependências
    if not install_dependencies():
        print_status("Falha ao configurar ambiente. Verifique os erros acima.", "ERROR")
        sys.exit(1)
    
    # Verificar banco de dados
    if not check_database_connection():
        print_status("Atenção: Problemas com banco de dados detectados", "WARNING")
        print_status("Certifique-se de que o Docker Compose está rodando:", "INFO")
        print_status("  cd .. && docker-compose up -d", "INFO")
    
    # Informações finais
    print_status("=== Setup Concluído ===", "SUCCESS")
    print_status("Backend configurado e pronto para uso!")
    print_status("")
    print_status("Comandos úteis:")
    print_status("  Iniciar servidor: python run.py")
    print_status("  Documentação API: http://localhost:8000/docs")
    print_status("  Health Check: http://localhost:8000/health")
    print_status("  phpMyAdmin: http://localhost:8080")
    print_status("")
    
    # Perguntar se quer iniciar o servidor
    try:
        start = input("Iniciar servidor agora? (y/N): ").lower().strip()
        if start in ['y', 'yes', 's', 'sim']:
            start_server()
    except KeyboardInterrupt:
        print_status("\nSaindo...", "INFO")

if __name__ == "__main__":
    main()