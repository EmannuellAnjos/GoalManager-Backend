# 🎨 Prompt para Ajustar Frontend - Tarefas Sem Objetivo

## 📋 Contexto

O backend foi atualizado para **remover a ligação de tarefas com objetivos**. Agora, **tarefas são ligadas exclusivamente a hábitos**.

---

## 🎯 Objetivo

Ajustar o frontend para refletir as mudanças do backend:
- ❌ Remover campo "Objetivo" do formulário de tarefas
- ✅ Tornar campo "Hábito" **obrigatório**
- ✅ Atualizar tipos TypeScript
- ✅ Atualizar validações
- ✅ Atualizar componentes de listagem

---

## 🔧 Alterações Necessárias

### 1. **Tipos TypeScript** (interfaces/types)

#### Antes ❌
```typescript
interface Tarefa {
  id: string;
  usuarioId: string;
  objetivoId?: string;      // Opcional
  habitoId?: string;        // Opcional
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status: StatusTarefa;
  estimativaHoras?: number;
  horasGastas: number;
  prazo?: string;
  progresso: number;
  posicao?: number;
  tags?: string[];
  anexos?: string[];
  createdAt: string;
  updatedAt: string;
}

interface TarefaCreate {
  objetivoId?: string;      // Opcional
  habitoId?: string;        // Opcional
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status?: StatusTarefa;
  estimativaHoras?: number;
  prazo?: string;
  tags?: string[];
  anexos?: string[];
}
```

#### Depois ✅
```typescript
interface Tarefa {
  id: string;
  usuarioId: string;
  // objetivoId REMOVIDO ❌
  habitoId: string;         // OBRIGATÓRIO ✅
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status: StatusTarefa;
  estimativaHoras?: number;
  horasGastas: number;
  prazo?: string;
  progresso: number;
  posicao?: number;
  tags?: string[];
  anexos?: string[];
  createdAt: string;
  updatedAt: string;
}

interface TarefaCreate {
  // objetivoId REMOVIDO ❌
  habitoId: string;         // OBRIGATÓRIO ✅
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status?: StatusTarefa;
  estimativaHoras?: number;
  prazo?: string;
  tags?: string[];
  anexos?: string[];
}

interface TarefaUpdate {
  titulo?: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status?: StatusTarefa;
  estimatimaHoras?: number;
  horasGastas?: number;
  prazo?: string;
  progresso?: number;
  posicao?: number;
  tags?: string[];
  anexos?: string[];
  // habitoId NÃO pode ser alterado
}
```

---

### 2. **Formulário de Criar/Editar Tarefa**

#### Remover Campo Objetivo ❌

**Antes:**
```tsx
<FormControl>
  <FormLabel>Objetivo</FormLabel>
  <Select
    name="objetivoId"
    value={formData.objetivoId || ''}
    onChange={handleChange}
  >
    <option value="">Nenhum</option>
    {objetivos.map(obj => (
      <option key={obj.id} value={obj.id}>{obj.titulo}</option>
    ))}
  </Select>
</FormControl>

<FormControl>
  <FormLabel>Hábito</FormLabel>
  <Select
    name="habitoId"
    value={formData.habitoId || ''}
    onChange={handleChange}
  >
    <option value="">Nenhum</option>
    {habitos.map(hab => (
      <option key={hab.id} value={hab.id}>{hab.titulo}</option>
    ))}
  </Select>
</FormControl>
```

**Depois:**
```tsx
{/* Campo Objetivo REMOVIDO */}

<FormControl isRequired>  {/* ✅ isRequired adicionado */}
  <FormLabel>Hábito *</FormLabel>
  <Select
    name="habitoId"
    value={formData.habitoId}
    onChange={handleChange}
    placeholder="Selecione um hábito"
    isRequired  {/* ✅ Obrigatório */}
  >
    {habitos.map(hab => (
      <option key={hab.id} value={hab.id}>{hab.titulo}</option>
    ))}
  </Select>
  <FormHelperText>Selecione o hábito ao qual esta tarefa pertence</FormHelperText>
</FormControl>
```

---

### 3. **Validação do Formulário**

#### Antes ❌
```typescript
const validarFormulario = (data: TarefaCreate): string[] => {
  const erros: string[] = [];
  
  if (!data.titulo?.trim()) {
    erros.push('Título é obrigatório');
  }
  
  // habitoId era opcional
  
  return erros;
};
```

#### Depois ✅
```typescript
const validarFormulario = (data: TarefaCreate): string[] => {
  const erros: string[] = [];
  
  if (!data.titulo?.trim()) {
    erros.push('Título é obrigatório');
  }
  
  // ✅ Validação de habitoId OBRIGATÓRIA
  if (!data.habitoId) {
    erros.push('Hábito é obrigatório');
  }
  
  return erros;
};
```

---

### 4. **Estado Inicial do Formulário**

#### Antes ❌
```typescript
const [formData, setFormData] = useState<TarefaCreate>({
  titulo: '',
  descricao: '',
  objetivoId: undefined,  // Opcional
  habitoId: undefined,    // Opcional
  status: 'backlog',
});
```

#### Depois ✅
```typescript
// Opção 1: Receber habitoId como prop (recomendado)
interface TarefaFormProps {
  habitoId: string;  // ✅ Obrigatório via prop
  onSave: (tarefa: TarefaCreate) => void;
  onCancel: () => void;
}

const TarefaForm: React.FC<TarefaFormProps> = ({ habitoId, onSave, onCancel }) => {
  const [formData, setFormData] = useState<TarefaCreate>({
    titulo: '',
    descricao: '',
    habitoId: habitoId,  // ✅ Já vem preenchido
    status: 'backlog',
  });
  
  // ...
};

// Opção 2: Selecionar hábito no formulário
const [formData, setFormData] = useState<TarefaCreate>({
  titulo: '',
  descricao: '',
  habitoId: '',  // ✅ String vazia, mas obrigatório preencher
  status: 'backlog',
});
```

---

### 5. **Componente de Lista de Tarefas**

#### Remover Referências a Objetivo

**Antes:**
```tsx
<Card>
  <CardHeader>
    <Heading size="sm">{tarefa.titulo}</Heading>
    {tarefa.objetivoId && (
      <Badge colorScheme="blue">
        Objetivo: {getObjetivoNome(tarefa.objetivoId)}
      </Badge>
    )}
    {tarefa.habitoId && (
      <Badge colorScheme="green">
        Hábito: {getHabitoNome(tarefa.habitoId)}
      </Badge>
    )}
  </CardHeader>
  {/* ... */}
</Card>
```

**Depois:**
```tsx
<Card>
  <CardHeader>
    <Heading size="sm">{tarefa.titulo}</Heading>
    {/* Badge de objetivo REMOVIDO */}
    <Badge colorScheme="green">
      Hábito: {getHabitoNome(tarefa.habitoId)}
    </Badge>
  </CardHeader>
  {/* ... */}
</Card>
```

---

### 6. **Filtros de Listagem**

#### Antes ❌
```tsx
<Stack direction="row" spacing={4}>
  <Select
    placeholder="Filtrar por Objetivo"
    value={filtros.objetivoId}
    onChange={(e) => setFiltros({...filtros, objetivoId: e.target.value})}
  >
    {objetivos.map(obj => (
      <option key={obj.id} value={obj.id}>{obj.titulo}</option>
    ))}
  </Select>
  
  <Select
    placeholder="Filtrar por Hábito"
    value={filtros.habitoId}
    onChange={(e) => setFiltros({...filtros, habitoId: e.target.value})}
  >
    {habitos.map(hab => (
      <option key={hab.id} value={hab.id}>{hab.titulo}</option>
    ))}
  </Select>
</Stack>
```

**Depois:**
```tsx
<Stack direction="row" spacing={4}>
  {/* Select de Objetivo REMOVIDO */}
  
  <Select
    placeholder="Filtrar por Hábito"
    value={filtros.habitoId}
    onChange={(e) => setFiltros({...filtros, habitoId: e.target.value})}
  >
    <option value="">Todos os hábitos</option>
    {habitos.map(hab => (
      <option key={hab.id} value={hab.id}>{hab.titulo}</option>
    ))}
  </Select>
</Stack>
```

---

### 7. **Modal/Drawer de Nova Tarefa**

#### Contexto Recomendado

**Melhor UX: Abrir modal a partir de um hábito**

```tsx
// No componente de Hábito
<Button onClick={() => setIsNovoTarefaOpen(true)}>
  + Nova Tarefa
</Button>

<Modal isOpen={isNovoTarefaOpen} onClose={() => setIsNovoTarefaOpen(false)}>
  <ModalOverlay />
  <ModalContent>
    <ModalHeader>Nova Tarefa para {habito.titulo}</ModalHeader>
    <ModalBody>
      <TarefaForm
        habitoId={habito.id}  {/* ✅ Passa o ID do hábito */}
        onSave={handleSave}
        onCancel={() => setIsNovoTarefaOpen(false)}
      />
    </ModalBody>
  </ModalContent>
</Modal>
```

---

### 8. **Chamadas à API**

#### Criar Tarefa

```typescript
const criarTarefa = async (data: TarefaCreate): Promise<Tarefa> => {
  // ✅ habitoId agora é obrigatório no payload
  const response = await fetch('/api/v1/tarefas', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      habitoId: data.habitoId,  // ✅ Obrigatório
      titulo: data.titulo,
      descricao: data.descricao,
      prioridade: data.prioridade,
      status: data.status || 'backlog',
      estimativaHoras: data.estimativaHoras,
      prazo: data.prazo,
      tags: data.tags,
      anexos: data.anexos,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Erro ao criar tarefa');
  }
  
  const result = await response.json();
  return result.data;
};
```

#### Listar Tarefas por Hábito

```typescript
const listarTarefasPorHabito = async (habitoId: string): Promise<Tarefa[]> => {
  const response = await fetch(`/api/v1/tarefas/habito/${habitoId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Erro ao listar tarefas');
  }
  
  const result = await response.json();
  return result.data;
};
```

---

### 9. **Tratamento de Erros**

```typescript
const handleSubmit = async (data: TarefaCreate) => {
  try {
    // Validar antes de enviar
    if (!data.habitoId) {
      toast({
        title: 'Erro de validação',
        description: 'Selecione um hábito para a tarefa',
        status: 'error',
        duration: 5000,
      });
      return;
    }
    
    await criarTarefa(data);
    
    toast({
      title: 'Sucesso!',
      description: 'Tarefa criada com sucesso',
      status: 'success',
      duration: 3000,
    });
    
    onClose();
  } catch (error) {
    toast({
      title: 'Erro',
      description: error.message || 'Erro ao criar tarefa',
      status: 'error',
      duration: 5000,
    });
  }
};
```

---

## 🎨 Componente Completo de Exemplo

```tsx
import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  FormHelperText,
  Input,
  Textarea,
  Select,
  Button,
  useToast,
  VStack,
} from '@chakra-ui/react';

interface TarefaFormProps {
  habitoId: string;  // ✅ Obrigatório
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface TarefaCreate {
  habitoId: string;
  titulo: string;
  descricao?: string;
  prioridade?: 'baixa' | 'media' | 'alta';
  status?: string;
  estimativaHoras?: number;
  prazo?: string;
}

export const NovaTarefaModal: React.FC<TarefaFormProps> = ({
  habitoId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<TarefaCreate>({
    habitoId: habitoId,  // ✅ Já vem preenchido
    titulo: '',
    descricao: '',
    prioridade: 'media',
    status: 'backlog',
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validação
    if (!formData.titulo.trim()) {
      toast({
        title: 'Erro',
        description: 'Título é obrigatório',
        status: 'error',
      });
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/tarefas', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Erro ao criar tarefa');
      }
      
      toast({
        title: 'Sucesso!',
        description: 'Tarefa criada com sucesso',
        status: 'success',
      });
      
      onSuccess?.();
      onClose();
      
      // Resetar form
      setFormData({
        habitoId,
        titulo: '',
        descricao: '',
        prioridade: 'media',
        status: 'backlog',
      });
      
    } catch (error) {
      toast({
        title: 'Erro',
        description: error instanceof Error ? error.message : 'Erro desconhecido',
        status: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>Nova Tarefa</ModalHeader>
          
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Título *</FormLabel>
                <Input
                  name="titulo"
                  value={formData.titulo}
                  onChange={handleChange}
                  placeholder="Ex: Completar curso de TypeScript"
                  isRequired
                />
              </FormControl>

              <FormControl>
                <FormLabel>Descrição</FormLabel>
                <Textarea
                  name="descricao"
                  value={formData.descricao}
                  onChange={handleChange}
                  placeholder="Descreva a tarefa..."
                  rows={3}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Prioridade</FormLabel>
                <Select
                  name="prioridade"
                  value={formData.prioridade}
                  onChange={handleChange}
                >
                  <option value="baixa">Baixa</option>
                  <option value="media">Média</option>
                  <option value="alta">Alta</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Status</FormLabel>
                <Select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="backlog">Backlog</option>
                  <option value="a_fazer">A Fazer</option>
                  <option value="fazendo">Fazendo</option>
                  <option value="bloqueada">Bloqueada</option>
                  <option value="concluida">Concluída</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Estimativa (horas)</FormLabel>
                <Input
                  name="estimativaHoras"
                  type="number"
                  step="0.5"
                  min="0"
                  value={formData.estimativaHoras || ''}
                  onChange={handleChange}
                  placeholder="Ex: 2.5"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Prazo</FormLabel>
                <Input
                  name="prazo"
                  type="date"
                  value={formData.prazo || ''}
                  onChange={handleChange}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter gap={3}>
            <Button onClick={onClose} isDisabled={loading}>
              Cancelar
            </Button>
            <Button
              type="submit"
              colorScheme="blue"
              isLoading={loading}
            >
              Criar Tarefa
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};
```

---

## ✅ Checklist de Implementação

### Tipos e Interfaces
- [ ] Atualizar interface `Tarefa` (remover `objetivoId?`, `habitoId` obrigatório)
- [ ] Atualizar interface `TarefaCreate` (remover `objetivoId?`, `habitoId` obrigatório)
- [ ] Atualizar interface `TarefaUpdate` (sem `habitoId`)

### Formulários
- [ ] Remover campo "Objetivo" do formulário
- [ ] Tornar campo "Hábito" obrigatório (isRequired)
- [ ] Adicionar validação de `habitoId` obrigatório
- [ ] Adicionar asterisco (*) no label do Hábito
- [ ] Atualizar estado inicial do formulário

### Componentes de Listagem
- [ ] Remover badges/tags de objetivo
- [ ] Remover filtro por objetivo
- [ ] Ajustar layout sem o campo objetivo

### API e Serviços
- [ ] Atualizar chamadas de criação (garantir `habitoId`)
- [ ] Atualizar chamadas de atualização (sem `objetivoId`)
- [ ] Atualizar tratamento de erros para validação de `habitoId`

### UX e Mensagens
- [ ] Atualizar mensagens de validação
- [ ] Atualizar tooltips/helpers
- [ ] Testar fluxo completo (criar, editar, listar)

### Testes
- [ ] Testar criação de tarefa sem hábito (deve falhar)
- [ ] Testar criação de tarefa com hábito (deve funcionar)
- [ ] Testar edição de tarefa
- [ ] Testar listagem por hábito
- [ ] Testar visualização Kanban

---

## 🎯 Resumo das Mudanças

| Item | Ação | Prioridade |
|------|------|-----------|
| Campo Objetivo | ❌ Remover | 🔴 Alta |
| Campo Hábito | ✅ Tornar obrigatório | 🔴 Alta |
| Validação habitoId | ✅ Adicionar | 🔴 Alta |
| Tipos TypeScript | ✅ Atualizar | 🔴 Alta |
| Filtros | ❌ Remover filtro por objetivo | 🟡 Média |
| Badges/Tags | ❌ Remover referências a objetivo | 🟡 Média |
| UX | ✅ Melhorar mensagens | 🟢 Baixa |

---

## 📱 Exemplo de Fluxo Atualizado

1. **Usuário está vendo um Hábito**
2. **Clica em "Nova Tarefa"** no card do hábito
3. **Modal abre** com `habitoId` já preenchido (não visível/editável)
4. **Usuário preenche** apenas: título, descrição, prioridade, etc.
5. **Submete** → Backend recebe `habitoId` obrigatório
6. **Sucesso** → Tarefa criada e vinculada ao hábito

---

## 🆘 Suporte

Se precisar de ajuda com alguma parte específica:
- Consulte `EXEMPLOS_API_TAREFAS.md` para ver exemplos de API
- Use o TypeScript para validar em tempo de compilação
- Teste cada alteração incrementalmente

---

**Última Atualização:** 2025-11-01  
**Versão:** 1.0 (Pós-migração backend)

