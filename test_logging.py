"""
Script de teste para o sistema de logging de requisições
"""
import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def test_logging_system():
    """Testa o sistema de logging fazendo várias requisições"""
    
    print("🧪 Testando sistema de logging...")
    
    # 1. Teste de rota pública (sem autenticação)
    print("\n1. Testando rota pública...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/health")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Servidor não está rodando. Inicie com: python run.py")
        return
    
    # 2. Teste de registro de usuário
    print("\n2. Testando registro de usuário...")
    user_data = {
        "nome": "Usuário Teste",
        "email": f"teste_{int(time.time())}@example.com",
        "password": "senha123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            token = data["data"]["access_token"]
            print(f"   Token obtido: {token[:50]}...")
            
            # 3. Teste de rota autenticada
            print("\n3. Testando rota autenticada...")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Obter perfil
            response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
            print(f"   Status perfil: {response.status_code}")
            
            # Obter estatísticas do dashboard
            response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
            print(f"   Status dashboard: {response.status_code}")
            
            # 4. Teste de requisição com dados
            print("\n4. Testando criação de objetivo...")
            objetivo_data = {
                "titulo": "Objetivo de Teste",
                "descricao": "Este é um objetivo criado para testar o logging",
                "meta_numerica": 100,
                "unidade_medida": "pontos",
                "data_limite": "2025-12-31",
                "categoria": "teste"
            }
            
            response = requests.post(f"{BASE_URL}/objetivos", json=objetivo_data, headers=headers)
            print(f"   Status objetivo: {response.status_code}")
            
    except Exception as e:
        print(f"   Erro: {e}")
    
    print("\n✅ Teste concluído! Verifique os logs no console do servidor.")

if __name__ == "__main__":
    test_logging_system()