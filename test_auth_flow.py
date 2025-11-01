"""
Script para testar autenticação e demonstrar como o frontend deve enviar informações
"""
import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def test_authentication_flow():
    """Testa o fluxo completo de autenticação"""
    
    print("🔐 TESTANDO FLUXO DE AUTENTICAÇÃO\n")
    
    # 1. Testar requisição sem token (deve aparecer como Anônimo)
    print("1️⃣ Fazendo requisição SEM token...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/health")
        print(f"   ✅ Status: {response.status_code}")
        print("   📝 Log esperado: Usuário Anônimo\n")
    except requests.exceptions.ConnectionError:
        print("   ❌ Servidor não está rodando. Inicie com: python run.py")
        return
    
    # 2. Registrar novo usuário
    print("2️⃣ Registrando novo usuário...")
    user_data = {
        "nome": "João Silva",
        "email": f"joao_{int(time.time())}@example.com",
        "password": "senha123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"   ✅ Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            token = data["data"]["access_token"]
            user_info = data["data"]["user"]
            
            print(f"   🎟️ Token obtido: {token[:50]}...")
            print(f"   👤 Usuário: {user_info['nome']} ({user_info['email']})")
            print("   📝 Log esperado: Usuário Anônimo (ainda não autenticado)\n")
            
            # 3. Fazer login para obter token limpo
            print("3️⃣ Fazendo login...")
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data["data"]["access_token"]
                user_info = data["data"]["user"]
                
                print(f"   🎟️ Novo token: {token[:50]}...")
                print("   📝 Log esperado: Usuário Anônimo (login não usa token)\n")
                
                # 4. Agora fazer requisições autenticadas
                print("4️⃣ Fazendo requisições AUTENTICADAS...")
                
                # IMPORTANTE: Este é o formato correto que o frontend deve usar
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                print(f"   📋 Headers enviados:")
                print(f"      Authorization: Bearer {token[:20]}...")
                print(f"      Content-Type: application/json\n")
                
                # Obter perfil
                print("   4.1 Obtendo perfil do usuário...")
                response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
                print(f"       ✅ Status: {response.status_code}")
                print(f"       📝 Log esperado: Usuário {user_info['nome']} ({user_info['email']})")
                
                if response.status_code == 200:
                    profile = response.json()
                    print(f"       👤 Perfil: {profile['data']['nome']}")
                
                # Obter estatísticas
                print("\n   4.2 Obtendo estatísticas do dashboard...")
                response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
                print(f"       ✅ Status: {response.status_code}")
                print(f"       📝 Log esperado: Usuário {user_info['nome']} ({user_info['email']})")
                
                # Testar POST com dados
                print("\n   4.3 Criando objetivo (POST com dados)...")
                objetivo_data = {
                    "titulo": "Meu Primeiro Objetivo",
                    "descricao": "Objetivo criado para testar logging",
                    "meta_numerica": 100,
                    "unidade_medida": "pontos",
                    "data_limite": "2025-12-31",
                    "categoria": "teste"
                }
                
                response = requests.post(f"{BASE_URL}/objetivos", json=objetivo_data, headers=headers)
                print(f"       ✅ Status: {response.status_code}")
                print(f"       📝 Log esperado: Usuário {user_info['nome']} com dados do objetivo")
                
                # 5. Testar token inválido
                print("\n5️⃣ Testando token INVÁLIDO...")
                invalid_headers = {
                    "Authorization": "Bearer token_invalido_123",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(f"{BASE_URL}/user/profile", headers=invalid_headers)
                print(f"   ❌ Status: {response.status_code}")
                print("   📝 Log esperado: Usuário Anônimo (token inválido)")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*80)
    print("📚 RESUMO - COMO O FRONTEND DEVE ENVIAR INFORMAÇÕES:")
    print("="*80)
    print()
    print("1️⃣ REGISTRO/LOGIN:")
    print("   POST /api/v1/auth/register")
    print("   POST /api/v1/auth/login")
    print("   Content-Type: application/json")
    print("   Body: {\"email\": \"...\", \"password\": \"...\", \"nome\": \"...\"}")
    print()
    print("2️⃣ REQUISIÇÕES AUTENTICADAS:")
    print("   Headers obrigatórios:")
    print("   {")
    print("     \"Authorization\": \"Bearer <token>\",")
    print("     \"Content-Type\": \"application/json\"")
    print("   }")
    print()
    print("3️⃣ EXEMPLO COMPLETO EM JAVASCRIPT:")
    print("   ```javascript")
    print("   // Após login/registro, salvar token")
    print("   const token = response.data.access_token;")
    print()
    print("   // Para todas as requisições autenticadas:")
    print("   const headers = {")
    print("     'Authorization': `Bearer ${token}`,")
    print("     'Content-Type': 'application/json'")
    print("   };")
    print()
    print("   // GET")
    print("   fetch('/api/v1/user/profile', { headers });")
    print()
    print("   // POST")
    print("   fetch('/api/v1/objetivos', {")
    print("     method: 'POST',")
    print("     headers,")
    print("     body: JSON.stringify(data)")
    print("   });")
    print("   ```")
    print()
    print("4️⃣ VERIFICAÇÃO NO LOG:")
    print("   ✅ Com token válido: Usuário: ID:123 | Nome:João Silva | Email:joao@example.com")
    print("   ❌ Sem token/inválido: Usuário: Anônimo")

if __name__ == "__main__":
    test_authentication_flow()