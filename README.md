# Backend API (FastAPI)

Este é o backend do sistema de gestão de academia de Jiu-Jitsu, construído com **FastAPI**, **SQLAlchemy (Async)**, **Alembic** e **PostgreSQL**. O código segue uma arquitetura orientada a domínios (Domain-Driven).

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) (Gerenciador de pacotes ultrarrápido)
- [Docker e Docker Compose](https://docs.docker.com/compose/) (Para rodar o banco de dados)

## Configuração Inicial

1. **Suba o banco de dados localmente:**
   A partir da raiz do projeto (uma pasta acima desta), inicie o contêiner do PostgreSQL:
   ```bash
   docker compose up -d
   ```
   *(Isso iniciará o banco na porta `5432` com as credenciais padrões de desenvolvimento configuradas).*

2. **Sincronize o ambiente:**
   Dentro desta pasta (`api/`), utilize o `uv` para instalar todas as dependências isoladamente:
   ```bash
   uv sync
   ```

3. **Configure as Variáveis de Ambiente:**
   Copie o arquivo `.env.example` para `.env` (o FastAPI com Pydantic Settings fará a leitura automática):
   ```bash
   cp .env.example .env
   ```

4. **Execute as migrações (Setup do Banco):**
   Crie as tabelas iniciais no banco de dados rodando o Alembic:
   ```bash
   uv run alembic upgrade head
   ```

5. **Administrador Inicial:**
   Com as variáveis `ADMIN_EMAIL` e `ADMIN_PASSWORD` preenchidas no seu `.env` (ou `.env.example`), o sistema criará o usuário administrador automaticamente na primeira vez que você rodar o servidor. Não é necessário rodar scripts manuais.

6. **Opcional: Popular com Dados de Teste (Seed):**
   Se quiser testar a aplicação com alunos, escolas, turmas e fluxo de caixa já preenchidos (baseados nos mocks do frontend), execute o comando abaixo.
   *Aviso: Isso apagará os dados existentes e reiniciará o banco com dados de demonstração.*
   ```bash
   uv run python -m src.seed
   ```

## Executando a Aplicação

Para iniciar o servidor local de desenvolvimento com *hot-reload*:

```bash
uv run uvicorn src.main:app --reload
```

A API estará rodando em: **http://localhost:8000**

### Documentação da API

O FastAPI gera a documentação do OpenAPI automaticamente. Com o servidor rodando, acesse:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Executando Testes

O projeto utiliza `pytest` e `pytest-asyncio` para testes. Para rodar toda a suíte:

```bash
uv run pytest -v
```

## Comandos Úteis do Alembic (Migrações)

Sempre que você criar ou alterar um modelo do SQLAlchemy (`models.py`), será necessário criar uma nova migração.

- **Gerar uma nova migração:**
  ```bash
  uv run alembic revision --autogenerate -m "descrição da sua mudança"
  ```

- **Aplicar as migrações pendentes ao banco:**
  ```bash
  uv run alembic upgrade head
  ```

- **Desfazer a última migração aplicada:**
  ```bash
  uv run alembic downgrade -1
  ```
