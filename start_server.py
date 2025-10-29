#!/usr/bin/env python
"""
Script para iniciar o servidor GoalManager
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Mudar para o diretório do backend
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print(f"Iniciando servidor no diretório: {backend_dir}")
    print("Servidor será iniciado em: http://localhost:8000")
    print("Documentação em: http://localhost:8000/docs")
    print("Pressione Ctrl+C para parar")
    print("-" * 50)
    
    try:
        # Iniciar servidor uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()