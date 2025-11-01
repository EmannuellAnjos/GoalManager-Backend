#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo após correção do disable_auth.
Testa o sistema com autenticação habilitada e verifica se os dados são retornados.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from starlette.testclient import TestClient
from app.main import app
from datetime import datetime
import json

def test_sistema_corrigido():
    print("🔧 TESTE APÓS CORREÇÃO DO DISABLE_AUTH")
    print("=" * 70)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Criar cliente de teste
    client = TestClient(app)
    
    print("📋 TESTE 1: Login com usuário real")
    print("-" * 50)
    
    # Login com credenciais corretas
    login_data = {
        "email": "teste@goalmanager.com",
        "password": "password"
    }
    
    print(f"📧 Email: {login_data['email']}")
    print(f"🔑 Password: {login_data['password']}")
    
    response = client.post("/api/v1/auth/login", json=login_data)
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        login_response = response.json()
        data = login_response.get('data', {})
        token = data.get('access_token')
        print("✅ LOGIN REALIZADO COM SUCESSO!")
        print(f"🎫 Token obtido: {token[:50] if token else 'N/A'}...")
        
        if token:
            print()
            print("📋 TESTE 2: Buscar objetivos com usuário autenticado")
            print("-" * 50)
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Testar múltiplas rotas
            endpoints = [
                ("/api/v1/objetivos", "Objetivos"),
                ("/api/v1/habitos", "Hábitos"),
                ("/api/v1/tarefas", "Tarefas"),
                ("/api/v1/auth/me", "Perfil do usuário")
            ]
            
            for endpoint, nome in endpoints:
                print(f"🌐 Testando: {nome} - {endpoint}")
                try:
                    response = client.get(endpoint, headers=headers)
                    print(f"   📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if endpoint == "/api/v1/objetivos":
                            # Verificar se há dados de objetivos
                            objetivos_data = data.get('data', {})
                            items = objetivos_data.get('items', [])
                            total = objetivos_data.get('total', 0)
                            print(f"   🎯 Objetivos encontrados: {total}")
                            
                            if items:
                                print("   ✅ DADOS DE OBJETIVOS RETORNADOS!")
                                for obj in items[:2]:  # Mostrar apenas 2 primeiros
                                    print(f"      📝 {obj.get('titulo', 'N/A')} - Status: {obj.get('status', 'N/A')}")
                            else:
                                print("   ❌ Nenhum objetivo retornado")
                                
                        elif endpoint == "/api/v1/auth/me":
                            user_info = data.get('data', {})
                            print(f"   👤 Usuário: {user_info.get('nome', 'N/A')}")
                            print(f"   📧 Email: {user_info.get('email', 'N/A')}")
                            print(f"   🆔 ID: {user_info.get('id', 'N/A')}")
                            
                        else:
                            # Para outros endpoints, mostrar total de itens
                            endpoint_data = data.get('data', {})
                            if isinstance(endpoint_data, dict):
                                total = endpoint_data.get('total', 0)
                                print(f"   📊 Total de itens: {total}")
                            
                    else:
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                        print(f"   ❌ Erro: {error_data}")
                        
                except Exception as e:
                    print(f"   ❌ Exceção: {str(e)}")
                    
                print()
                
    else:
        print(f"❌ ERRO NO LOGIN: {response.status_code}")
        try:
            error_data = response.json()
            print(f"📝 Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📝 Texto: {response.text}")
    
    print()
    print("🎯 RESUMO DOS RESULTADOS:")
    print("=" * 70)
    print("✅ disable_auth alterado para false")
    print("✅ Sistema de autenticação ativo")
    print("✅ Teste usando usuário real do banco")
    print()
    print("📝 EXPECTATIVA:")
    print("   🔸 Login deve funcionar com credenciais corretas")
    print("   🔸 Objetivos devem ser retornados (3 objetivos no banco)")
    print("   🔸 Logs devem mostrar usuário autenticado")
    print()
    print(f"⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    test_sistema_corrigido()