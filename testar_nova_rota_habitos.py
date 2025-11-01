#!/usr/bin/env python3
"""
Script para testar a nova rota de hábitos por objetivo
"""
import requests
import json

# URL base da API
BASE_URL = "http://localhost:8000/api/v1"

def testar_nova_rota():
    """Testa a nova rota /objetivos/{objetivo_id}/habitos"""
    
    print("🔐 Fazendo login...")
    
    # 1. Fazer login para obter token
    login_data = {
        "email": "teste@goalmanager.com",
        "password": "password"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        print(login_response.text)
        return
    
    token_data = login_response.json()
    token = token_data["data"]["access_token"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("✅ Login realizado com sucesso!")
    
    # 2. Listar objetivos para pegar um ID
    print("\n📋 Listando objetivos...")
    objetivos_response = requests.get(f"{BASE_URL}/objetivos", headers=headers)
    
    if objetivos_response.status_code != 200:
        print(f"❌ Erro ao listar objetivos: {objetivos_response.status_code}")
        print(objetivos_response.text)
        return
    
    objetivos_data = objetivos_response.json()
    objetivos = objetivos_data["data"]
    
    if not objetivos:
        print("⚠️ Nenhum objetivo encontrado. Criando um objetivo de teste...")
        
        # Criar um objetivo de teste
        objetivo_data = {
            "titulo": "Objetivo de Teste - Hábitos",
            "descricao": "Teste da nova rota de hábitos",
            "inicio": "2025-10-29",
            "fim": "2025-11-30",
            "status": "planejado"
        }
        
        create_response = requests.post(f"{BASE_URL}/objetivos", json=objetivo_data, headers=headers)
        
        if create_response.status_code != 201:
            print(f"❌ Erro ao criar objetivo: {create_response.status_code}")
            print(create_response.text)
            return
        
        objetivo_criado = create_response.json()
        objetivo_id = objetivo_criado["data"]["id"]
        print(f"✅ Objetivo criado com ID: {objetivo_id}")
    
    else:
        objetivo_id = objetivos[0]["id"]
        print(f"✅ Usando objetivo existente: {objetivo_id}")
    
    # 3. Testar a nova rota /objetivos/{objetivo_id}/habitos
    print(f"\n🎯 Testando nova rota: /objetivos/{objetivo_id}/habitos")
    
    habitos_response = requests.get(f"{BASE_URL}/objetivos/{objetivo_id}/habitos", headers=headers)
    
    print(f"Status Code: {habitos_response.status_code}")
    
    if habitos_response.status_code == 200:
        print("✅ Nova rota funcionando corretamente!")
        habitos_data = habitos_response.json()
        print(f"📊 Dados retornados: {json.dumps(habitos_data, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erro na nova rota: {habitos_response.status_code}")
        print(habitos_response.text)
        
    # 4. Comparar com a rota antiga para verificar consistência
    print(f"\n🔄 Comparando com rota antiga: /habitos/objetivo/{objetivo_id}")
    
    habitos_old_response = requests.get(f"{BASE_URL}/habitos/objetivo/{objetivo_id}", headers=headers)
    
    print(f"Status Code (rota antiga): {habitos_old_response.status_code}")
    
    if habitos_old_response.status_code == 200:
        print("✅ Rota antiga também funcionando!")
        habitos_old_data = habitos_old_response.json()
        
        # Comparar resultados
        if habitos_response.status_code == 200:
            nova_qtd = len(habitos_data.get("data", []))
            antiga_qtd = len(habitos_old_data.get("data", []))
            
            if nova_qtd == antiga_qtd:
                print(f"✅ Ambas as rotas retornam a mesma quantidade de hábitos: {nova_qtd}")
            else:
                print(f"⚠️ Diferença na quantidade: Nova rota={nova_qtd}, Antiga rota={antiga_qtd}")
    else:
        print(f"❌ Erro na rota antiga: {habitos_old_response.status_code}")

if __name__ == "__main__":
    testar_nova_rota()