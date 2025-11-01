"""
Script para testar especificamente a rota de login
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    print("🧪 TESTANDO ROTA DE LOGIN\n")
    
    # 1. Primeiro testar registro
    print("1️⃣ Testando registro de usuário...")
    register_data = {
        "nome": "Usuário Teste",
        "email": "teste@exemplo.com",
        "password": "senha123456"  # Senha normal
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", 
                               json=register_data,
                               headers={"Content-Type": "application/json"})
        print(f"   Status registro: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Registro bem-sucedido")
        elif response.status_code == 400:
            print("   ⚠️ Usuário já existe (normal)")
        else:
            print(f"   ❌ Erro inesperado: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Servidor não está rodando!")
        print("   💡 Execute: python run.py")
        return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 2. Agora testar login
    print("\n2️⃣ Testando login...")
    login_data = {
        "email": "teste@exemplo.com",
        "password": "senha123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login",
                               json=login_data,
                               headers={"Content-Type": "application/json"})
        
        print(f"   Status login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login bem-sucedido!")
            print(f"   🎟️ Token: {data['data']['access_token'][:50]}...")
            print(f"   👤 Usuário: {data['data']['user']['nome']}")
            
            # 3. Testar token
            print("\n3️⃣ Testando token obtido...")
            token = data['data']['access_token']
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            profile_response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
            print(f"   Status perfil: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("   ✅ Token válido!")
                print(f"   👤 Perfil: {profile_data['data']['nome']} ({profile_data['data']['email']})")
                print("\n🎉 TODOS OS TESTES PASSARAM!")
                
                print("\n📋 EXEMPLO PARA FRONTEND:")
                print("// 1. Login")
                print("const loginData = {")
                print('  "email": "teste@exemplo.com",')
                print('  "password": "senha123456"')
                print("};")
                print("")
                print("const response = await fetch('/api/v1/auth/login', {")
                print("  method: 'POST',")
                print("  headers: { 'Content-Type': 'application/json' },")
                print("  body: JSON.stringify(loginData)")
                print("});")
                print("")
                print("const data = await response.json();")
                print("const token = data.data.access_token;")
                print("")
                print("// 2. Usar token em requisições")
                print("const headers = {")
                print("  'Authorization': `Bearer ${token}`,")
                print("  'Content-Type': 'application/json'")
                print("};")
                
            else:
                print(f"   ❌ Token inválido: {profile_response.text}")
        
        elif response.status_code == 401:
            print("   ❌ Credenciais inválidas")
            print("   💡 Verifique email e senha")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_login()