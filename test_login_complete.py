#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema de login para verificar se tudo está funcionando.
"""
import requests
import json
from datetime import datetime

def test_login_complete():
    print("🧪 TESTE COMPLETO DO SISTEMA DE LOGIN")
    print("=" * 60)
    
    # URL do servidor (assumindo que está rodando localmente)
    base_url = "http://localhost:8000"
    
    # Dados de teste
    test_data = {
        "email": "teste@exemplo.com",
        "password": "senha123456"
    }
    
    try:
        print(f"📡 Fazendo requisição POST para {base_url}/api/v1/auth/login")
        print(f"📝 Dados: {json.dumps(test_data, indent=2)}")
        print()
        
        # Fazer requisição de login
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            login_data = response.json()
            print("✅ LOGIN REALIZADO COM SUCESSO!")
            print(f"🎯 Resposta: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
            
            # Teste de rota autenticada
            if 'access_token' in login_data:
                token = login_data['access_token']
                print("\n🔐 TESTANDO ROTA AUTENTICADA...")
                
                auth_response = requests.get(
                    f"{base_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                
                print(f"📊 Status /me: {auth_response.status_code}")
                if auth_response.status_code == 200:
                    user_data = auth_response.json()
                    print(f"👤 Dados do usuário: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
                    print("✅ SISTEMA DE AUTENTICAÇÃO FUNCIONANDO PERFEITAMENTE!")
                else:
                    print(f"❌ Erro na rota /me: {auth_response.text}")
        else:
            print(f"❌ ERRO NO LOGIN: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
        print("🚀 Execute: python run.py")
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout na requisição")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🕒 Teste executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_login_complete()