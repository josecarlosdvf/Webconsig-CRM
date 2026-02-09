# 🧠 PROMPT-BASE — ARQUITETO DE CRM/ERP IA-FIRST (2026)

Este documento e a **unica fonte de verdade arquitetural** do projeto. Toda geracao de codigo deve segui-lo integralmente. Aplique estas regras **em cada modulo gerado ou modificado**.

---

## 📌 CONTEXTO DO PROJETO

Voce esta desenvolvendo um **CRM/ERP moderno**, robusto, extensivel e sustentavel a longo prazo, **destinado a crescer continuamente em logica e interface sem degradacao estrutural**.

O projeto sera mantido inicialmente por **um unico desenvolvedor**, com **forte uso de agentes de IA para geracao e evolucao de codigo**.

O sistema deve ser:

* Orientado a dominio (nao a telas ou endpoints)
* Contratual (OpenAPI como fonte da verdade)
* Deterministico no core
* IA-first, porem IA **nao decisoria**
* Estruturalmente rigido e logicamente extensivel

Nota: regras sobre ferramentas do AI Toolkit ficam em tools.instructions.md.

---

## 🧱 STACK DEFINIDA (NAO NEGOCIAVEL)

### Backend

* Python 3.12+
* FastAPI (com Depends para injecao de dependencias)
* Pydantic v2 (schemas e validacao)
* SQLAlchemy 2.0+ (async, modelos ORM)
* Alembic (migrations explicitas e versionadas)
* OpenAPI automatico (gerado pelo FastAPI)

### Frontend

* React 18+
* Next.js 14+ (App Router)
* TypeScript strict
* Separacao clara entre UI e consumo de API

### Banco de Dados

* PostgreSQL 15+
* Modelagem relacional
* Migrations explicitas via Alembic

---

## 🧭 PRINCIPIOS OBRIGATORIOS

### 1. Separacao de responsabilidades

* Frontend **nao contem regras de negocio**
* Backend **nao contem logica de UI**
* Banco **nao contem decisoes**
* IA **nao grava diretamente no banco**

---

### 2. Arquitetura orientada a dominio

Toda funcionalidade pertence a um **dominio claro**, como:

* crm
* sales
* finance
* billing
* inventory
* auth
* hr

Nenhuma funcionalidade generica fora de um dominio.

---

### 3. Estrutura raiz do projeto (OBRIGATORIA)

```
backend/
 ├─ main.py                  # bootstrap FastAPI + mount routers
 ├─ config.py                # settings via Pydantic BaseSettings
 ├─ dependencies.py          # Depends globais (get_db, get_tenant, get_current_user)
 ├─ domain/                  # dominios de negocio
 │   ├─ __init__.py
 │   ├─ crm/
 │   ├─ sales/
 │   ├─ finance/
 │   ├─ billing/
 │   ├─ inventory/
 │   ├─ auth/
 │   └─ hr/
 ├─ api/                     # camada de endpoints (routers)
 │   ├─ __init__.py
 │   ├─ crm.py
 │   ├─ sales.py
 │   ├─ finance.py
 │   ├─ billing.py
 │   ├─ inventory.py
 │   ├─ auth.py
 │   └─ hr.py
 ├─ shared/                  # modulos transversais
 │   ├─ __init__.py
 │   ├─ pagination.py        # PaginatedResponse, params de paginacao
 │   ├─ exceptions.py        # excecoes padronizadas (NotFound, Conflict, etc.)
 │   ├─ middleware.py         # tenant resolution, CORS, logging
 │   ├─ events.py            # bus de eventos (WebSocket + Webhook dispatch)
 │   ├─ auth.py              # JWT encode/decode, password hashing
 │   ├─ audit.py             # registro de auditoria (tenant_id, actor_id, ip, timestamp)
 │   ├─ storage.py           # abstração de storage (S3/Cloudflare/local)
 │   └─ importer.py          # engine de importação inteligente (parse, validação, batch insert)
 ├─ alembic/                 # migrations
 │   ├─ versions/
 │   └─ env.py
 ├─ alembic.ini
 ├─ requirements.txt
 └─ tests/
     ├─ conftest.py
     ├─ test_crm/
     ├─ test_sales/
     └─ ...

frontend/
 ├─ src/
 │   ├─ app/                 # Next.js App Router (pages)
 │   │   ├─ crm/
 │   │   ├─ sales/
 │   │   ├─ finance/
 │   │   ├─ billing/
 │   │   ├─ inventory/
 │   │   ├─ auth/
 │   │   └─ hr/
 │   ├─ components/          # componentes de UI reutilizaveis (burros)
 │   ├─ services/            # wrappers de API (fetch tipado)
 │   │   ├─ crm.ts
 │   │   ├─ sales.ts
 │   │   └─ ...
 │   ├─ hooks/               # hooks customizados
 │   ├─ stores/              # estado global (zustand ou similar)
 │   ├─ types/               # tipos TypeScript (gerados do OpenAPI)
 │   └─ lib/                 # utilitarios (api client, auth, tenant)
 ├─ public/
 ├─ next.config.js
 ├─ tsconfig.json
 └─ package.json
```

---

### 4. Estrutura fixa de dominio backend (OBRIGATORIA)

Todo dominio backend deve seguir este padrao:

```
domain/<dominio>/
 ├─ __init__.py      # exporta entidades publicas do dominio
 ├─ models.py        # modelos ORM (SQLAlchemy)
 ├─ schemas.py       # Pydantic schemas (Create, Update, Response, Filters)
 ├─ services.py      # regras de negocio (UNICO lugar para logica)
 ├─ repository.py    # acesso a dados (queries, CRUD)
 └─ events.py        # definicao e emissao de eventos do dominio
```

📌 **Regras absolutas**

> Nenhuma regra de negocio fora de `services.py`.
> Todo acesso a dados passa por `repository.py` (services nunca acessam session diretamente).
> Schemas de entrada (Create/Update) NUNCA incluem `id`, `tenant_id`, `created_at` ou `updated_at`.

---

### 5. Camada de API separada

Endpoints devem existir apenas em:

```
api/<dominio>.py
```

Cada arquivo de API:

* Registra um `APIRouter` com prefix `/api/v1/<dominio>`
* Injeta dependencias via `Depends()` (db session, tenant_id, current_user)
* Valida entrada via Pydantic schemas
* Chama `services` para logica de negocio
* Nunca implementa regra de negocio
* Retorna Pydantic Response schemas

Exemplo de assinatura:

```python
@router.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    return await client_service.create(db, tenant_id, data)
```

---

### 6. Banco de dados

* Tabelas nomeadas por dominio: `<dominio>_<entidade>`
* Estados explicitos (Python Enums mapeados para DB Enums)
* Historico e auditoria previstos em todas as entidades
* Nada implicito
* `tenant_id` como coluna obrigatoria + indice em todas as tabelas de dominio
* Soft-delete padrao: coluna `deleted_at` (nullable timestamp). `DELETE` endpoint marca `deleted_at`, nao apaga fisicamente.

Exemplo de nomes de tabelas:

```
crm_clients
crm_leads
sales_opportunities
finance_accounts
finance_companies
billing_invoices
hr_employees
```

---

### 7. Frontend orientado a dominio

Regras:

* Nenhum `fetch` direto em componentes
* Toda chamada de API passa por `services/*.ts` (wrappers tipados)
* Componentes sao burros (recebem dados via props, nao buscam dados)
* Estado complexo fica em stores (fora da UI)
* Tipos TypeScript devem ser gerados a partir do OpenAPI spec

---

### 8. Contrato como lei

* OpenAPI e a fonte da verdade entre frontend e backend
* Frontend consome contratos tipados (gerados automaticamente)
* Toda mudanca de contrato exige: nova versao do schema + migration + teste
* Nada "implicito" entre frontend e backend

---

### 9. Regras de tenant_id e contexto

* `tenant_id` **NUNCA** aparece no body de requests — e extraido do JWT ou header `X-Tenant-Id`
* Todo repository filtra por `tenant_id` automaticamente
* Todo service recebe `tenant_id` como parametro (injetado pelo endpoint via Depends)
* Nao e permitido acesso cruzado entre tenants em nenhum cenario
* Relacionamentos (FK) devem validar que ambas as entidades pertencem ao mesmo `tenant_id`

---

### 10. Auditoria e rastreabilidade de acoes (OBRIGATORIA)

Todo sistema deve registrar **quem fez o que, quando e onde**. A auditoria e transversal a todos os dominios.

**Tabela: `shared_audit_logs`**

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | Tenant onde a acao ocorreu |
| `actor_id` | UUID | ID do usuario que executou a acao |
| `actor_email` | string | Email do usuario (snapshot no momento da acao) |
| `action` | enum | Tipo de acao executada |
| `domain` | string | Dominio afetado (crm, sales, finance, etc.) |
| `entity` | string | Entidade afetada (clients, leads, payments, etc.) |
| `entity_id` | UUID | ID do registro afetado |
| `changes` | JSONB | Diff dos campos alterados (`{ "field": { "old": X, "new": Y } }`) |
| `ip_address` | string | IP de origem do request |
| `user_agent` | string | User-Agent do request |
| `endpoint` | string | Rota da API chamada (ex: `POST /api/v1/crm/clients`) |
| `occurred_at` | datetime | Timestamp da acao (UTC) |
| `metadata` | JSONB | Dados extras opcionais (ex: motivo, contexto) |

**Enum `audit_action`**: `create`, `update`, `delete`, `restore`, `login`, `logout`, `password_change`, `stage_change`, `approve`, `reject`, `assign`, `convert`, `confirm`, `terminate`, `export`, `import`

**Regras de auditoria:**

* Todo endpoint de escrita (POST, PATCH, DELETE) gera automaticamente um registro de auditoria
* O registro e criado pelo middleware/decorator de auditoria em `shared/audit.py`
* Services NAO geram auditoria diretamente — a camada de API e responsavel
* `changes` armazena apenas os campos que mudaram (diff antes/depois) para PATCH
* Para CREATE, `changes` contem todos os campos do registro criado
* Para DELETE (soft-delete), `changes` contem `{ "deleted_at": { "old": null, "new": "timestamp" } }`
* Audit logs NUNCA sao deletados (nem soft-delete) — retencao minima de 5 anos
* Audit logs sao imutaveis — nao ha UPDATE na tabela de auditoria
* Consultas de auditoria sao read-only e filtradas por `tenant_id`

**Endpoints de auditoria:**

* `GET /api/v1/audit/logs` — Lista paginada de registros de auditoria do tenant
* `GET /api/v1/audit/logs/{entity}/{entity_id}` — Historico de uma entidade especifica

**Filtros de auditoria:** `actor_id`, `action`, `domain`, `entity`, `entity_id`, `date_from`, `date_to`

**Schema AuditLogResponse:**

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "actor_id": "uuid",
  "actor_email": "string",
  "action": "create",
  "domain": "crm",
  "entity": "clients",
  "entity_id": "uuid",
  "changes": {},
  "ip_address": "string",
  "user_agent": "string",
  "endpoint": "string",
  "occurred_at": "date-time",
  "metadata": {}
}
```

**Scope de auditoria:** `audit:read` (somente leitura; nao existe `audit:write`)

---

## ⚙️ REQUISITOS ADICIONAIS (OBRIGATORIOS)

* Tempo real e sincronizacao: usar WebSockets e Webhooks para comunicacao em tempo real entre sistema, componentes e usuarios
* Multitenant desde o inicio (row-level isolation com `tenant_id`)
* Versionamento sempre ativo (API, contratos, migracoes e eventos)
* Testar sempre; se Python, no minimo validar trechos com `python -c`
* Usuario admin inicial: `admin/admin` (senha editavel posteriormente)
* URL sempre com criptografia (HTTPS/TLS)
* O sistema deve se adaptar ao processo do tenant (fluxos e nomenclaturas configuraveis)
* Suporte a empresas de servicos com funis e etapas personalizaveis por tenant
* Integracoes multicanal (WhatsApp API, email, SMS, app mobile) como base operacional
* Soft-delete padrao em todas as entidades (coluna `deleted_at`)
* Queries de listagem devem excluir registros com `deleted_at IS NOT NULL` por padrao
* Toda entidade deve ter `created_at`, `updated_at` (auto-gerenciados) e `deleted_at` (nullable)
* Importacao inteligente de dados com validacao, mapeamento de colunas, deteccao de duplicatas e relatorio de erros

---

### 11. Importacao inteligente de dados (OBRIGATORIA)

O sistema deve suportar importacao em massa de dados para qualquer entidade de dominio, com validacao rigorosa, rastreabilidade e inteligencia no mapeamento.

**Dominios suportados para importacao:**

* `crm` — clients, leads
* `sales` — opportunities
* `finance` — companies, accounts, payables, receivables
* `billing` — invoices
* `inventory` — items
* `auth` — users
* `hr` — employees, candidates, absences, contracts, benefits

**Formatos aceitos:** CSV, XLSX, JSON

**Tabela: `shared_import_jobs`**

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | Tenant que iniciou a importacao |
| `actor_id` | UUID | Usuario que iniciou a importacao |
| `domain` | string | Dominio alvo (crm, sales, finance, etc.) |
| `entity` | string | Entidade alvo (clients, employees, etc.) |
| `file_name` | string | Nome original do arquivo importado |
| `file_url` | string | URL do arquivo armazenado (storage) |
| `file_format` | enum | Formato do arquivo (csv, xlsx, json) |
| `column_mapping` | JSONB | Mapeamento de colunas do arquivo → campos do schema |
| `total_rows` | int | Total de linhas no arquivo |
| `processed_rows` | int | Linhas processadas ate o momento |
| `success_count` | int | Linhas importadas com sucesso |
| `error_count` | int | Linhas com erro |
| `duplicate_count` | int | Linhas ignoradas por duplicidade |
| `status` | enum | Estado da importacao |
| `errors` | JSONB | Lista de erros por linha `[{ "row": 5, "field": "email", "error": "invalid_format" }]` |
| `options` | JSONB | Opcoes da importacao (skip_duplicates, update_existing, dry_run) |
| `started_at` | datetime | Inicio do processamento |
| `completed_at` | datetime (null) | Fim do processamento |
| `created_at` | datetime | Timestamp de criacao |
| `updated_at` | datetime | Timestamp de atualizacao |

**Enum `import_status`**: `pending`, `validating`, `processing`, `completed`, `completed_with_errors`, `failed`, `canceled`

**Enum `import_file_format`**: `csv`, `xlsx`, `json`

**Fluxo de importacao:**

1. **Upload** — Usuario envia arquivo via `POST /api/v1/import/jobs` com `domain`, `entity` e arquivo
2. **Template** — Antes do upload, usuario pode baixar template via `GET /api/v1/import/templates/{domain}/{entity}`
3. **Preview** — Sistema retorna preview das primeiras N linhas com mapeamento sugerido via `POST /api/v1/import/jobs/{job_id}/preview`
4. **Mapeamento** — Usuario ajusta mapeamento de colunas via `PATCH /api/v1/import/jobs/{job_id}/mapping`
5. **Dry-run (opcional)** — Validacao completa sem persistir via `POST /api/v1/import/jobs/{job_id}/validate`
6. **Execucao** — Processamento em batch via `POST /api/v1/import/jobs/{job_id}/execute`
7. **Progresso** — Acompanhamento em tempo real via WebSocket (`import.job.progress`)
8. **Resultado** — Relatorio final com sucesso, erros e duplicatas via `GET /api/v1/import/jobs/{job_id}`
9. **Download de erros** — Arquivo com linhas que falharam via `GET /api/v1/import/jobs/{job_id}/errors`

**Regras de importacao:**

* Toda importacao e associada ao `tenant_id` do usuario.
* Campos obrigatorios do schema da entidade sao validados antes da insercao.
* Campos como `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at` sao gerados automaticamente e NUNCA vem do arquivo.
* Duplicatas sao detectadas por campos unicos da entidade (ex: `email` para clients, `document` para employees, `cnpj` para companies).
* Opcao `skip_duplicates` (default true) ignora duplicatas; `update_existing` (default false) atualiza registros existentes.
* Opcao `dry_run` (default false) valida sem persistir.
* Processamento em batch (default 100 linhas por batch) com transacao por batch.
* Se um batch falha, os anteriores ja persistidos NAO sao revertidos — erros sao registrados por linha.
* Toda importacao gera registro de auditoria: acao `import` com `metadata.job_id` referenciando o job.
* O mapeamento de colunas e inteligente: o sistema sugere mapeamento por similaridade de nomes entre colunas do arquivo e campos do schema.
* Charset detection automatico (UTF-8, ISO-8859-1, Windows-1252).
* Tamanho maximo de arquivo: configuravel por tenant (default 10MB).
* Importacoes sao processadas de forma assincrona (background task).
* O usuario recebe notificacao ao concluir (WebSocket + email opcional).

**Integracao com auditoria:**

* Acao `import` adicionada ao enum `audit_action`.
* Cada job gera UM registro de auditoria com `entity` = entidade alvo, `changes` = `{ "imported": N, "errors": M, "duplicates": D }`.
* Registros individuais criados pela importacao nao geram auditoria individual (evita flood).

---


---

### 12. Sistema de extensoes modulares (OBRIGATORIO)

O sistema deve suportar extensoes (plugins) que adicionam funcionalidades a dominios existentes ou criam novos dominios, sem modificar o core. Extensoes sao ativadas/desativadas por tenant.

**Principios:**

1. O core funciona 100% sem nenhuma extensao ativa
2. Extensoes NAO alteram tabelas do core — criam suas proprias tabelas com prefixo `ext_<id>_`
3. Extensoes registram rotas, eventos e schemas de forma isolada
4. Cada extensao possui um `manifest.json` com metadados e dependencias
5. Extensoes sao carregadas dinamicamente no bootstrap da aplicacao
6. Toda extensao e isolada por `tenant_id`
7. Extensoes podem emitir e escutar eventos do event bus
8. O frontend carrega componentes de extensao dinamicamente (lazy loading)

**Diretorio de extensoes (backend):**

```
backend/
  extensions/
    __init__.py
    base.py          # classe abstrata Extension (ABC)
    registry.py      # registro global de extensoes
    loader.py        # carregamento dinamico no bootstrap
    middleware.py     # guard que verifica se extensao esta ativa para o tenant
    <extension_id>/
      __init__.py
      manifest.json   # metadados da extensao
      models.py       # tabelas ext_<id>_<entidade>
      schemas.py
      services.py
      repository.py
      routes.py       # APIRouter com prefix /api/v1/ext/<id>/
      events.py
```

**Diretorio de extensoes (frontend):**

```
frontend/
  src/
    extensions/
      <extension_id>/
        index.ts      # ponto de entrada
        components/
        services/
        types/
```

**manifest.json (schema):**

```json
{
  "id": "consignado",
  "name": "Credito Consignado",
  "version": "1.0.0",
  "description": "Modulo de credito consignado com tabelas bancarias e comissoes",
  "author": "Webconsig",
  "domain": "sales",
  "dependencies": [],
  "min_core_version": "1.0.0",
  "permissions": ["sales:read", "sales:write", "finance:read"],
  "config_schema": {
    "enable_auto_simulation": { "type": "boolean", "default": false },
    "max_age_limit": { "type": "integer", "default": 80 }
  },
  "events": {
    "emits": ["ext.consignado.simulation_created", "ext.consignado.proposal_sent"],
    "listens": ["sales.opportunity.stage_changed"]
  }
}
```

**Tabela: `shared_extensions`**

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | string (PK) | Identificador unico da extensao (slug) |
| `name` | string | Nome legivel da extensao |
| `version` | string | Versao atual (semver) |
| `description` | string | Descricao da extensao |
| `author` | string | Autor/mantenedor |
| `domain` | string | Dominio principal (sales, crm, finance, etc.) |
| `status` | enum | Estado global da extensao |
| `manifest` | JSONB | Copia completa do manifest.json |

**Enum `extension_status`**: `available`, `deprecated`, `disabled`

**Tabela: `shared_tenant_extensions`**

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | UUID (PK) | PK |
| `tenant_id` | UUID | Tenant que ativou |
| `extension_id` | string (FK) | Referencia para `shared_extensions.id` |
| `status` | enum | Estado da extensao para este tenant |
| `config` | JSONB | Configuracoes especificas do tenant (baseadas em `config_schema`) |
| `activated_at` | datetime | Quando foi ativada |
| `deactivated_at` | datetime (null) | Quando foi desativada (se aplicavel) |
| `activated_by` | UUID | Usuario que ativou |
| `created_at` | datetime | Timestamp de criacao |
| `updated_at` | datetime | Timestamp de atualizacao |

**Enum `tenant_extension_status`**: `active`, `inactive`, `error`

**Ciclo de vida de uma extensao:**

1. **Registro** — Extensao e registrada globalmente em `shared_extensions` (deploy)
2. **Ativacao** — Admin do tenant ativa via `POST /api/v1/extensions/{extension_id}/activate`
3. **Configuracao** — Admin ajusta config via `PATCH /api/v1/extensions/{extension_id}/config`
4. **Execucao** — Middleware verifica se extensao esta ativa antes de processar requests em `/api/v1/ext/<id>/`
5. **Desativacao** — Admin desativa via `POST /api/v1/extensions/{extension_id}/deactivate`
6. **Migracao** — Ao ativar, extensao pode executar migrations proprias (tabelas `ext_<id>_*`)
7. **Remocao** — Extensao pode ser removida do tenant (dados preservados por soft-delete)

**Classe base Extension (ABC):**

```python
from abc import ABC, abstractmethod
from fastapi import APIRouter

class Extension(ABC):
    @abstractmethod
    def get_id(self) -> str: ...

    @abstractmethod
    def get_router(self) -> APIRouter: ...

    @abstractmethod
    async def on_activate(self, tenant_id: UUID, db: AsyncSession) -> None: ...

    @abstractmethod
    async def on_deactivate(self, tenant_id: UUID, db: AsyncSession) -> None: ...

    def get_event_handlers(self) -> dict[str, Callable]: return {}
```

**Middleware de extensao:**

* Toda rota em `/api/v1/ext/<extension_id>/` passa por um guard middleware
* O middleware verifica em `shared_tenant_extensions` se `tenant_id` + `extension_id` esta `active`
* Se nao estiver ativa, retorna `403 Extension not active for this tenant`
* Config do tenant e injetada no request context via `Depends`

**Regras de extensoes:**

* Extensoes NUNCA acessam tabelas do core diretamente — usam services do core via imports
* Tabelas de extensao seguem naming: `ext_<extension_id>_<entidade>` (ex: `ext_consignado_proposals`)
* Rotas de extensao seguem pattern: `/api/v1/ext/<extension_id>/<recurso>`
* Eventos de extensao seguem pattern: `ext.<extension_id>.<evento>`
* Extensoes herdam multitenancy do core (`tenant_id` obrigatorio)
* Extensoes herdam auditoria do core (registros em `shared_audit_logs` com `domain = "ext.<id>"`)
* Config de extensao e validada contra `config_schema` do manifest
* Extensoes podem depender de outras extensoes (field `dependencies` no manifest)
* Versoes de extensao seguem semver; upgrade exige migration
* Extensoes desativadas preservam dados mas nao processam requests

**Integracao com auditoria:**

* Acao `activate_extension` e `deactivate_extension` adicionadas ao enum `audit_action`
* Ativacao/desativacao geram registro de auditoria com `domain = "extensions"`, `entity = extension_id`

**Extensoes planejadas (exemplos):**

| ID | Nome | Dominio | Descricao |
|---|---|---|---|
| `consignado` | Credito Consignado | sales | Tabelas bancarias, simulacoes, comissoes |
| `whatsapp` | WhatsApp Integration | crm | Comunicacao via WhatsApp Business API |
| `email_marketing` | Email Marketing | crm | Campanhas de email em massa |
| `sms_gateway` | SMS Gateway | crm | Envio de SMS em massa |
| `bank_integration` | Integracao Bancaria | finance | Conciliacao automatica, PIX, boletos |
| `payroll` | Folha de Pagamento | hr | Calculo de folha, INSS, IRRF, FGTS |
| `e_social` | eSocial | hr | Envio de eventos para eSocial |
| `nfe` | Nota Fiscal | billing | Emissao de NF-e e NFS-e |
| `reports` | Relatorios Avancados | shared | Dashboards e relatorios customizaveis |
| `mobile_app` | App Mobile | shared | API otimizada para app mobile |


## 🤖 PAPEL DA IA NO PROJETO

A IA deve:

* Criar scaffolding de dominios
* Gerar CRUDs padronizados
* Criar migrations
* Criar testes iniciais
* Expandir funcionalidades **sem quebrar padroes**

A IA **NAO DEVE**:

* Inventar estrutura nova
* Criar atalhos arquiteturais
* Misturar camadas
* Duplicar logica

Se houver duvida, **prefira nao implementar** a violar estrutura.

---

## � USO OBRIGATÓRIO DO TASK-LIST DURANTE DESENVOLVIMENTO

### Task-list.md como fonte da verdade do progresso

**ANTES** de qualquer desenvolvimento ou modificação no sistema:

1. **Consulte sempre** o arquivo `.github/task-list.md` para verificar o status atual dos componentes
2. **Valide o que realmente está implementado** vs. o que está marcado como "feito"
3. **Identifique dependências** entre as tarefas antes de iniciar qualquer trabalho
4. **Priorize** de acordo com a ordem de execução recomendada no task-list

### Regras de uso do task-list

* ✅ **"Feito e funcional"** = implementado + testado + sem erros críticos
* ⚠️ **"Parcial"** = scaffold existe mas incompleto ou com gaps significativos  
* ❌ **"Não feito"** = não implementado ou apenas placeholder/comentário
* 🔲 **"Não iniciado"** = planejado mas aguardando dependências

### Critérios rigorosos para marcar como "Done"

**Backend:**
* Código implementado com lógica funcional (não apenas placeholders)
* Testes passando (pelo menos happy path)
* Sem erros de import/syntax
* Validação manual com `python -c "from module import function; print('OK')"`

**Frontend:**  
* Componentes renderizam corretamente
* Integração com API funcionando
* TypeScript sem erros
* UI responsiva e navegável

**Banco de dados:**
* Migration gerada e testada (up + down)
* Modelos validados contra constraints
* Dados de seed funcionais

### Protocolo de atualização do task-list

**Ao completar uma tarefa:**
1. Teste rigorosamente a funcionalidade
2. Valide dependências downstream não quebradas  
3. Atualize status no task-list com nota explicativa
4. Marque data de conclusão
5. Identifique próximas tarefas desbloqueadas

**Ao encontrar gaps:**
1. Marque status realista (⚠️ ou ❌) 
2. Documente o que falta especificamente
3. Estime complexidade e dependências
4. Ajuste prioridades se necessário

### Ordem de desenvolvimento mandatória

**Siga rigorosamente a ordem do task-list:**
1. Fase 8 (Alembic) — sem banco, nada funciona
2. Fase 0 (Infraestrutura) — foundation crítica
3. Fase 1.2 (Paginação/Filtros) — bloqueadores de produção
4. Demais fases conforme dependências

**NUNCA** implemente funcionalidades de fases posteriores se as dependências anteriores não estiverem ✅.

### Validação antes de commit

**Check-list obrigatório:**
* [ ] Tarefa está marcada como ✅ no task-list?
* [ ] Dependências upstream estão ✅?
* [ ] Testes passando para o escopo modificado?
* [ ] Nenhuma funcionalidade anterior foi quebrada?
* [ ] Status do task-list reflete a realidade?

### Controle de versao obrigatorio

* Sempre executar commit apos qualquer alteracao relevante
* Sempre executar push apos a finalizacao de cada tarefa

---

## �🗺️ PLANEJAMENTO DE DESENVOLVIMENTO (MVP POR DOMINIO)

Este planejamento converte as diretrizes em uma entrega minima, mantendo OpenAPI como lei e separacao total de camadas.

### Escopo transversal minimo (todos os dominios)

* CRUD completo com estados explicitos
* Auditoria e historico previstos
* Multitenancy aplicado a todas as tabelas e consultas
* Eventos em tempo real (WebSocket + Webhook) por dominio
* Contratos OpenAPI versionados

### Dominio crm (MVP)

* Entidades: clientes, leads
* Fluxos: criar, listar, atualizar, desativar
* Eventos: lead criado, cliente convertido

### Dominio sales (MVP)

* Entidades: oportunidades
* Fluxos: criar, listar, atualizar, alterar estagio
* Eventos: estagio alterado

### Servicos e fluxos configuraveis (MVP transversal)

* Etapas e nomenclaturas configuraveis por tenant (ex: funil de credito consignado)
* Regras de transicao com validacoes por etapa
* Campos obrigatorios por etapa e por canal
* SLAs e cadencias por tenant

### Fluxo inicial recomendado (credito consignado)

* prospectar
* solicitar informacoes e documentacao previa para analise
* se for possivel, enviar simulacao/proposta e avancar o fluxo
* comunicacao preferencial via app e WhatsApp (com email como apoio)

### Consignado - tabelas bancarias e comissoes

* Bancos enviam tabelas com convenio (orgao), limite de idade, limite operacional, coeficiente e percentual de comissao.
* O tenant deve cadastrar e versionar essas tabelas (impacto em simuladores e contas a receber).
* Cada tenant define regras internas de comissionamento por grupos e campanhas.
* Bancos podem pagar comissao em datas especificas apos o fechamento (dia do mes ou dia da semana).
* Comissoes internas sao pagas em data posterior, agendada pelo financeiro, separadas da folha.

### Dominio finance (MVP)

* Entidades: contas, pagamentos basicos, empresas (multi-CNPJ por tenant), contas a pagar/receber
* Fluxos: criar, listar, atualizar, conciliar, aprovar pagamentos/recebimentos
* Cada lancamento financeiro deve conter `company_id` (empresa do tenant)
* Contas a pagar/receber com anexos (boletos, comprovantes, notas) via repositorio de documentos
* Integracao bancaria (pix/api bancaria) para pagamento/recebimento e conciliacao automatica
* Eventos: pagamento confirmado, recebimento confirmado, conciliacao realizada

### Dominio billing (MVP)

* Entidades: faturas
* Fluxos: criar, listar, atualizar, marcar como pago
* Eventos: fatura emitida

### Dominio inventory (MVP)

* Entidades: itens, estoque
* Fluxos: criar, listar, atualizar, ajustar saldo
* Eventos: estoque alterado

### Dominio auth (MVP)

* Entidades: usuarios, perfis
* Fluxos: criar, listar, atualizar, trocar senha
* Eventos: usuario criado

### Dominio hr (MVP)

* Entidades: recrutamento, candidatos, funcionarios, faltas, atrasos, atestados/comprovantes, contratos, ferias, beneficios (vr/va/vt), horas extras, desligamentos
* Fluxos: recrutar, contratar, registrar ocorrencias, aprovar ferias, conceder beneficios, desligar
* Integracoes: eventos do RH geram efeitos no financeiro (folha, beneficios, rescisao, contas a pagar/receber) com `company_id`
* Eventos: candidato avancou etapa, funcionario contratado, ausencia registrada, ferias aprovadas, desligamento registrado

---

## 📜 CONTRATOS OPENAPI INICIAIS (POR DOMINIO)

Padrao de versionamento: `/api/v1` (incrementar ao quebrar contrato).

### OpenAPI - crm

* `GET /api/v1/crm/clients`
* `POST /api/v1/crm/clients`
* `GET /api/v1/crm/clients/{client_id}`
* `PATCH /api/v1/crm/clients/{client_id}`
* `DELETE /api/v1/crm/clients/{client_id}`
* `GET /api/v1/crm/leads`
* `POST /api/v1/crm/leads`
* `GET /api/v1/crm/leads/{lead_id}`
* `PATCH /api/v1/crm/leads/{lead_id}`
* `POST /api/v1/crm/leads/{lead_id}/convert`

### OpenAPI - sales

* `GET /api/v1/sales/opportunities`
* `POST /api/v1/sales/opportunities`
* `GET /api/v1/sales/opportunities/{opportunity_id}`
* `PATCH /api/v1/sales/opportunities/{opportunity_id}`
* `POST /api/v1/sales/opportunities/{opportunity_id}/stage`

### OpenAPI - finance

* `GET /api/v1/finance/companies`
* `POST /api/v1/finance/companies`
* `GET /api/v1/finance/companies/{company_id}`
* `PATCH /api/v1/finance/companies/{company_id}`
* `GET /api/v1/finance/accounts`
* `POST /api/v1/finance/accounts`
* `GET /api/v1/finance/accounts/{account_id}`
* `PATCH /api/v1/finance/accounts/{account_id}`
* `GET /api/v1/finance/payments`
* `POST /api/v1/finance/payments`
* `POST /api/v1/finance/payments/{payment_id}/confirm`
* `GET /api/v1/finance/payables`
* `POST /api/v1/finance/payables`
* `GET /api/v1/finance/payables/{payable_id}`
* `PATCH /api/v1/finance/payables/{payable_id}`
* `POST /api/v1/finance/payables/{payable_id}/pay`
* `GET /api/v1/finance/receivables`
* `POST /api/v1/finance/receivables`
* `GET /api/v1/finance/receivables/{receivable_id}`
* `PATCH /api/v1/finance/receivables/{receivable_id}`
* `POST /api/v1/finance/receivables/{receivable_id}/confirm`

### OpenAPI - billing

* `GET /api/v1/billing/invoices`
* `POST /api/v1/billing/invoices`
* `GET /api/v1/billing/invoices/{invoice_id}`
* `PATCH /api/v1/billing/invoices/{invoice_id}`
* `POST /api/v1/billing/invoices/{invoice_id}/mark-paid`

### OpenAPI - inventory

* `GET /api/v1/inventory/items`
* `POST /api/v1/inventory/items`
* `GET /api/v1/inventory/items/{item_id}`
* `PATCH /api/v1/inventory/items/{item_id}`
* `POST /api/v1/inventory/stock-adjustments`

### OpenAPI - auth

* `POST /api/v1/auth/login`
* `POST /api/v1/auth/logout`
* `GET /api/v1/auth/users`
* `POST /api/v1/auth/users`
* `GET /api/v1/auth/users/{user_id}`
* `PATCH /api/v1/auth/users/{user_id}`
* `POST /api/v1/auth/users/{user_id}/change-password`
* `GET /api/v1/auth/roles`
* `POST /api/v1/auth/roles`

### OpenAPI - hr

* `GET /api/v1/hr/employees`
* `POST /api/v1/hr/employees`
* `GET /api/v1/hr/employees/{employee_id}`
* `PATCH /api/v1/hr/employees/{employee_id}`
* `POST /api/v1/hr/employees/{employee_id}/terminate`
* `GET /api/v1/hr/recruitments`
* `POST /api/v1/hr/recruitments`
* `GET /api/v1/hr/recruitments/{recruitment_id}`
* `PATCH /api/v1/hr/recruitments/{recruitment_id}`
* `GET /api/v1/hr/candidates`
* `POST /api/v1/hr/candidates`
* `GET /api/v1/hr/candidates/{candidate_id}`
* `PATCH /api/v1/hr/candidates/{candidate_id}`
* `POST /api/v1/hr/candidates/{candidate_id}/advance`
* `GET /api/v1/hr/absences`
* `POST /api/v1/hr/absences`
* `GET /api/v1/hr/time-entries`
* `POST /api/v1/hr/time-entries`
* `POST /api/v1/hr/time-entries/{time_entry_id}/approve`
* `GET /api/v1/hr/leave-requests`
* `POST /api/v1/hr/leave-requests`
* `POST /api/v1/hr/leave-requests/{leave_request_id}/approve`
* `GET /api/v1/hr/documents`
* `POST /api/v1/hr/documents`
* `GET /api/v1/hr/contracts`
* `POST /api/v1/hr/contracts`
* `GET /api/v1/hr/benefits`
* `POST /api/v1/hr/benefits`
* `POST /api/v1/hr/benefits/{benefit_id}/assign`

### OpenAPI - audit

* `GET /api/v1/audit/logs`
* `GET /api/v1/audit/logs/{entity}/{entity_id}`

### OpenAPI - import

* `GET /api/v1/import/templates/{domain}/{entity}`
* `GET /api/v1/import/jobs`
* `POST /api/v1/import/jobs`
* `GET /api/v1/import/jobs/{job_id}`
* `POST /api/v1/import/jobs/{job_id}/preview`
* `PATCH /api/v1/import/jobs/{job_id}/mapping`
* `POST /api/v1/import/jobs/{job_id}/validate`
* `POST /api/v1/import/jobs/{job_id}/execute`
* `GET /api/v1/import/jobs/{job_id}/errors`
* `POST /api/v1/import/jobs/{job_id}/cancel`

### OpenAPI - extensions

* `GET /api/v1/extensions` (lista extensoes disponiveis)
* `GET /api/v1/extensions/{extension_id}` (detalhes da extensao)
* `POST /api/v1/extensions/{extension_id}/activate` (ativar para tenant)
* `POST /api/v1/extensions/{extension_id}/deactivate` (desativar para tenant)
* `PATCH /api/v1/extensions/{extension_id}/config` (atualizar config do tenant)
* `GET /api/v1/extensions/tenant` (lista extensoes ativas do tenant)
* `GET /api/v1/extensions/tenant/{extension_id}` (detalhes da extensao no tenant)
* `GET /api/v1/extensions/tenant/{extension_id}/config` (config atual do tenant)



---

## 📦 SCHEMAS OPENAPI (REQUEST/RESPONSE)

Padrao de headers:

* `Authorization: Bearer <token>`
* `X-Tenant-Id: <tenant_id>` (se nao houver tenant no token)

### Schemas base (response)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "status": "enum",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

📌 **Convencoes de schemas**

> **CreateRequest**: campos obrigatorios para criacao. NUNCA inclui `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`. Status inicial e definido pelo backend (default), NAO pelo cliente.
> **UpdateRequest**: mesmos campos do CreateRequest, mas TODOS opcionais (Pydantic `Optional`). Usado em PATCH.
> **Response**: inclui todos os campos incluindo `id`, `tenant_id`, timestamps e `deleted_at`.

### Schemas - crm

`ClientCreateRequest`

```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "document": "string"
}
```

`ClientResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "document": "string",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`LeadCreateRequest`

```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "source": "string"
}
```

`LeadResponse` (status default: `new`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "source": "string",
  "status": "new",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - sales

`OpportunityCreateRequest`

```json
{
  "title": "string",
  "client_id": "uuid",
  "value": 0,
  "currency": "BRL"
}
```

`OpportunityResponse` (stage default: `prospecting`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "title": "string",
  "client_id": "uuid",
  "value": 0,
  "currency": "BRL",
  "stage": "prospecting",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - finance

`AccountCreateRequest`

```json
{
  "name": "string",
  "type": "asset",
  "currency": "BRL"
}
```

`AccountResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "type": "asset",
  "currency": "BRL",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`CompanyCreateRequest`

```json
{
  "name": "string",
  "cnpj": "string",
  "trading_name": "string",
  "address": "string"
}
```

`CompanyResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "cnpj": "string",
  "trading_name": "string",
  "address": "string",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`PaymentCreateRequest`

```json
{
  "account_id": "uuid",
  "company_id": "uuid",
  "amount": 0,
  "currency": "BRL",
  "method": "pix"
}
```

`PaymentResponse` (status default: `pending`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "account_id": "uuid",
  "company_id": "uuid",
  "amount": 0,
  "currency": "BRL",
  "method": "pix",
  "status": "pending",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`PayableCreateRequest`

```json
{
  "company_id": "uuid",
  "account_id": "uuid",
  "description": "string",
  "amount": 0,
  "currency": "BRL",
  "due_date": "date",
  "category": "string"
}
```

`PayableResponse` (status default: `pending`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "company_id": "uuid",
  "account_id": "uuid",
  "description": "string",
  "amount": 0,
  "currency": "BRL",
  "due_date": "date",
  "category": "string",
  "status": "pending",
  "paid_at": "date-time | null",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`ReceivableCreateRequest`

```json
{
  "company_id": "uuid",
  "account_id": "uuid",
  "description": "string",
  "amount": 0,
  "currency": "BRL",
  "due_date": "date",
  "category": "string",
  "source_domain": "string",
  "source_id": "uuid"
}
```

`ReceivableResponse` (status default: `pending`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "company_id": "uuid",
  "account_id": "uuid",
  "description": "string",
  "amount": 0,
  "currency": "BRL",
  "due_date": "date",
  "category": "string",
  "source_domain": "string",
  "source_id": "uuid",
  "status": "pending",
  "received_at": "date-time | null",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - billing

`InvoiceCreateRequest`

```json
{
  "client_id": "uuid",
  "company_id": "uuid",
  "total": 0,
  "currency": "BRL",
  "due_date": "date"
}
```

`InvoiceResponse` (status default: `draft`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "client_id": "uuid",
  "company_id": "uuid",
  "total": 0,
  "currency": "BRL",
  "due_date": "date",
  "status": "draft",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - inventory

`ItemCreateRequest`

```json
{
  "sku": "string",
  "name": "string",
  "unit": "unit"
}
```

`ItemResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "sku": "string",
  "name": "string",
  "unit": "unit",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`StockAdjustmentRequest`

```json
{
  "item_id": "uuid",
  "delta": 0,
  "reason": "string"
}
```

### Schemas - auth

`LoginRequest`

```json
{
  "username": "string",
  "password": "string"
}
```

`LoginResponse`

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 0
}
```

`UserCreateRequest`

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role_ids": ["uuid"]
}
```

`UserResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "username": "string",
  "email": "string",
  "status": "active",
  "role_ids": ["uuid"],
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`RoleCreateRequest`

```json
{
  "name": "string"
}
```

`RoleResponse`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - hr

`EmployeeCreateRequest`

```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "document": "string",
  "department": "string",
  "role": "string",
  "company_id": "uuid",
  "hired_at": "date"
}
```

`EmployeeResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "document": "string",
  "department": "string",
  "role": "string",
  "company_id": "uuid",
  "hired_at": "date",
  "terminated_at": "date | null",
  "termination_reason": "string | null",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`RecruitmentCreateRequest`

```json
{
  "position": "string",
  "department": "string",
  "description": "string",
  "vacancies": 1
}
```

`RecruitmentResponse` (status default: `open`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "position": "string",
  "department": "string",
  "description": "string",
  "vacancies": 1,
  "status": "open",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`CandidateCreateRequest`

```json
{
  "recruitment_id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "resume_url": "string | null"
}
```

`CandidateResponse` (status default: `applied`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "recruitment_id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "resume_url": "string | null",
  "status": "applied",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`AbsenceCreateRequest`

```json
{
  "employee_id": "uuid",
  "date": "date",
  "reason": "string | null"
}
```

`AbsenceResponse` (status default: `pending`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "date": "date",
  "reason": "string | null",
  "status": "pending",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`TimeEntryCreateRequest`

```json
{
  "employee_id": "uuid",
  "date": "date",
  "type": "late",
  "minutes": 0,
  "description": "string | null"
}
```

`TimeEntryResponse` (status default: `pending`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "date": "date",
  "type": "late",
  "minutes": 0,
  "description": "string | null",
  "status": "pending",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`LeaveRequestCreateRequest`

```json
{
  "employee_id": "uuid",
  "start_date": "date",
  "end_date": "date",
  "type": "vacation",
  "reason": "string | null"
}
```

`LeaveRequestResponse` (status default: `requested`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "start_date": "date",
  "end_date": "date",
  "type": "vacation",
  "reason": "string | null",
  "status": "requested",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`DocumentCreateRequest`

```json
{
  "employee_id": "uuid",
  "type": "medical_certificate",
  "description": "string",
  "file_url": "string"
}
```

`DocumentResponse`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "type": "medical_certificate",
  "description": "string",
  "file_url": "string",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`ContractCreateRequest`

```json
{
  "employee_id": "uuid",
  "company_id": "uuid",
  "type": "clt",
  "start_date": "date",
  "end_date": "date | null",
  "salary": 0,
  "currency": "BRL"
}
```

`ContractResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "employee_id": "uuid",
  "company_id": "uuid",
  "type": "clt",
  "start_date": "date",
  "end_date": "date | null",
  "salary": 0,
  "currency": "BRL",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

`BenefitCreateRequest`

```json
{
  "type": "vr",
  "description": "string",
  "value": 0,
  "currency": "BRL"
}
```

`BenefitResponse` (status default: `active`)

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "type": "vr",
  "description": "string",
  "value": 0,
  "currency": "BRL",
  "employee_id": "uuid | null",
  "status": "active",
  "created_at": "date-time",
  "updated_at": "date-time",
  "deleted_at": "date-time | null"
}
```

### Schemas - import

`ImportJobResponse`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "actor_id": "uuid",
  "domain": "crm",
  "entity": "clients",
  "file_name": "string",
  "file_url": "string",
  "file_format": "csv",
  "column_mapping": {},
  "total_rows": 0,
  "processed_rows": 0,
  "success_count": 0,
  "error_count": 0,
  "duplicate_count": 0,
  "status": "pending",
  "errors": [],
  "options": {
    "skip_duplicates": true,
    "update_existing": false,
    "dry_run": false
  },
  "started_at": "date-time | null",
  "completed_at": "date-time | null",
  "created_at": "date-time",
  "updated_at": "date-time"
}
```

`ImportPreviewResponse`

```json
{
  "job_id": "uuid",
  "file_columns": ["string"],
  "schema_fields": ["string"],
  "suggested_mapping": {
    "file_column": "schema_field"
  },
  "sample_rows": [{}],
  "total_rows": 0
}
```

`ImportErrorResponse`

```json
{
  "row": 0,
  "field": "string",
  "value": "string | null",
  "error": "string"
}
```

`ImportMappingUpdateRequest`

```json
{
  "column_mapping": {
    "file_column": "schema_field"
  }
}
```

### Schemas - extensions

`ExtensionCreateRequest`

```json
{
  "id": "string",
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string",
  "domain": "string",
  "manifest": {}
}
```

`ExtensionResponse`

```json
{
  "id": "string",
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string",
  "domain": "string",
  "status": "available",
  "manifest": {}
}
```

`TenantExtensionResponse`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "extension_id": "string",
  "status": "active",
  "config": {},
  "activated_at": "date-time",
  "deactivated_at": "date-time | null",
  "activated_by": "uuid",
  "created_at": "date-time",
  "updated_at": "date-time"
}
```

`ExtensionConfigUpdateRequest`

```json
{
  "config": {}
}
```



---

## 🔗 MAPEAMENTO DE ENDPOINTS (SCHEMAS + ERROS)

Padrao de erro (response):

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Codigos base:

* `400` invalid_request
* `401` unauthorized
* `403` forbidden
* `404` not_found
* `409` conflict
* `422` validation_error
* `429` rate_limited
* `500` internal_error

### Endpoints - crm

* `GET /api/v1/crm/clients` -> `ClientResponse[]` | erros: `401`, `403`
* `POST /api/v1/crm/clients` -> `ClientCreateRequest` / `ClientResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/crm/clients/{client_id}` -> `ClientResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/crm/clients/{client_id}` -> `ClientUpdateRequest` / `ClientResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `DELETE /api/v1/crm/clients/{client_id}` -> `204` | erros: `401`, `403`, `404`
* `GET /api/v1/crm/leads` -> `LeadResponse[]` | erros: `401`, `403`
* `POST /api/v1/crm/leads` -> `LeadCreateRequest` / `LeadResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/crm/leads/{lead_id}` -> `LeadResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/crm/leads/{lead_id}` -> `LeadUpdateRequest` / `LeadResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/crm/leads/{lead_id}/convert` -> `ClientResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - sales

* `GET /api/v1/sales/opportunities` -> `OpportunityResponse[]` | erros: `401`, `403`
* `POST /api/v1/sales/opportunities` -> `OpportunityCreateRequest` / `OpportunityResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/sales/opportunities/{opportunity_id}` -> `OpportunityResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/sales/opportunities/{opportunity_id}` -> `OpportunityUpdateRequest` / `OpportunityResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/sales/opportunities/{opportunity_id}/stage` -> `{ "stage": "enum" }` / `OpportunityResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - finance

* `GET /api/v1/finance/companies` -> `CompanyResponse[]` | erros: `401`, `403`
* `POST /api/v1/finance/companies` -> `CompanyCreateRequest` / `CompanyResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/finance/companies/{company_id}` -> `CompanyResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/finance/companies/{company_id}` -> `CompanyUpdateRequest` / `CompanyResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `GET /api/v1/finance/accounts` -> `AccountResponse[]` | erros: `401`, `403`
* `POST /api/v1/finance/accounts` -> `AccountCreateRequest` / `AccountResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/finance/accounts/{account_id}` -> `AccountResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/finance/accounts/{account_id}` -> `AccountUpdateRequest` / `AccountResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `GET /api/v1/finance/payments` -> `PaymentResponse[]` | erros: `401`, `403`
* `POST /api/v1/finance/payments` -> `PaymentCreateRequest` / `PaymentResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `POST /api/v1/finance/payments/{payment_id}/confirm` -> `PaymentResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/finance/payables` -> `PayableResponse[]` | erros: `401`, `403`
* `POST /api/v1/finance/payables` -> `PayableCreateRequest` / `PayableResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/finance/payables/{payable_id}` -> `PayableResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/finance/payables/{payable_id}` -> `PayableUpdateRequest` / `PayableResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/finance/payables/{payable_id}/pay` -> `PayableResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/finance/receivables` -> `ReceivableResponse[]` | erros: `401`, `403`
* `POST /api/v1/finance/receivables` -> `ReceivableCreateRequest` / `ReceivableResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/finance/receivables/{receivable_id}` -> `ReceivableResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/finance/receivables/{receivable_id}` -> `ReceivableUpdateRequest` / `ReceivableResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/finance/receivables/{receivable_id}/confirm` -> `ReceivableResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - billing

* `GET /api/v1/billing/invoices` -> `InvoiceResponse[]` | erros: `401`, `403`
* `POST /api/v1/billing/invoices` -> `InvoiceCreateRequest` / `InvoiceResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/billing/invoices/{invoice_id}` -> `InvoiceResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/billing/invoices/{invoice_id}` -> `InvoiceUpdateRequest` / `InvoiceResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/billing/invoices/{invoice_id}/mark-paid` -> `InvoiceResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - inventory

* `GET /api/v1/inventory/items` -> `ItemResponse[]` | erros: `401`, `403`
* `POST /api/v1/inventory/items` -> `ItemCreateRequest` / `ItemResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/inventory/items/{item_id}` -> `ItemResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/inventory/items/{item_id}` -> `ItemUpdateRequest` / `ItemResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/inventory/stock-adjustments` -> `StockAdjustmentRequest` / `204` | erros: `400`, `401`, `403`, `404`, `409`, `422`

### Endpoints - auth

* `POST /api/v1/auth/login` -> `LoginRequest` / `LoginResponse` | erros: `400`, `401`, `422`
* `POST /api/v1/auth/logout` -> `204` | erros: `401`
* `GET /api/v1/auth/users` -> `UserResponse[]` | erros: `401`, `403`
* `POST /api/v1/auth/users` -> `UserCreateRequest` / `UserResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/auth/users/{user_id}` -> `UserResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/auth/users/{user_id}` -> `UserUpdateRequest` / `UserResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/auth/users/{user_id}/change-password` -> `{ "password": "string" }` / `204` | erros: `400`, `401`, `403`, `404`, `422`
* `GET /api/v1/auth/roles` -> `RoleResponse[]` | erros: `401`, `403`
* `POST /api/v1/auth/roles` -> `RoleCreateRequest` / `RoleResponse` | erros: `400`, `401`, `403`, `409`, `422`

### Endpoints - hr

* `GET /api/v1/hr/employees` -> `EmployeeResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/employees` -> `EmployeeCreateRequest` / `EmployeeResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/employees/{employee_id}` -> `EmployeeResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/hr/employees/{employee_id}` -> `EmployeeUpdateRequest` / `EmployeeResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/hr/employees/{employee_id}/terminate` -> `{ "reason": "string" }` / `EmployeeResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/hr/recruitments` -> `RecruitmentResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/recruitments` -> `RecruitmentCreateRequest` / `RecruitmentResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/recruitments/{recruitment_id}` -> `RecruitmentResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/hr/recruitments/{recruitment_id}` -> `RecruitmentUpdateRequest` / `RecruitmentResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `GET /api/v1/hr/candidates` -> `CandidateResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/candidates` -> `CandidateCreateRequest` / `CandidateResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/candidates/{candidate_id}` -> `CandidateResponse` | erros: `401`, `403`, `404`
* `PATCH /api/v1/hr/candidates/{candidate_id}` -> `CandidateUpdateRequest` / `CandidateResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/hr/candidates/{candidate_id}/advance` -> `{ "stage": "enum" }` / `CandidateResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/hr/absences` -> `AbsenceResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/absences` -> `AbsenceCreateRequest` / `AbsenceResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/time-entries` -> `TimeEntryResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/time-entries` -> `TimeEntryCreateRequest` / `TimeEntryResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `POST /api/v1/hr/time-entries/{time_entry_id}/approve` -> `TimeEntryResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/hr/leave-requests` -> `LeaveRequestResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/leave-requests` -> `LeaveRequestCreateRequest` / `LeaveRequestResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `POST /api/v1/hr/leave-requests/{leave_request_id}/approve` -> `LeaveRequestResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/hr/documents` -> `DocumentResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/documents` -> `DocumentCreateRequest` / `DocumentResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/contracts` -> `ContractResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/contracts` -> `ContractCreateRequest` / `ContractResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `GET /api/v1/hr/benefits` -> `BenefitResponse[]` | erros: `401`, `403`
* `POST /api/v1/hr/benefits` -> `BenefitCreateRequest` / `BenefitResponse` | erros: `400`, `401`, `403`, `409`, `422`
* `POST /api/v1/hr/benefits/{benefit_id}/assign` -> `{ "employee_id": "uuid" }` / `BenefitResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - audit

* `GET /api/v1/audit/logs` -> `AuditLogResponse[]` | erros: `401`, `403`
* `GET /api/v1/audit/logs/{entity}/{entity_id}` -> `AuditLogResponse[]` | erros: `401`, `403`, `404`

### Endpoints - import

* `GET /api/v1/import/templates/{domain}/{entity}` -> arquivo (CSV/XLSX) | erros: `400`, `401`, `403`, `404`
* `GET /api/v1/import/jobs` -> `ImportJobResponse[]` | erros: `401`, `403`
* `POST /api/v1/import/jobs` -> `ImportJobCreateRequest` (multipart + file) / `ImportJobResponse` | erros: `400`, `401`, `403`, `422`
* `GET /api/v1/import/jobs/{job_id}` -> `ImportJobResponse` | erros: `401`, `403`, `404`
* `POST /api/v1/import/jobs/{job_id}/preview` -> `ImportPreviewResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `PATCH /api/v1/import/jobs/{job_id}/mapping` -> `ImportMappingUpdateRequest` / `ImportJobResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `POST /api/v1/import/jobs/{job_id}/validate` -> `ImportJobResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `POST /api/v1/import/jobs/{job_id}/execute` -> `ImportJobResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `GET /api/v1/import/jobs/{job_id}/errors` -> `ImportErrorResponse[]` | erros: `401`, `403`, `404`
* `POST /api/v1/import/jobs/{job_id}/cancel` -> `ImportJobResponse` | erros: `400`, `401`, `403`, `404`, `409`

### Endpoints - extensions

* `GET /api/v1/extensions` -> `ExtensionResponse[]` | erros: `401`, `403`
* `GET /api/v1/extensions/{extension_id}` -> `ExtensionResponse` | erros: `401`, `403`, `404`
* `POST /api/v1/extensions/{extension_id}/activate` -> `TenantExtensionResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `POST /api/v1/extensions/{extension_id}/deactivate` -> `TenantExtensionResponse` | erros: `400`, `401`, `403`, `404`, `409`
* `PATCH /api/v1/extensions/{extension_id}/config` -> `ExtensionConfigUpdateRequest` / `TenantExtensionResponse` | erros: `400`, `401`, `403`, `404`, `422`
* `GET /api/v1/extensions/tenant` -> `TenantExtensionResponse[]` | erros: `401`, `403`
* `GET /api/v1/extensions/tenant/{extension_id}` -> `TenantExtensionResponse` | erros: `401`, `403`, `404`
* `GET /api/v1/extensions/tenant/{extension_id}/config` -> `{ "config": {} }` | erros: `401`, `403`, `404`



---

## 📃 LISTAS, PAGINACAO E FILTROS

Padrao de lista (response):

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0,
  "has_next": false
}
```

Query params comuns:

* `page` (int, default 1)
* `page_size` (int, default 20, max 100)
* `sort` (ex: `created_at:desc`)
* `q` (busca simples)

### Filtros - crm

* clients: `name`, `email`, `document`, `status`, `created_from`, `created_to`
* leads: `name`, `email`, `source`, `status`, `created_from`, `created_to`

### Filtros - sales

* opportunities: `client_id`, `stage`, `value_min`, `value_max`, `created_from`, `created_to`

### Filtros - finance

* companies: `name`, `cnpj`, `status`
* accounts: `type`, `status`, `currency`
* payments: `account_id`, `company_id`, `status`, `method`, `created_from`, `created_to`
* payables: `company_id`, `account_id`, `status`, `category`, `due_from`, `due_to`, `created_from`, `created_to`
* receivables: `company_id`, `account_id`, `status`, `category`, `source_domain`, `due_from`, `due_to`, `created_from`, `created_to`

### Filtros - billing

* invoices: `client_id`, `status`, `due_from`, `due_to`, `created_from`, `created_to`

### Filtros - inventory

* items: `sku`, `name`, `status`

### Filtros - auth

* users: `username`, `email`, `status`, `role_id`

### Filtros - hr

* employees: `name`, `status`, `department`, `role`, `hired_from`, `hired_to`
* recruitments: `status`, `position`, `created_from`, `created_to`
* candidates: `status`, `recruitment_id`, `created_from`, `created_to`
* absences: `employee_id`, `status`, `date_from`, `date_to`
* time_entries: `employee_id`, `type`, `status`, `date_from`, `date_to`
* leave_requests: `employee_id`, `status`, `date_from`, `date_to`
* documents: `employee_id`, `type`, `status`, `created_from`, `created_to`
* contracts: `employee_id`, `type`, `status`, `created_from`, `created_to`
* benefits: `employee_id`, `type`, `status`

### Filtros - audit

* logs: `actor_id`, `action`, `domain`, `entity`, `entity_id`, `date_from`, `date_to`

### Filtros - import

* jobs: `domain`, `entity`, `status`, `actor_id`, `created_from`, `created_to`


### Filtros - extensions

* extensions: `status`, `domain`, `author`, `q`
* tenant_extensions: `extension_id`, `status`


---

## 🧩 ESTADOS (ENUMS) POR ENTIDADE

* `crm_clients.status`: `active`, `inactive`
* `crm_leads.status`: `new`, `contacted`, `qualified`, `disqualified`, `converted`
* `sales_opportunities.stage`: `prospecting`, `proposal`, `negotiation`, `won`, `lost`
* `finance_accounts.status`: `active`, `inactive`
* `finance_accounts.type`: `asset`, `liability`, `income`, `expense`
* `finance_payments.status`: `pending`, `confirmed`, `failed`, `canceled`
* `finance_payments.method`: `pix`, `card`, `bank_transfer`, `cash`
* `finance_companies.status`: `active`, `inactive`
* `finance_payables.status`: `pending`, `approved`, `paid`, `overdue`, `canceled`
* `finance_receivables.status`: `pending`, `confirmed`, `received`, `overdue`, `canceled`
* `billing_invoices.status`: `draft`, `issued`, `overdue`, `paid`, `canceled`
* `inventory_items.status`: `active`, `inactive`
* `inventory_items.unit`: `unit`, `kg`, `g`, `l`, `ml`, `m`, `cm`
* `auth_users.status`: `active`, `blocked`
* `hr_employees.status`: `active`, `inactive`, `terminated`
* `hr_recruitments.status`: `open`, `on_hold`, `closed`
* `hr_candidates.status`: `applied`, `screening`, `interview`, `offer`, `hired`, `rejected`
* `hr_absences.status`: `pending`, `justified`, `unexcused`
* `hr_time_entries.type`: `late`, `overtime`, `regular`
* `hr_time_entries.status`: `pending`, `approved`, `rejected`
* `hr_leave_requests.status`: `requested`, `approved`, `rejected`, `canceled`
* `hr_documents.type`: `medical_certificate`, `proof`, `contract`, `other`
* `hr_contracts.type`: `clt`, `pj`, `intern`, `temp`
* `hr_contracts.status`: `active`, `expired`, `terminated`
* `hr_benefits.type`: `vr`, `va`, `vt`
* `hr_benefits.status`: `active`, `suspended`, `canceled`
* `shared_import_jobs.status`: `pending`, `validating`, `processing`, `completed`, `completed_with_errors`, `failed`, `canceled`
* `shared_import_jobs.file_format`: `csv`, `xlsx`, `json`
* `shared_extensions.status`: `available`, `deprecated`, `disabled`
* `shared_tenant_extensions.status`: `active`, `inactive`, `error`


---

## 🏢 MODELO MULTITENANT (TENANT_ID, SCOPES E POLITICAS)

* `tenant_id` obrigatorio em todas as tabelas de dominio.
* `tenant_id` propagado em claims de autenticacao e em todas as consultas.
* Chave composta ou indice por `tenant_id` em entidades de negocio.
* Nao permitir acesso cruzado entre tenants, inclusive em relacionamentos.

### Scopes minimos (auth)

* `crm:read`, `crm:write`
* `sales:read`, `sales:write`
* `finance:read`, `finance:write`
* `billing:read`, `billing:write`
* `inventory:read`, `inventory:write`
* `auth:read`, `auth:write`
* `hr:read`, `hr:write`
* `audit:read`
* `import:read`, `import:write`
* `extensions:read`, `extensions:write`, `extensions:manage`


### Politicas

* Toda query filtra por `tenant_id`.
* Toda acao de escrita valida escopo e tenant.
* Admin global existe apenas dentro do proprio tenant.
* Logs e auditoria registram `tenant_id`, `actor_id`, `ip` e `timestamp`.

### Whitelabel por tenant (obrigatorio)

* Cada tenant possui identidade visual e configuracoes proprias (nome do sistema, logo, icones, cores, temas, lingua, politicas).
* O admin master cria e habilita tenants, define limites, dominios permitidos e usuarios iniciais.
* O acesso ocorre por subdominio dedicado: `empresaX.hubsystecnologia.com.br` (dominio base configuravel).
* Tambem e suportado dominio proprio do tenant (ex: `sistema.empresax.com.br`) via CNAME/ALIAS.
* O primeiro acesso do tenant abre um assistente de configuracao para finalizar dados da empresa e preferencias.
* Todas as configuracoes devem ser armazenadas por `tenant_id` e carregadas no bootstrap do frontend.
* O backend deve validar o tenant pela origem (host/subdominio) + claims (token/header).
* O frontend deve carregar tema, branding e textos dinamicamente a partir da configuracao do tenant.

---

## ⚙️ PLANEJAMENTO DE CONFIGURACOES (CAPILARIZADO)

### Config - Backend

* `APP_ENV` (development|staging|production)
* `API_VERSION` (ex: v1)
* `DATABASE_URL`
* `JWT_SECRET` e `JWT_EXPIRES_IN`
* `TENANT_HEADER` (default `X-Tenant-Id`)
* `WEBHOOK_SECRET`
* `ENABLE_TLS` (true|false)

### Config - Banco de dados

* `DB_POOL_SIZE`, `DB_POOL_MAX_OVERFLOW`
* `DB_CONN_TIMEOUT`
* `DB_SSLMODE` (require em producao)

### Config - Autenticacao e autorizacao

* `ACCESS_TOKEN_TTL`
* `REFRESH_TOKEN_TTL`
* `PASSWORD_POLICY` (min_len, complexity)
* `ADMIN_DEFAULT_PASSWORD` (default `admin`)

### Config - Multitenancy

* `TENANT_ISOLATION_MODE` (row_level)
* `TENANT_RESOLUTION` (host|token|header)
* `TENANT_ID_REQUIRED` (true|false)

### Config - Whitelabel

* `BASE_DOMAIN` (ex: hubsystecnologia.com.br)
* `TENANT_SUBDOMAIN_MODE` (subdomain)
* `TENANT_CUSTOM_DOMAIN_ENABLED` (true|false)
* `TENANT_CUSTOM_DOMAIN_SOURCE` (db)
* `TENANT_BRANDING_SOURCE` (db)
* `TENANT_SETUP_REQUIRED` (true|false)
* `TENANT_ALLOWED_DOMAINS` (lista)

### Config - Processos e nomenclaturas

* `TENANT_WORKFLOW_SOURCE` (db)
* `TENANT_STAGE_LABELS_SOURCE` (db)
* `TENANT_REQUIRED_FIELDS_SOURCE` (db)
* `TENANT_SLA_RULES_SOURCE` (db)
* `TENANT_NOTIFICATION_RULES_SOURCE` (db)

### Config - Canais e comunicacao

* `WHATSAPP_PROVIDER`
* `WHATSAPP_WEBHOOK_SECRET`
* `EMAIL_PROVIDER`
* `SMS_PROVIDER`
* `PUSH_PROVIDER`
* `MOBILE_APP_BASE_URL`

### Config - Documentos e armazenamento

* `DOCUMENTS_STORAGE_PROVIDER` (s3|cloudflare|local)
* `DOCUMENTS_BUCKET`
* `DOCUMENTS_REGION`
* `DOCUMENTS_ENDPOINT`
* `DOCUMENTS_ACCESS_KEY`
* `DOCUMENTS_SECRET_KEY`
* `DOCUMENTS_PUBLIC_BASE_URL`

---

## 🧩 SCHEMAS DE CONFIGURACAO (WORKFLOW E DOCUMENTOS)

### WorkflowConfig

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "domain": "sales",
  "name": "Credito consignado",
  "version": 1,
  "active": true,
  "stages": [
    {
      "id": "uuid",
      "key": "prospecting",
      "label": "Prospectar",
      "order": 1,
      "required_fields": ["lead_name", "phone"],
      "required_documents": ["rg", "comprovante_renda"],
      "sla_hours": 24
    }
  ],
  "transitions": [
    {
      "from": "prospecting",
      "to": "pre_analysis",
      "rules": [
        {
          "type": "required_fields",
          "fields": ["lead_name", "phone"]
        },
        {
          "type": "required_documents",
          "documents": ["rg", "comprovante_renda"]
        }
      ]
    }
  ],
  "channels": {
    "whatsapp": {
      "required_fields": ["phone"],
      "allowed": true
    },
    "email": {
      "required_fields": ["email"],
      "allowed": true
    },
    "app": {
      "required_fields": ["client_id"],
      "allowed": true
    }
  },
  "metadata": {
    "schema_version": 1
  }
}
```

### WorkflowStage

```json
{
  "id": "uuid",
  "key": "pre_analysis",
  "label": "Analise previa",
  "order": 2,
  "required_fields": ["document"],
  "required_documents": ["rg", "comprovante_residencia"],
  "sla_hours": 48
}
```

### WorkflowTransition

```json
{
  "from": "pre_analysis",
  "to": "proposal",
  "rules": [
    {
      "type": "stage_status",
      "status": "approved"
    },
    {
      "type": "required_documents",
      "documents": ["rg", "comprovante_residencia"]
    }
  ]
}
```

### RequiredFieldRule

```json
{
  "type": "required_fields",
  "fields": ["name", "email", "phone"]
}
```

### RequiredDocumentRule

```json
{
  "type": "required_documents",
  "documents": ["rg", "contracheque"]
}
```

### DocumentRepositoryConfig

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "provider": "s3",
  "bucket": "tenant-docs",
  "region": "sa-east-1",
  "endpoint": "https://s3.amazonaws.com",
  "access_key": "string",
  "secret_key": "string",
  "public_base_url": "https://cdn.tenant.com/docs",
  "retention_days": 3650,
  "encryption": "aes256",
  "allowed_types": ["pdf", "png", "jpg"],
  "max_file_mb": 25,
  "metadata": {
    "schema_version": 1
  }
}
```

### DocumentTypeConfig

```json
{
  "key": "rg",
  "label": "Documento de identidade",
  "required": true,
  "expires_in_days": 3650,
  "allowed_types": ["pdf", "png", "jpg"],
  "max_file_mb": 10
}
```

### Config - Eventos em tempo real

* `WEBSOCKET_URL` (wss://...)
* `WEBHOOK_RETRY_MAX`
* `WEBHOOK_RETRY_BACKOFF`
* `EVENTS_VERSION` (ex: 1)

### Config - Observabilidade

* `LOG_LEVEL`
* `TRACE_ENABLED`
* `METRICS_ENABLED`

### Config - Frontend

* `NEXT_PUBLIC_API_BASE_URL`
* `NEXT_PUBLIC_WEBSOCKET_URL`
* `NEXT_PUBLIC_APP_VERSION`

---

## ⚡ EVENTOS EM TEMPO REAL (WEBSOCKET + WEBHOOK)

Padrao WebSocket (por tenant): `wss://<host>/ws/v1/{tenant_id}`

Padrao Webhook (por tenant): `POST https://<host>/webhooks/v1/{tenant_id}`

### Payload padrao (eventos)

```json
{
  "id": "uuid",
  "type": "domain.event",
  "version": 1,
  "occurred_at": "date-time",
  "tenant_id": "uuid",
  "idempotency_key": "string",
  "actor": {
    "id": "uuid",
    "type": "user"
  },
  "source": "api",
  "trace_id": "string",
  "data": {},
  "metadata": {
    "schema_version": 1
  }
}
```

Regras:

* `idempotency_key` unico por evento para evitar duplicidade
* `version` incrementa ao quebrar contrato do evento
* `metadata.schema_version` controla mudancas internas sem quebra

### Events - crm

* `crm.lead.created`
* `crm.client.converted`

### Events - sales

* `sales.opportunity.stage_changed`

### Events - finance

* `finance.payment.confirmed`
* `finance.receivable.confirmed`
* `finance.reconciliation.completed`

### Events - billing

* `billing.invoice.issued`
* `billing.invoice.paid`

### Events - inventory

* `inventory.stock.adjusted`

### Events - auth

* `auth.user.created`
* `auth.user.password_changed`

### Events - hr

* `hr.recruitment.created`
* `hr.candidate.stage_changed`
* `hr.employee.hired`
* `hr.employee.terminated`
* `hr.absence.recorded`
* `hr.time_entry.approved`
* `hr.leave.approved`
* `hr.benefit.assigned`

### Events - import

* `import.job.started`
* `import.job.progress`
* `import.job.completed`
* `import.job.failed`

### Events - extensions

* `extensions.activated`
* `extensions.deactivated`
* `extensions.config_updated`
* `extensions.error`



---

## ✅ CHECK-LIST DE QUALIDADE (OBRIGATÓRIO)

Toda entrega gerada pela IA deve responder **SIM** para todas as perguntas abaixo:

### Checklist - Arquitetura

* [ ] A funcionalidade pertence a um domínio claro?
* [ ] A estrutura segue exatamente o padrão definido?
* [ ] Nenhuma regra está fora de `services.py`?

### Checklist - Backend

* [ ] Endpoints apenas orquestram?
* [ ] Há separação entre schema, model e service?
* [ ] O OpenAPI reflete corretamente a funcionalidade?

### Checklist - Frontend

* [ ] Componentes não contêm regra de negócio?
* [ ] O consumo de API passa por services?
* [ ] A UI pode mudar sem afetar o backend?

### Checklist - Banco

* [ ] O banco armazena fatos, não decisões?
* [ ] Estados são explícitos?
* [ ] Há caminho para auditoria/histórico?

### Checklist - IA

* [ ] A IA apenas sugere, não decide?
* [ ] Toda ação crítica passa pelo backend?
* [ ] O sistema continua funcional sem IA?


### Checklist - Extensoes

* [ ] A extensao funciona isolada do core?
* [ ] Tabelas seguem naming `ext_<id>_<entidade>`?
* [ ] Eventos seguem pattern `ext.<id>.<evento>`?
* [ ] Rotas seguem pattern `/api/v1/ext/<id>/`?
* [ ] O core continua funcional sem a extensao?
* [ ] Multitenancy e auditoria sao herdados do core?


---

## 📎 REGRA FINAL (NÃO QUEBRAR)

> **Se uma funcionalidade não couber naturalmente nesta estrutura, ela está mal definida. Refaça o design antes de codar.**

---

## 🔒 OBJETIVO FINAL

Criar um CRM/ERP que:

* Cresce por adição, não por remendo
* Pode ser mantido por humanos ou IAs
* Permite evolução visual sem quebrar lógica
* Permite evolução lógica sem quebrar UI
* Permanece confiável com o tempo

````
