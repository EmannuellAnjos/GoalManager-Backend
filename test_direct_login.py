#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do processo de login testando diretamente as funções (sem servidor HTTP).
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auth import authenticate_user, create_access_token
from app.core.database import get_db
from datetime import datetime

def test_direct_login():
    print("🔐 TESTE DIRETO DO PROCESSO DE LOGIN")
    print("=" * 60)
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        
        # Dados de teste
        email = "teste@exemplo.com"
        password = "senha123456"
        
        print(f"📧 Testando login para: {email}")
        print(f"🔑 Senha: {password}")
        print()
        
        # Testar autenticação
        print("1️⃣ Tentando autenticar usuário...")
        user = authenticate_user(db, email, password)
        
        if user:
            print("✅ USUÁRIO AUTENTICADO COM SUCESSO!")
            print(f"👤 ID: {user.id}")
            print(f"👤 Nome: {user.nome}")
            print(f"👤 Email: {user.email}")
            print(f"👤 Ativo: {user.ativo}")
            print()
            
            # Criar token de acesso
            print("2️⃣ Gerando token de acesso...")
            access_token = create_access_token(data={"sub": user.email})
            print(f"🎫 Token gerado: {access_token[:50]}...")
            print()
            
            print("🎉 PROCESSO DE LOGIN FUNCIONANDO PERFEITAMENTE!")
            print("=" * 60)
            print("📋 DADOS PARA USAR NO POSTMAN/INSOMNIA:")
            print("POST http://localhost:8000/api/v1/auth/login")
            print("Content-Type: application/json")
            print("{")
            print(f'  "email": "{email}",')
            print(f'  "password": "{password}"')
            print("}")
            print("=" * 60)
            
        else:
            print("❌ FALHA NA AUTENTICAÇÃO")
            print("🔍 Possíveis causas:")
            print("  - Email não encontrado")
            print("  - Senha incorreta")
            print("  - Usuário inativo")
            
        # Fechar sessão
        db.close()
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕒 Teste executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_direct_login()