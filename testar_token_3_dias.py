#!/usr/bin/env python3
"""
Script para testar se o token JWT agora expira em 3 dias
"""
import requests
import json
from datetime import datetime
import jwt

# URL base da API
BASE_URL = "http://localhost:8000/api/v1"

def testar_token_3_dias():
    """Testa se o token JWT agora está configurado para 3 dias"""
    
    print("🔐 Testando nova configuração de token (3 dias)...")
    
    # 1. Fazer login para obter token
    login_data = {
        "email": "teste@goalmanager.com",
        "password": "password"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(login_response.text)
            return
        
        token_data = login_response.json()
        token = token_data["data"]["access_token"]
        expires_in = token_data["data"]["expires_in"]
        
        print("✅ Login realizado com sucesso!")
        print(f"📊 Token expires_in: {expires_in} segundos")
        
        # Converter para horas e dias
        expires_in_hours = expires_in / 3600
        expires_in_days = expires_in_hours / 24
        
        print(f"📊 Equivale a: {expires_in_hours:.1f} horas")
        print(f"📊 Equivale a: {expires_in_days:.1f} dias")
        
        # 2. Decodificar o token JWT para verificar a data de expiração
        try:
            # Decodificar sem verificar assinatura (apenas para inspecionar)
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            exp_timestamp = decoded_token.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
                current_datetime = datetime.now()
                
                print(f"📅 Token criado em: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📅 Token expira em: {exp_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Calcular diferença
                time_diff = exp_datetime - current_datetime
                days_diff = time_diff.total_seconds() / (24 * 3600)
                
                print(f"⏰ Tempo até expiração: {days_diff:.2f} dias")
                
                # Verificar se está próximo de 3 dias
                if 2.9 <= days_diff <= 3.1:
                    print("✅ Configuração de 3 dias aplicada com sucesso!")
                else:
                    print(f"⚠️  Configuração pode não estar correta. Esperado ~3 dias, obtido {days_diff:.2f} dias")
            
        except Exception as e:
            print(f"⚠️  Não foi possível decodificar o token: {e}")
        
        # 3. Testar uma requisição autenticada
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n🧪 Testando requisição autenticada...")
        test_response = requests.get(f"{BASE_URL}/objetivos", headers=headers)
        
        if test_response.status_code == 200:
            print("✅ Token funcionando perfeitamente!")
        else:
            print(f"❌ Erro na requisição autenticada: {test_response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_token_3_dias()