# Dojo Virtual — API

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-async-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](./Dockerfile)
[![pytest](https://img.shields.io/badge/testes-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](./tests)

Backend do **Dojo Virtual**, um **projeto social**: um sistema de gestão para uma academia de Jiu-Jitsu que centraliza as rotinas administrativas, pedagógicas e financeiras que antes ficavam espalhadas em planilhas e mensagens.

> O frontend (React + TypeScript) está em **[johnpaulo0602/dojo-virtual](https://github.com/johnpaulo0602/dojo-virtual)**.

## Funcionalidades

A API é organizada por domínios, cada um com seus modelos, schemas, regras e rotas:

| Domínio | Responsabilidade |
|---|---|
| `identity` | Usuários, autenticação JWT com refresh token, primeiro acesso e gestão de senhas |
| `academic` | Alunos, responsáveis, escolas, ficha de saúde, contatos de emergência, graduações de faixa e feedback dos instrutores |
| `classes` | Turmas, grade de horários, geração de aulas e controle de presença |
| `financial` | Receitas, despesas, doadores e doações |
| `dashboard` | Resumo consolidado da operação |
| `config` | Categorias, dados da organização e preferências do usuário |

## Stack

- **FastAPI** com documentação OpenAPI automática
- **SQLAlchemy 2 (async)** + **asyncpg** e **Alembic** para migrações
- **PyJWT** + **bcrypt** para autenticação
- **Pydantic Settings** para configuração via variáveis de ambiente
- **pytest** + **pytest-asyncio** para testes
- **uv** para gerenciamento de dependências
- **Docker** para empacotamento

## Como rodar localmente

Pré-requisitos: [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/) e [Docker](https://docs.docker.com/get-docker/).

```bash
# 1. Suba um PostgreSQL local
docker run -d --name dojo-postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres postgres:16

# 2. Instale as dependências
uv sync

# 3. Configure o ambiente (ajuste DATABASE_URL, SECRET_KEY e o admin inicial)
cp .env.example .env

# 4. Crie as tabelas
uv run alembic upgrade head

# 5. Inicie a API com hot-reload
uv run uvicorn src.main:app --reload
```

A API sobe em **http://localhost:8000**, com documentação em [`/docs`](http://localhost:8000/docs) (Swagger) e [`/redoc`](http://localhost:8000/redoc).

O usuário administrador é criado automaticamente na primeira execução a partir de `ADMIN_EMAIL` e `ADMIN_PASSWORD`.

**Dados de demonstração (opcional):** para popular alunos, escolas, turmas e fluxo de caixa de exemplo, rode `uv run python -m src.seed`. Isso **apaga os dados existentes**.

## Testes

```bash
uv run pytest -v
```

## Migrações

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"  # gera uma migração
uv run alembic upgrade head                                       # aplica as pendentes
uv run alembic downgrade -1                                       # desfaz a última
```
