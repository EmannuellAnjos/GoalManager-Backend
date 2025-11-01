#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de login com as credenciais corretas descobertas.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.auth import authenticate_user, create_access_token
from app.core.database import get_db
from datetime import datetime

def test_login_correto():
    print("🔐 TESTE COM CREDENCIAIS CORRETAS")
    print("=" * 50)
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        
        # Credenciais corretas descobertas
        email = "teste@goalmanager.com"
        password = "password"
        
        print(f"📧 Email: {email}")
        print(f"🔑 Senha: {password}")
        print()
        
        # Testar autenticação
        print("🧪 Testando autenticação...")
        user = authenticate_user(db, email, password)
        
        if user:
            print("✅ SUCESSO! Usuário autenticado:")
            print(f"👤 ID: {user.id}")
            print(f"👤 Nome: {user.nome}")
            print(f"👤 Email: {user.email}")
            print(f"👤 Ativo: {user.ativo}")
            print()
            
            # Criar token
            token = create_access_token(data={"sub": user.email})
            print(f"🎫 Token: {token[:50]}...")
            print()
            
            print("🎉 CREDENCIAIS FUNCIONANDO PERFEITAMENTE!")
            print()
            print("📋 DADOS PARA USAR NO FRONTEND/POSTMAN:")
            print("=" * 50)
            print("POST http://localhost:8000/api/v1/auth/login")
            print("Content-Type: application/json")
            print("{")
            print(f'  "email": "{email}",')
            print(f'  "password": "{password}"')
            print("}")
            
        else:
            print("❌ FALHA NA AUTENTICAÇÃO")
        
        # Fechar sessão
        db.close()
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕒 Teste executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_login_correto()