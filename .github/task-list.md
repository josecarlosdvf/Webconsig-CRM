# 📋 Webconsig CRM/ERP — Task List & Roadmap

> **Última auditoria:** 2026-02-08
> **Fonte de verdade:** `.github/copilot-instructions.md`
> **Critério de "done":** implementado + testado + sem erros de lint/type

---

## Legenda

- ✅ Feito e funcional
- ⚠️ Parcial (existe mas incompleto ou com gaps)
- ❌ Não feito
- 🔲 Não iniciado (planejado)

---

## Fase 0 — Infraestrutura e Scaffold

| # | Item | Status | Notas |
|---|------|--------|-------|
| 0.1 | Estrutura de diretórios backend (domain/, api/, shared/, extensions/) | ✅ | Conforme spec |
| 0.2 | Estrutura de diretórios frontend (src/app/, src/services/, src/components/, src/hooks/, src/stores/, src/types/, src/lib/) | ✅ | Layout base e paginas scaffold com estilos globais |
| 0.3 | `main.py` — bootstrap FastAPI + mount de todos os routers | ✅ | 10 routers registrados |
| 0.4 | `config.py` — AppSettings via Pydantic/dataclass | ✅ | Cobre DB, JWT, tenant, webhook, TLS |
| 0.5 | `dependencies.py` — get_db, get_tenant_id, get_current_user | ✅ | Bearer token + fallback X-Tenant-Id |
| 0.6 | `shared/__init__.py` — Base, mixins (Id, Tenant, Timestamp) | ✅ | |
| 0.7 | `shared/auth.py` — JWT + password hashing | ✅ | bcrypt + python-jose |
| 0.8 | `shared/exceptions.py` — not_found, conflict, forbidden | ✅ | |
| 0.9 | `shared/pagination.py` — PageParams, PaginatedResponse + helpers SQL | ✅ | Completo com paginate_query, get_total_count, build_paginated_response; CRM usando SQL real |
| 0.9.1 | `shared/filters.py` — Query builders SQL reutilizáveis | ✅ | apply_text_filter, apply_text_search, apply_enum_filter, apply_date_range_filter, apply_numeric_range_filter, apply_sorting |
| 0.10 | `shared/audit.py` — AuditLog model + log_action | ✅ | Modelo e helper de log |
| 0.11 | `shared/events.py` — Event bus (WebSocket + Webhook) | ❌ | Placeholder vazio (1 linha docstring) |
| 0.12 | `shared/storage.py` — Abstração S3/Cloudflare/local | ❌ | Placeholder vazio (1 linha docstring) |
| 0.13 | `shared/middleware.py` — Tenant resolution, CORS, logging | ✅ | CORS, request logging e tenant resolution implementados |
| 0.14 | `shared/importer.py` — Engine de importação inteligente | ⚠️ | Models + schemas + service de estado OK; engine de parsing/batch/duplicata NÃO implementado |
| 0.15 | `alembic/env.py` — configuração Alembic | ✅ | Async engine configurado para asyncpg |
| 0.16 | `alembic.ini` — configuração base | ✅ | Logging e file_template configurados |
| 0.17 | Migrations geradas | ✅ | Migration inicial criada com 24 tabelas |
| 0.18 | Seed admin/admin + tenant inicial | ✅ | Seed script em seed.py: admin@webconsig.localhost / admin / tenant UUID criado |
| 0.19 | `requirements.txt` completo e validado | ✅ | Todas as deps instaladas e validadas |
| 0.20 | Docker / docker-compose para dev (app + postgres + redis) | ✅ | PostgreSQL 15 na porta 5433, Redis na 6379 |
| 0.21 | `.env.example` com variáveis documentadas | ✅ | Inclui APP_DATABASE_URL local |

---

## Fase 1 — Backend Core (7 Domínios)

### 1.1 Contratos de domínio (models, schemas, repository, services)

| Domínio | Models | Schemas (Create/Update/Response) | Repository (CRUD) | Services (lógica) | Status |
|---------|--------|----------------------------------|--------------------|--------------------|--------|
| crm | ✅ Client, Lead + enums | ✅ 6 schemas | ✅ CRUD completo | ✅ CRUD + convert_lead | ✅ |
| sales | ✅ Opportunity + enum | ✅ 4 schemas | ✅ CRUD completo | ✅ CRUD + change_stage | ✅ |
| finance | ✅ 5 entidades + 7 enums | ✅ 15 schemas | ✅ CRUD completo | ✅ CRUD + confirm/pay | ✅ |
| billing | ✅ Invoice + enum | ✅ 3 schemas | ✅ CRUD completo | ✅ CRUD + mark_paid | ✅ |
| inventory | ✅ Item, StockAdj + enums | ✅ 4 schemas | ✅ CRUD completo | ✅ CRUD + adjust_stock | ✅ |
| auth | ✅ User, Role + enum | ✅ 8 schemas | ✅ CRUD completo | ✅ CRUD + login + change_pw | ✅ |
| hr | ✅ 9 entidades + 11 enums | ✅ ~25 schemas | ✅ CRUD completo | ✅ CRUD + terminate/advance/approve/assign | ✅ |

### 1.2 Lacunas transversais (todos os domínios)

| # | Item | Status | Impacto |
|---|------|--------|---------|
| 1.2.1 | Paginação real no SQL (LIMIT/OFFSET) nos repositories | ✅ | Aplicado a todos os domínios |
| 1.2.2 | Schemas de filtro por entidade (query params) | ✅ | Todos os domínios com Filters dedicados |
| 1.2.3 | Filtros nos endpoints (name, email, status, date_from, etc.) | ✅ | Endpoints usam filtros e query params |
| 1.2.4 | Sorting (sort=field:asc/desc) | ✅ | Aplicado a todos os domínios |
| 1.2.5 | Busca simples (q=texto) | ✅ | Busca multi-coluna aplicada por entidade |
| 1.2.6 | Validação de transições de estado | ✅ | Regras adicionadas nos services de cada domínio |
| 1.2.7 | Validação de FK cross-tenant | ❌ | Nenhum repository valida se entidades referenciadas pertencem ao mesmo tenant |
| 1.2.8 | Soft-delete completo em todas entidades HR | ⚠️ | Apenas soft_delete_employee existe; falta para as demais 8 entidades |
| 1.2.9 | convert_lead — document vazio hardcoded | ⚠️ | Seta document="" ao converter lead→client |
| 1.2.10 | login retorna 409 em vez de 401 para credenciais inválidas | ⚠️ | Spec diz 401 |
| 1.2.11 | role_ids em User — JSONB em vez de FK real | ⚠️ | Sem integridade referencial |
| 1.2.12 | Logout endpoint — sem lógica de invalidação de token | ❌ | Endpoint existe mas sem blacklist |
| 1.2.13 | Campo quantity no Item (saldo de estoque) | ❌ | adjust_stock registra adjustment mas não atualiza nenhum saldo |
| 1.2.14 | Endpoint extra DELETE /crm/leads/{id} fora da spec | ⚠️ | Avaliar se mantém ou remove |

**📦 Artefatos criados na conclusão parcial do 1.2 (CRM)**:
- `shared/pagination.py` — Helpers SQL completos (paginate_query, get_total_count, build_paginated_response)
- `shared/filters.py` — Query builders reutilizáveis (apply_text_filter, apply_text_search, apply_enum_filter, apply_date_range_filter, apply_numeric_range_filter, apply_sorting)
- `domain/crm/schemas.py` — ClientFilters, LeadFilters com validação Pydantic
- `domain/crm/repository.py` — list_clients e list_leads refatorados com paginação SQL real, filtros aplicados, total count, sorting
- `domain/crm/services.py` — list_clients e list_leads com assinatura nova + validações de transição de estado (VALID_CLIENT_STATUS_TRANSITIONS, VALID_LEAD_STATUS_TRANSITIONS)
- `api/crm.py` — Endpoints GET /clients e GET /leads com query params (filters, sort, page, page_size) e retorno direto do PaginatedResponse SQL

**🎯 Próximos passos**:
1. Aplicar mesmo padrão (1.2.1-1.2.6) aos demais 6 domínios (sales, finance, billing, inventory, auth, hr)
2. Template pronto em CRM para replicação


---

## Fase 1.5 — API Routers

| # | Item | Status | Notas |
|---|------|--------|-------|
| 1.5.1 | Routers CRM (10 endpoints spec) | ✅ | 11 implementados (+1 DELETE lead extra) |
| 1.5.2 | Routers Sales (5 endpoints) | ✅ | |
| 1.5.3 | Routers Finance (21 endpoints) | ✅ | |
| 1.5.4 | Routers Billing (5 endpoints) | ✅ | |
| 1.5.5 | Routers Inventory (5 endpoints) | ✅ | |
| 1.5.6 | Routers Auth (9 endpoints) | ✅ | |
| 1.5.7 | Routers HR (29 endpoints) | ✅ | |
| 1.5.8 | Routers Audit (2 endpoints) | ✅ | Read-only |
| 1.5.9 | Routers Import (10 endpoints) | ⚠️ | Endpoints existem, mas lógica interna é stub (templates vazios, preview vazio, execute no-op) |
| 1.5.10 | Routers Extensions (8 endpoints) | ✅ | |
| 1.5.11 | Audit logging nos endpoints de escrita | ✅ | Inline em cada handler (funciona, mas código repetido) |
| 1.5.12 | Paginação na resposta dos list endpoints | ✅ | Todos os domínios com SQL real |
| 1.5.13 | Refatorar audit logging para decorator/middleware | ❌ | Atualmente inline/duplicado em cada endpoint |

---

## Fase 2 — Eventos e Comunicação em Tempo Real

| # | Item | Status | Notas |
|---|------|--------|-------|
| 2.1 | Event bus — shared/events.py (publish/subscribe) | ❌ | Placeholder |
| 2.2 | WebSocket server — wss://{host}/ws/v1/{tenant_id} | ❌ | |
| 2.3 | Webhook dispatcher — POST com retry+backoff | ❌ | |
| 2.4 | Events CRM — lead.created, client.converted | ❌ | events.py placeholder |
| 2.5 | Events Sales — opportunity.stage_changed | ❌ | events.py placeholder |
| 2.6 | Events Finance — payment.confirmed, receivable.confirmed, reconciliation.completed | ❌ | events.py placeholder |
| 2.7 | Events Billing — invoice.issued, invoice.paid | ❌ | events.py placeholder |
| 2.8 | Events Inventory — stock.adjusted | ❌ | events.py placeholder |
| 2.9 | Events Auth — user.created, user.password_changed | ❌ | events.py placeholder |
| 2.10 | Events HR — 8 eventos (recruitment, candidate, employee, absence, etc.) | ❌ | events.py placeholder |
| 2.11 | Events Import — job.started, job.progress, job.completed, job.failed | ❌ | |
| 2.12 | Events Extensions — activated, deactivated, config_updated, error | ❌ | |
| 2.13 | Payload padrão de evento — idempotency_key, version, trace_id | ❌ | |

---

## Fase 3 — Importação Inteligente de Dados

| # | Item | Status | Notas |
|---|------|--------|-------|
| 3.1 | Model ImportJob + enums (import_status, import_file_format) | ✅ | Em shared/importer.py |
| 3.2 | Schemas (ImportJobResponse, PreviewResponse, ErrorResponse, MappingUpdate) | ✅ | |
| 3.3 | Repository CRUD para import_jobs | ✅ | Básico, sem filtros |
| 3.4 | Service — gestão de estado do job (create, update, cancel) | ✅ | |
| 3.5 | Engine de parsing — CSV reader com charset detection | ❌ | |
| 3.6 | Engine de parsing — XLSX reader | ❌ | |
| 3.7 | Engine de parsing — JSON reader | ❌ | |
| 3.8 | Preview com mapeamento sugerido por similaridade de nomes | ❌ | |
| 3.9 | Validação contra schema da entidade alvo | ❌ | |
| 3.10 | Detecção de duplicatas por campos únicos | ❌ | |
| 3.11 | Processamento em batch (100 linhas/batch, transaction per batch) | ❌ | |
| 3.12 | Modo dry-run (validação sem persistir) | ❌ | |
| 3.13 | Opção update_existing (atualizar registros duplicados) | ❌ | |
| 3.14 | Download de template por domínio/entidade | ❌ | Endpoint retorna CSV vazio |
| 3.15 | Download de relatório de erros | ❌ | |
| 3.16 | Processamento assíncrono (background task) | ❌ | |
| 3.17 | Integração com auditoria (1 log por job) | ❌ | |
| 3.18 | Notificação ao concluir (WebSocket + email opcional) | ❌ | |
| 3.19 | Limite de tamanho de arquivo configurável por tenant | ❌ | |

---

## Fase 4 — Sistema de Extensões

| # | Item | Status | Notas |
|---|------|--------|-------|
| 4.1 | ABC Extension (base.py) | ✅ | get_id, get_router, on_activate, on_deactivate, get_event_handlers |
| 4.2 | ExtensionRegistry (registry.py) | ✅ | register, get, list_all, get_event_handlers |
| 4.3 | Extension middleware/guard (middleware.py) | ✅ | Verifica tenant_id + extension_id ativo → 403 |
| 4.4 | Models: ExtensionDefinition + TenantExtension | ✅ | Em shared/extensions.py |
| 4.5 | Schemas: ExtensionResponse, TenantExtensionResponse, ConfigUpdate | ✅ | |
| 4.6 | Repository + Service para extensions | ✅ | CRUD + activate/deactivate/update_config |
| 4.7 | API Router extensions (8 endpoints) | ✅ | |
| 4.8 | Dynamic loader — descoberta automática de extensões em filesystem | ❌ | loader.py é no-op |
| 4.9 | Execução de migrations de extensão ao ativar | ❌ | |
| 4.10 | Validação de config contra config_schema do manifest | ❌ | |
| 4.11 | Extensão exemplo — consignado (como referência) | ❌ | |

---

## Fase 5 — Multitenancy, Middleware e Segurança

| # | Item | Status | Notas |
|---|------|--------|-------|
| 5.1 | Tenant resolution por host/subdomínio | ⚠️ | TenantResolutionMiddleware implementado (extrai subdomain), mas ainda não valida tenant_id no DB |
| 5.2 | CORS middleware configurável | ✅ | Configure via APP_CORS_ALLOWED_ORIGINS, APP_CORS_ALLOW_CREDENTIALS, etc. — commit 5bc8c90 |
| 5.3 | Request logging middleware | ✅ | RequestLoggingMiddleware com timing (logs method, path, status, time) |
| 5.4 | Rate limiting | ❌ | |
| 5.5 | Whitelabel — config por tenant (nome, logo, cores, tema) | ❌ | |
| 5.6 | Domínio customizado por tenant (CNAME/ALIAS) | ❌ | |
| 5.7 | Seed de tenant + admin/admin no bootstrap | ✅ | seed.py cria tenant UUID, role Admin com todos os scopes, user admin/admin |
| 5.8 | Assistente de primeiro acesso do tenant | ❌ | |
| 5.9 | Scope-based authorization (crm:read, crm:write, etc.) | ✅ | 19 scopes definidos em shared/scopes.py, JWT com scopes, require_scopes() dependency, aplicado aos endpoints CRM — commit 4874629 |
| 5.10 | Password policy (min_len, complexity) | ✅ | PasswordPolicy configurável via APP_PASSWORD_* (min_length, require_uppercase, lowercase, digit, special) — commit 961a367 |

---

## Fase 6 — Storage e Documentos

| # | Item | Status | Notas |
|---|------|--------|-------|
| 6.1 | Abstração de storage (S3/Cloudflare/local) | ❌ | shared/storage.py vazio |
| 6.2 | Upload de arquivos (documentos HR, comprovantes finance, importação) | ❌ | |
| 6.3 | Config de storage por tenant (bucket, region, limits) | ❌ | |
| 6.4 | Validação de tipo/tamanho de arquivo | ❌ | |
| 6.5 | URL assinada para download seguro | ❌ | |

---

## Fase 7 — Workflows Configuráveis

| # | Item | Status | Notas |
|---|------|--------|-------|
| 7.1 | Model WorkflowConfig (stages, transitions, required fields/docs, SLA) | ❌ | |
| 7.2 | CRUD de workflows por tenant | ❌ | |
| 7.3 | Validação de transições de estado contra workflow ativo | ❌ | |
| 7.4 | Campos obrigatórios por etapa e por canal | ❌ | |
| 7.5 | Documentos obrigatórios por etapa | ❌ | |
| 7.6 | SLA por etapa com notificação | ❌ | |
| 7.7 | Labels/nomenclaturas customizáveis por tenant | ❌ | |

---

## Fase 8 — Alembic e Banco de Dados

| # | Item | Status | Notas |
|---|------|--------|-------|
| 8.1 | Corrigir incompatibilidade asyncpg/sync no alembic | ✅ | env.py usa async engine |
| 8.2 | Completar alembic.ini (logging, file_template, etc.) | ✅ | Concluido |
| 8.3 | Gerar migration inicial com todos os models | ✅ | Migration 20260208_0858598983f8_initial.py criada |
| 8.4 | Validar migration inicial (up + down) | ✅ | Upgrade executado com sucesso |
| 8.5 | Seed de dados iniciais (tenant, admin, roles padrão) | ✅ | Tenant + admin/admin + role Admin criados |

---

## Fase 9 — Testes

| # | Item | Status | Notas |
|---|------|--------|-------|
| 9.1 | conftest.py — fixtures async, test DB, auth headers | ✅ | |
| 9.2 | Tests CRM — happy path (create, list, convert) | ✅ | 1 teste, ~6 assertions |
| 9.3 | Tests Sales — happy path | ✅ | 1 teste, 3 assertions |
| 9.4 | Tests Finance — happy path (5 entidades) | ✅ | 1 teste, 8 assertions |
| 9.5 | Tests Billing — happy path | ✅ | 1 teste, 3 assertions |
| 9.6 | Tests Inventory — happy path | ✅ | 1 teste, 3 assertions |
| 9.7 | Tests Auth — happy path (role, user, login, change pw) | ✅ | 1 teste, 4 assertions |
| 9.8 | Tests HR — happy path (9 entidades) | ✅ | 1 teste, ~15 assertions |
| 9.9 | Tests Audit — happy path | ✅ | 1 teste, 3 assertions |
| 9.10 | Tests Import — happy path | ❌ | Sem test_import/ |
| 9.11 | Tests Extensions — happy path | ❌ | Sem test_extensions/ |
| 9.12 | Tests negativos — 400, 401, 403, 404, 409, 422 | ❌ | Nenhum teste de erro |
| 9.13 | Tests de isolamento multitenant | ❌ | Não testa que tenant A ≠ tenant B |
| 9.14 | Tests de paginação (page, page_size, total, has_next) | ❌ | |
| 9.15 | Tests de filtros (query params) | ❌ | |
| 9.16 | Tests de soft-delete (DELETE marca deleted_at, list exclui) | ❌ | |
| 9.17 | Tests de PATCH parcial | ❌ | |
| 9.18 | Tests unitários (services isolados, repository isolado) | ❌ | Tudo é integração e2e |
| 9.19 | Execução dos testes existentes validada (pytest funciona?) | ❌ | Requer PostgreSQL de teste configurado |

---

## Fase 10 — Frontend

| # | Item | Status | Notas |
|---|------|--------|-------|
| 10.1 | Setup Next.js + TypeScript + dependências de UI | ⚠️ | Next.js + React instalados; sem TS como dep, sem lib de UI |
| 10.2 | Layout principal (sidebar, header, tenant branding) | ❌ | Layout atual é HTML mínimo sem providers |
| 10.3 | API client tipado (lib/api-client.ts) | ❌ | lib/ contém apenas .gitkeep |
| 10.4 | Geração de tipos TypeScript a partir do OpenAPI | ❌ | types/ vazio |
| 10.5 | Auth — login, logout, proteção de rotas | ❌ | |
| 10.6 | Services — wrappers tipados para API (7 domínios) | ❌ | Cada arquivo é 1 linha de comentário placeholder |
| 10.7 | Store global (zustand ou similar) | ❌ | stores/ vazio |
| 10.8 | Hooks customizados (useAuth, useTenant, etc.) | ❌ | hooks/ vazio |
| 10.9 | Componentes base (Table, Form, Modal, Button, etc.) | ❌ | components/ vazio |
| 10.10 | Páginas CRM (clients list, detail, leads, convert) | ❌ | Apenas `<main>CRM</main>` |
| 10.11 | Páginas Sales (opportunities, pipeline, stage change) | ❌ | Apenas placeholder |
| 10.12 | Páginas Finance (empresas, contas, pagamentos, payables, receivables) | ❌ | Apenas placeholder |
| 10.13 | Páginas Billing (invoices) | ❌ | Apenas placeholder |
| 10.14 | Páginas Inventory (items, stock) | ❌ | Apenas placeholder |
| 10.15 | Páginas Auth (users, roles, profile) | ❌ | Apenas placeholder |
| 10.16 | Páginas HR (9 entidades) | ❌ | Apenas placeholder |
| 10.17 | Páginas Audit (logs viewer) | ❌ | |
| 10.18 | Páginas Import (upload, preview, mapping, progress) | ❌ | |
| 10.19 | Páginas Extensions (catálogo, ativar/desativar, config) | ❌ | |
| 10.20 | Extensions frontend — lazy loading de componentes | ❌ | extensions/ vazio |
| 10.21 | WebSocket client para eventos em tempo real | ❌ | |
| 10.22 | Responsividade mobile | ❌ | |

---

## Fase 11 — DevOps e Produção

| # | Item | Status | Notas |
|---|------|--------|-------|
| 11.1 | Docker + docker-compose (app + postgres + redis?) | ❌ | |
| 11.2 | .env.example com todas as variáveis documentadas | ✅ | Inclui APP_DATABASE_URL local |
| 11.3 | CI/CD pipeline (lint, test, build) | ❌ | |
| 11.4 | HTTPS/TLS configuração | ❌ | |
| 11.5 | Logging estruturado (JSON logs) | ❌ | |
| 11.6 | Health check endpoint | ❌ | |
| 11.7 | Observabilidade (traces, métricas) | ❌ | |

---

## 📊 Resumo Executivo

| Fase | Progresso | Prioridade |
|------|-----------|------------|
| 0 — Infra & Scaffold | ✅ ~85% | 🔴 Alta |
| 1 — Backend Core (7 domínios) | ✅ ~95% (contratos ok, faltam validações adicionais) | 🔴 Alta |
| 1.5 — API Routers | ✅ ~95% (rotas ok, faltam ajustes em import/audit) | 🔴 Alta |
| 2 — Eventos tempo real | ❌ 0% | 🟡 Média |
| 3 — Importação inteligente | ⚠️ ~25% (scaffold ok, engine não implementada) | 🟡 Média |
| 4 — Extensões | ⚠️ ~65% (core ok, loader e migrations faltam) | 🟡 Média |
| 5 — Multitenancy & Segurança | ❌ ~10% | 🔴 Alta |
| 6 — Storage & Documentos | ❌ 0% | 🟡 Média |
| 7 — Workflows configuráveis | ❌ 0% | 🟡 Média |
| 8 — Alembic & BD | ✅ 100% | 🔴 Alta |
| 9 — Testes | ⚠️ ~25% (happy paths ok, sem negativos/edge cases) | 🔴 Alta |
| 10 — Frontend | ❌ ~5% (scaffold apenas) | 🟠 Média-alta |
| 11 — DevOps | ❌ 0% | 🟡 Média |

---

## 🗺️ Ordem de Execução Recomendada

1. **Fase 8** — Alembic: corrigir config + gerar migrations (sem banco funcionando, nada roda)
2. **Fase 0** — Completar infra: middleware, .env, seed admin
3. **Fase 1.2** — Paginação SQL real + filtros + validações de estado/FK
4. **Fase 5** — Segurança: scopes, CORS, password policy
5. **Fase 9** — Expandir testes: negativos, multitenant, soft-delete
6. **Fase 10** — Frontend: setup completo, auth, primeiras páginas
7. **Fase 2** — Eventos em tempo real
8. **Fase 6** — Storage
9. **Fase 3** — Importação (engine real)
10. **Fase 7** — Workflows configuráveis
11. **Fase 4** — Completar extensões (loader + extensão exemplo)
12. **Fase 11** — DevOps e produção
