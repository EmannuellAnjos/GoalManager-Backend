# 🔐 GUIA COMPLETO: Como o Frontend Deve Enviar Informações do Usuário

## ✅ DIAGNÓSTICO: Sistema Funcionando Corretamente!

O sistema de logging está **funcionando perfeitamente**. O usuário aparece como "Anônimo" porque **o frontend não está enviando o token JWT** nas requisições.

## 📋 Como Funciona a Autenticação

### 1. **Fluxo de Autenticação**
```
🔄 FRONTEND                    🖥️ BACKEND
1. Login/Registro       ──►    Gera JWT Token
2. Salva token         ◄──     Retorna token
3. Envia token em      ──►     Valida token
   todas requisições           Identifica usuário
```

### 2. **O que o Backend Espera**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🚀 Implementação no Frontend

### **JavaScript/TypeScript**

#### **1. Armazenar Token Após Login**
```javascript
// Após login bem-sucedido
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'usuario@example.com',
    password: 'senha123'
  })
});

const data = await loginResponse.json();
const token = data.data.access_token;

// Salvar token (escolha uma opção)
localStorage.setItem('auth_token', token);        // Opção 1
sessionStorage.setItem('auth_token', token);      // Opção 2
// ou usar Context/Redux/Zustand                  // Opção 3
```

#### **2. Enviar Token em Todas as Requisições**
```javascript
// Função para fazer requisições autenticadas
async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('auth_token');
  
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
}

// Exemplos de uso:
// GET
const profile = await authenticatedFetch('/api/v1/user/profile');

// POST
const newGoal = await authenticatedFetch('/api/v1/objetivos', {
  method: 'POST',
  body: JSON.stringify({
    titulo: 'Meu Objetivo',
    descricao: 'Descrição do objetivo'
  })
});
```

#### **3. Interceptador Axios (se usar Axios)**
```javascript
import axios from 'axios';

// Configurar interceptador
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Agora todas as requisições incluem o token automaticamente
const response = await axios.get('/api/v1/user/profile');
```

### **React**

#### **1. Context de Autenticação**
```jsx
// AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    const newToken = data.data.access_token;
    
    setToken(newToken);
    setUser(data.data.user);
    localStorage.setItem('auth_token', newToken);
  };

  const authenticatedFetch = async (url, options = {}) => {
    return fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
  };

  return (
    <AuthContext.Provider value={{ token, user, login, authenticatedFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

#### **2. Hook Personalizado**
```jsx
// useAuthenticatedFetch.js
import { useAuth } from './AuthContext';

export function useAuthenticatedFetch() {
  const { token } = useAuth();

  return async (url, options = {}) => {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  };
}

// Uso nos componentes
function ProfileComponent() {
  const authenticatedFetch = useAuthenticatedFetch();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const loadProfile = async () => {
      const data = await authenticatedFetch('/api/v1/user/profile');
      setProfile(data.data);
    };
    loadProfile();
  }, []);

  return <div>Olá, {profile?.nome}!</div>;
}
```

### **Vue.js**

#### **1. Plugin de Autenticação**
```javascript
// auth.js
export default {
  install(app) {
    const token = ref(localStorage.getItem('auth_token'));
    
    const authenticatedFetch = async (url, options = {}) => {
      return fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
    };

    app.config.globalProperties.$auth = {
      token,
      authenticatedFetch,
      login: async (email, password) => {
        // Implementar login
      }
    };
  }
};
```

## 🧪 Testando a Implementação

### **1. Teste Manual com cURL**
```bash
# 1. Fazer login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"senha123"}'

# 2. Copiar o token da resposta
# 3. Usar em requisições autenticadas
curl -X GET http://localhost:8000/api/v1/user/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### **2. Teste com Postman**
1. **POST** `/api/v1/auth/login` com email e senha
2. Copiar `access_token` da resposta
3. Nas próximas requisições, adicionar header:
   - **Key:** `Authorization`
   - **Value:** `Bearer SEU_TOKEN_AQUI`

### **3. Verificação nos Logs**
Quando implementado corretamente, você verá:
```
🌐 REQUISIÇÃO RECEBIDA | Método: GET | URL: /api/v1/user/profile | 👤 Usuário: ID:123 | Nome:João Silva | Email:joao@example.com | Ativo:True
```

## ❌ Problemas Comuns

### **1. Token não é enviado**
**Sintomas:** Usuário sempre "Anônimo"
**Solução:** Verificar se o header Authorization está sendo enviado

### **2. Token malformado**
**Sintomas:** Erro 401 ou usuário "Anônimo"
**Verificar:** 
- Formato: `Bearer TOKEN` (com espaço)
- Token não expirado
- Token válido

### **3. Token expira**
**Sintomas:** Funcionava antes, agora não funciona
**Solução:** Implementar refresh automático ou relogin

## 🔧 Debugging

### **1. Ver Headers no DevTools**
1. F12 → Network
2. Fazer requisição
3. Verificar se header `Authorization` está presente

### **2. Logs do Backend (DEBUG habilitado)**
```
DEBUG:app.middleware.logging:🔍 Debug: Token extraído: eyJhbGciOiJIUzI1NiI...
DEBUG:app.middleware.logging:🔍 Debug: Usuário encontrado no BD: João Silva (joao@example.com)
```

### **3. Testar Token Manualmente**
```javascript
// No console do navegador
const token = localStorage.getItem('auth_token');
console.log('Token:', token);

// Testar requisição
fetch('/api/v1/user/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

## 🎯 Resumo - Lista de Verificação

- [ ] **Frontend faz login e recebe token**
- [ ] **Token é armazenado (localStorage/sessionStorage/estado)**
- [ ] **Header Authorization é enviado em todas requisições autenticadas**
- [ ] **Formato correto: `Bearer TOKEN`**
- [ ] **Token não expirado**
- [ ] **Logs mostram usuário identificado (não anônimo)**

## 💡 Dica Final

O sistema de logging está funcionando perfeitamente! Se você ainda vê usuários anônimos, é porque **o frontend não está enviando o token JWT corretamente**. Siga este guia para implementar a autenticação no frontend.

---

**🎉 Quando implementado corretamente, você verá logs detalhados como:**
```
🌐 REQUISIÇÃO RECEBIDA | Método: POST | URL: /api/v1/objetivos | 👤 Usuário: ID:abc123 | Nome:Maria Silva | Email:maria@example.com | Ativo:True | Body: JSON: {"titulo":"Exercitar-se","meta_numerica":30}

✅ RESPOSTA ENVIADA | Status: 201 | Tempo: 0.156s | 👤 Usuário: ID:abc123 | Nome:Maria Silva | Email:maria@example.com | Ativo:True
```