# 🚗 Scraper de Fichas Técnicas de Veículos

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-5.0%2B-4EA94B?style=for-the-badge&logo=mongodb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi)

Este projeto robusto e escalável é um scraper de dados técnicos de veículos, projeto para coletar,
processar e armazenar informações detalhadas de diversas fontes online. Além da coleta de dados, o
projeto inclui uma API RESTfull para acesso programático aos dados e um sistema de gerenciamento de
usuários e logs.

---

## 🌟 Funcionalidades Principais

- ✔️ **Coleta Automatizada de Dados**: Extração de fichas técnicas de veículos de múltiplas fontes especializadas.
- ✔️ **Múltiplas Fontes de Dados**: Suporte para diversos sites que tem fichas técnicas de veiculos, com a opção
de rodar todos os scrapers ("full")
- ✔️ **Execução por Fases**: Capacidade de executar o scraping em fases específicas (coleta inicial, ficha técnica,
ou tudo)
- ✔️ **Armazenamento Persistente**: Dados armazenados de forma eficiente em um banco de dados MongoDB, com coleções
dedicadas para veículos, especificações, logs, usuários e logs de requisição.
- ✔️ **API RESTfull**: Interface programática para consultar os dados coletados, permitindo integração com
outras aplicações.
- ✔️ **Sistema de Logging Robusto**: Monitoramento detalhado das operações de scraping e da API.
- ✔️ **Estrutura Modular**: Código bem organizado e fácil de estender para novas fontes de dados ou funcionalidades.

---

## 🚀 Fontes de Dados

O projeto extrai dados detalhados de fichas técnicas de veículos das seguintes fontes:

| Fonte | Descrição                                        |
|-------|--------------------------------------------------|
| `fichacompleta` | Fonte de dados, com grande variedades de versões |
| `full` | Executa todos os scrapers em sequência           |

Os dados coletados incluem:

- Montadora
- Modelo
- Versões
- Anos de fabricação
- Especificações técnicas completas (motor, potência, transmissão, etc.)
- Lista de equipamentos (quando disponível)

---

## 📂 Estrutura do Projeto

```text
fichas_tecnicas/
│
├── api/            # Módulo da API RESTful (FastAPI)
│   ├── middleware/ # Middlewares da API (ex: autenticação)
│   ├── routes/     # Definição das rotas da API
│   └── schemas/    # Modelos de dados (Pydantic) para a API
├── cli/            # Gerenciamento de argumentos de linha de comando (argparse)
├── db/             # Conexão e operações com o MongoDB
├── experiments/    # Testes e validações experimentais
├── logger/         # Sistema de logging centralizado
├── runners/        # Scripts principais para execução dos scrapers
├── scrapers/       # Scrapers específicos por site
├── tests/          # Testes automatizados
├── utils/          # Funções auxiliares e utilitários
├── main.py         # Ponto de entrada principal para execução dos scrapers
└── requirements.txt # Dependências do projeto
```

---

## 🛠️ Tecnologias Utilizadas

*   **Python**: Linguagem de programação principal (versão 3.8+).
*   **MongoDB**: Banco de dados NoSQL para armazenamento de dados (versão 5.0+).
*   **FastAPI**: Framework web para construção da API RESTful.
*   **Motor**: Driver assíncrono para MongoDB.
*   **Argparse**: Para gerenciamento de argumentos de linha de comando.

---

## ⚙️ Configuração e Instalação

1.  **Pré-requisitos**:
    *   Python 3.8+ instalado.
    *   MongoDB 5.0+ instalado e rodando localmente (ou acessível via URI).

2.  **Clonar o Repositório**:
    ```bash
    git clone https://github.com/AndreNogueir4/Scraping_Vehicle_Technical_File.git
    cd Scraping_Vehicle_Technical_File
    ```

3.  **Instalar Dependências**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Como Usar

#### Executando os Scrapers

O script 'main.py' é o ponto de entrada para executar os scrapers. Você pode especificar qual scraper rodar
e a fase de coleta.

*   **Executar um scraper específico**:
    ```bash
    python main.py <site_name> [--phase <phase_number>]
    ```
    Onde `<site_name>` pode ser `fichacompleta`, `carrosweb` ou `icarros`.
    Opcionalmente, `--phase` pode ser:
    *   `1`: Coleta apenas os dados iniciais dos veículos (montadora, modelo, ano, versão).
    *   `2`: Coleta as fichas técnicas detalhadas para veículos já identificados.
    *   `3` (padrão): Executa o processo completo de coleta (dados iniciais e fichas técnicas).

    Exemplos:
    ```bash
    python main.py fichacompleta
    python main.py carrosweb --phase 1
    python main.py icarros --phase 3
    ```

*   **Executar todos os scrapers**:
    ```bash
    python main.py full [--phase <phase_number>]
    ```
    Exemplo:
    ```bash
    python main.py full
    ```

### Executando a API

A API RESTful permite consultar os dados de veículos e especificações técnicas. Para iniciá-la:

```bash
cd api
uvicorn main:app --reload
```

Após iniciar, a API estará disponível em `http://127.0.0.1:8000`. Você pode acessar a documentação interativa
(Swagger UI) em `http://127.0.0.1:8000/docs`.

---

## 🗄️ Estrutura do Banco de Dados (MongoDB)

**Conexão Padrão**: 'mongodb://localhost:27017'

**Banco de Dados**: `technical_sheet`

**Collections Principais**:

*   `vehicles`: Armazena os dados básicos dos veículos coletados.
*   `vehicle_specs`: Contém as especificações técnicas detalhadas e equipamentos dos veículos.
*   `logs`: Registros de logs das operações do scraper e da API.
*   `users`: Gerenciamento de usuários para a API (autenticação).
*   `request_logs`: Logs de requisições feitas à API.

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
  "version": "ltz · 1.0 · turbo · at · flex",
  "status": "done" // Novo campo para rastrear o status da coleta
}
```

#### Collection `vehicle_specs` (Especificações completas)

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

*   Os documentos são relacionados pelos campos: `automaker`, `model`, `year`, `version`.
*   O campo `reference` indica a fonte dos dados (`fichacompleta`, `carrosweb`, `icarros`).
*   O `timestamp` registra quando o dado foi coletado.
*   Um novo campo `status` foi adicionado à coleção `vehicles` para rastrear o progresso da
coleta (`todo`, `in_progress`, `done`).

---

## 🛣️ Planos Futuros

   **Adição de Novas Fontes de Dados**: Continuar expandindo as fontes de dados para enriquecer a base de informações.
*   **Melhoria na Coleta de Dados**: Aprimorar a robustez e a eficiência dos scrapers.
*   **Otimização da API**: Melhorar o desempenho e adicionar novas funcionalidades à API.
*   **Implementação de Agendamento**: Ferramenta para agendar a execução automática dos scrapers.
*   **Dashboard de Monitoramento**: Criação de um dashboard para visualizar o status da coleta e os dados.
*   **Testes Automatizados Abrangentes**: Expandir a cobertura de testes para garantir a qualidade do código.

---

## 🤝 Contribuição

Contribuições são bem-vindas!!! Se você deseja contribuir com o projeto, siga os passos abaixo:

1.  Faça um fork do projeto.
2.  Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`).
3.  Commit suas mudanças (`git commit -m "Adicione uma mensagem explicando as mudanças que foram feitas"`).
4.  Push para a branch (`git push origin feature/AmazingFeature`).
5.  Abra um Pull Request.