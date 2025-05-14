# 🚗 Scraper de Fichas Técnicas de Veículos

![Scraper](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0%2B-green)

Projeto de scraping para coleta e atualização de fichas técniccas de veículos a partir
de fontes especializadas. Os dados são armazenados em um banco MongoDB local e futuramente
estarão disponíveis via API.

---

## 🌟 Principais Recursos

- ✔️ Coleta automatizada de dados técnicos de veículos
- ✔️ Suporte a múltiplas fontes de dados
- ✔️ Armazenamento em banco de dados MongoDB
- ✔️ Sistema de logging robusto
- ✔️ Fácil extensão para novas fontes

---

## 📚 Visão Geral

Este projeto extrai dados detalhados de fichas técnicas de veículos de duas fontes principais:

| Fonte | Descrição |
|-------|-----------|
| `fichacompleta` | Primeira fonte de dados |
| `carroweb` | Segunda fonte de dados |
| `full` | Executa ambos scrapers em sequência |

Os dados coletados incluem:

- Montadora
- Modelo
- Versões
- Anos de fabricação
- Especificações técnicas completas

---

## 🏗 Estrutura do Projeto

```text
fichas_tecnicas/
│
├── cli/            # Gerenciamento de argumentos com argparse
├── db/             # Conexão e operações no MongoDB
├── experiments/    # Testes e validações
├── logger/         # Sistema de logging centralizado
├── runners/        # Scripts principais dos scrapers
├── scraper/        # Scrapers específicos por site
├── utils/          # Funções auxiliares
├── main.py         # Ponto de entrada
└── requirements.txt
```

---

## 🚀 Como Executar

#### Pré-requisitos

- Python 3.8+
- MongoDB 5.0+
- Dependências do projeto

#### Instalação

```bash
  pip install -r requirements.txt
```

#### Modos de Execução

```bash
    # Executar um scraper específico
    python main.py --modo fichacompleta
    python main.py --modo carroweb
    
    # Executar todos os scrapers
    python main.py --modo full
```

---

## 🗃 Banco de Dados

**Tecnologia**: MongoDB

**Conexão padrão**: `mongodb://localhost:27017`

**Collections**: `vehicles` e `vehicle_specs`

### 📌 Estrutura dos Documentos

#### Collection `vehicles` (Dados básicos dos veículos)

```json
{
  "_id": ObjectId("682356da0e9e1b463a8fd32e"),
  "timestamp": "13-05-2025 11:27:38",
  "reference": "fichacompleta",
  "automaker": "chevrolet",
  "model": "onix",
  "year": "2025",
  "version": "ltz · 1.0 · turbo · at · flex"
}
```

Collection `vehicle_specs` (Especificações completas)

```json
{
  "_id": ObjectId("6824a244ce2c84160865e159"),
  "automaker": "chevrolet",
  "model": "onix",
  "year": "2025",
  "version": "ltz · 1.0 · turbo · at · flex",
  "information": {
    "motor": "1.0 Turbo Flex",
    "potencia": "116 cv",
    "transmissao": "Automática 6 velocidades",
    // Demais especificações técnicas
  },
  "equipment": [
    "Ar-condicionado digital",
    "Multimídia 8\"",
    "Sensor de estacionamento",
    // Lista completa de equipamentos
  ]
}
```

### 🔗 Relacionamento entre Collections

- Os documentos são relacionados pelos campos:
  - `automaker`
  - `model`
  - `year`
  - `version`

### ⚠️ Observações

- Quando não houver informações de equipamentos, o campo será:

```json
"equipment": "Equipamentos não especificados para esse modelo"
```

- O campo `reference` indica a fonte dos dados (`fichacompleta` ou `carroweb`)
- O `timestamp` registra quando o dado foi coletado

---

## 🛣 Roadmap

- Desenvolvimento de API REST para consulta
- Adição de novas fontes de dados
- Implementação de agendamento automático
- Melhoria no sistema de logs
- Criação de testes automatizados
- Dashboard de monitoramento

---

## 🤝 Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch com sua feature(`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças(`git commit -m "Adicione uma mensagem explicando as mudanças que foram feitas"`)
4. Push para a branch(`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

