# CLAUDE.md — Django Base

> Este arquivo define como o Claude deve se comportar neste projeto.
> Adapte as seções marcadas com `[ADAPTAR]` para cada projeto específico.

---

## 1. Visão Geral do Projeto

- **Nome:** PicPay Clone
- **Objetivo:** Simular o funcionamento básico do PicPay — cadastro de usuários (CPF/CNPJ), login, consulta de perfil e transferências entre contas.
- **Público-alvo:** Portfólio pessoal / estudo de arquitetura Django.

---

## 2. Stack Principal

```
Python 3.11 / Django 6.0.3
API: Django REST Framework 3.16.1
Banco de dados: PostgreSQL 17 (Docker)
Frontend: Django Templates + JS vanilla (sem framework)
Autenticação: django-role-permissions 3.2.0
Validação de documentos: validate-docbr (CPF/CNPJ)
Deploy: Docker Compose (picpay_django + picpay_db)
Testes: pytest + pytest-django
```

---

## 3. Fluxo de Trabalho — Plano Antes de Agir

**Para qualquer tarefa que envolva criar ou modificar código, o Claude DEVE:**

1. **Apresentar um plano** antes de escrever qualquer linha de código. O plano deve conter:
   - Quais arquivos serão criados ou modificados
   - O que cada arquivo fará (em uma frase)
   - Se alguma dependência nova será necessária
   - Riscos ou pontos de atenção identificados

2. **Aguardar confirmação** do usuário ("pode aplicar", "ok", "vai", ou similar).

3. **Só então implementar.**

Exemplo de formato de plano:
```
📋 Plano de implementação:

Criar:
  - features/orders/services/create_order.py — lógica de criação do pedido
  - features/orders/repositories/order_repository.py — acesso ao banco

Modificar:
  - features/orders/urls.py — adicionar rota POST /orders/

Dependências novas: nenhuma
Riscos: nenhum identificado

Posso aplicar?
```

---

## 4. Arquitetura — Feature-Based

O projeto é organizado por **feature** (domínio de negócio), não por tipo técnico.
Cada feature é autossuficiente: contém suas views, serviços, repositórios, modelos e testes.

### 4.1 Estrutura de Pastas

```
project_root/
├── manage.py
├── .env                        # nunca commitar
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/                     # configuração global
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py                 # apenas inclui as urls de cada feature
│   └── wsgi.py
├── features/                   # todo o código de domínio fica aqui
│   └── <feature_name>/         # ex: orders, users, payments
│       ├── __init__.py
│       ├── urls.py
│       ├── models.py           # entidades da feature
│       ├── admin.py
│       ├── views/              # uma view por arquivo se a feature crescer
│       │   └── __init__.py
│       ├── services/           # casos de uso — um arquivo por caso de uso
│       │   └── __init__.py
│       ├── repositories/       # acesso ao banco — isola o ORM
│       │   └── __init__.py
│       ├── serializers/        # se usar DRF
│       │   └── __init__.py
│       ├── forms/              # se usar Django forms
│       │   └── __init__.py
│       └── tests/
│           ├── test_services.py
│           ├── test_views.py
│           └── test_models.py
├── core/                     # código reutilizável entre features
│   ├── exceptions.py           # exceções base do domínio
│   ├── permissions.py
│   └── utils/
├── static/
├── media/
└── docs/
```

### 4.2 Regras da Arquitetura Feature-Based

- **Features não importam umas das outras diretamente.** Se precisar de algo de outra feature, use `core/` ou um evento/signal.
- **Cada feature é uma Django app** registrada no `INSTALLED_APPS` como `features.<nome>`.
- Não crie uma feature só porque um model existe — crie quando há um **domínio de negócio** coeso.
- Quando uma feature crescer demais, divida em sub-features; nunca misture responsabilidades.

---

## 5. Princípios de Design

### 5.1 SOLID

**S — Single Responsibility Principle**
Cada classe ou função tem uma única razão para mudar.
- View: receber request e retornar response. Nada mais.
- Service: executar um caso de uso. Nada mais.
- Repository: interagir com o banco. Nada mais.
- ❌ Errado: uma view que valida dados, faz query, envia email e retorna JSON.

**O — Open/Closed Principle**
Classes abertas para extensão, fechadas para modificação.
- Adicione comportamento via herança ou composição, não editando a classe original.
- Use classes base (`BaseRepository`, `BaseService`) como contratos que as implementações estendem.
- ❌ Errado: adicionar `if tipo == "email"` dentro de um `NotificationService` existente. Certo: criar `EmailNotificationService` que estende a base.

**L — Liskov Substitution Principle**
Subclasses devem substituir a classe base sem quebrar o comportamento esperado.
- Se `StripePaymentService` herda de `BasePaymentService`, qualquer código que use `BasePaymentService` deve funcionar com `StripePaymentService` sem adaptação.
- ❌ Errado: sobrescrever um método e mudar seu contrato — tipos de parâmetros, exceções lançadas ou valor retornado.

**I — Interface Segregation Principle**
Não force uma classe a depender de métodos que ela não usa.
- Prefira ABCs pequenas e focadas. Um repositório somente-leitura não deve herdar de uma classe que também escreve.
- ❌ Errado: um `FullCRUDRepository` com 10 métodos quando a feature só precisa de `get_by_id`.

**D — Dependency Inversion Principle**
Módulos de alto nível não dependem de módulos de baixo nível — ambos dependem de abstrações.
- Services dependem de interfaces de repositório, não da implementação concreta do ORM.
- Injete dependências via construtor.
- ❌ Errado: `OrderService` instancia `OrderRepository()` internamente. ✅ Certo: recebe o repositório como parâmetro.

---

### 5.2 Clean Architecture

O fluxo de dependências sempre aponta para dentro: **Views → Services → Repositories → Models**.
Camadas externas conhecem as internas; camadas internas **nunca** conhecem as externas.

```
┌─────────────────────────────────┐
│  Views / Serializers / Forms    │  ← entrada/saída (HTTP, JSON, HTML)
├─────────────────────────────────┤
│  Services (Casos de Uso)        │  ← regras de negócio da aplicação
├─────────────────────────────────┤
│  Domain / Models                │  ← entidades e regras de negócio puras
├─────────────────────────────────┤
│  Repositories                   │  ← persistência (ORM, cache, APIs externas)
└─────────────────────────────────┘
```

**Regras concretas:**

- **Views** não conhecem repositories. Só chamam services.
- **Services** não importam `request`, `HttpResponse` ou qualquer objeto HTTP.
- **Repositories** são a única camada que importa models Django e faz queries ORM.
- **Models** não importam services nem repositories — são entidades puras.
- Erros de domínio sobem como **exceções de domínio** (definidas em `core/exceptions.py`), não como `Http404` ou `ValidationError` do DRF dentro do service.

Exemplo de fluxo correto:
```python
# views/order_views.py
def create_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = CreateOrderService(OrderRepository()).execute(serializer.validated_data)
    return Response(OrderSerializer(order).data, status=201)

# services/create_order.py
class CreateOrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    def execute(self, data: dict) -> Order:
        # regras de negócio aqui
        return self.order_repo.create(data)

# repositories/order_repository.py
class OrderRepository:
    def create(self, data: dict) -> Order:
        return Order.objects.create(**data)
```

---

## 6. Regras de Código

- **Todo código em inglês.** Nomes de variáveis, funções, classes, arquivos, comentários e mensagens de commit. A única exceção é conteúdo visível ao usuário final (ex: strings em templates).
- **Seja conciso.** Prefira código simples e direto. Evite abstrações desnecessárias.
- **Não duplique lógica.** Se algo já existe no projeto, reutilize.
- **Sem comentários óbvios.** Comente apenas o que não é autoevidente.
- **Type hints** nas assinaturas de funções públicas. Não force em variáveis locais triviais.
- Siga **PEP 8**. Limite de linha: 100 caracteres.
- Models sempre com `__str__`, `Meta.ordering` e `Meta.verbose_name`.
- Prefira `select_related` / `prefetch_related` — nunca queries dentro de loops.
- URLs sempre com `app_name` para namespacing e nomes descritivos.

---

## 7. Segurança — Regras Inegociáveis

- **Nunca hardcode** credenciais, secrets ou chaves. Use sempre variáveis de ambiente.
- **Nunca** desabilite `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_SECURE` ou `SECURE_SSL_REDIRECT` em produção.
- Todo input de usuário que vai pro banco passa por form/serializer com validação.
- Use `get_object_or_404` em vez de `.get()` sem tratamento nas views.
- Permissões explícitas em toda view que exige autenticação.
- `DEBUG = False` em produção. Nunca exponha tracebacks.
- Nunca use `.raw()` ou `format()` em SQL com input do usuário. Use o ORM.

---

## 8. Variáveis de Ambiente

O projeto usa `.env` na raiz. **Nunca sugira colocar valores reais no código.**

```python
import os
SECRET_KEY = os.environ["SECRET_KEY"]           # falha ruidosa se ausente — intencional
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")  # default só em dev
```

---

## 9. Testes

- Todo código novo deve ter testes. Não pule esta etapa.
- Use `pytest-django` com `@pytest.mark.django_db`.
- Teste o comportamento, não a implementação interna.
- Prefira `factory_boy` a fixtures JSON.
- Teste services de forma isolada — mocke repositories quando necessário.
- Mínimo: **caminho feliz + 1 caso de erro** por caso de uso.

---

## 10. Migrações

- Nunca edite uma migração já aplicada em produção.
- Migrações geradas pelo Django (`makemigrations`), não escritas à mão, salvo data migrations.
- Data migrations devem ter o motivo documentado no topo do arquivo.

---

## 11. Como o Claude Deve se Comportar

### Faça:
- **Sempre apresente o plano e aguarde confirmação antes de implementar** (ver seção 3).
- Pergunte antes de criar arquivos fora da estrutura definida.
- Reutilize o que já existe no projeto.
- Aponte ativamente riscos de segurança e violações de arquitetura que encontrar.
- Prefira o que o Django já oferece nativamente.

### Não faça:
- Não implemente nada sem o plano ter sido aprovado.
- Não crie features, models ou migrations sem confirmar.
- Não adicione dependências sem perguntar.
- Não escreva código verboso — concisão é uma virtude aqui.
- Não assuma stack sem verificar `.env` ou `settings/`.
- Não misture responsabilidades de camadas (ex: query ORM dentro de uma view).

---

## 12. Notas Específicas do Projeto

- Há duas camadas de views na feature `picpay`: views HTML (Django templates) e endpoints REST (DRF APIViews). Mantenha essa separação — views HTML em `views/`, endpoints REST em `views/rest_views.py` ou similar.
- O login é feito por **e-mail**, não por username. O form customizado (`EmailAuthenticationForm`) deve viver em `core/forms.py`.
- Existe um fluxo de **Guest Login** que cria usuários temporários para demo — não quebre esse comportamento ao refatorar o registro.
- Validação de CPF/CNPJ usa `validate-docbr`. Os validadores ficam em `features/picpay/validators/`.
- Roles são gerenciadas pelo `django-role-permissions` — o assign de role acontece no service de registro, nunca na view.
- Para rodar localmente: `docker compose up --build`. A app sobe na porta `8001`.
- O arquivo `.env` fica em `dotenv_files/.env`. Nunca comite valores reais.



## 13. Pipeline de Qualidade — Pre-commit + CI/CD

### Visão Geral

O projeto tem três camadas de verificação automática, em ordem de execução:

```
dev faz commit
      ↓
  pre-commit  (local — roda na máquina do dev)
      ↓ push para qualquer branch
  CI          (GitHub Actions — obrigatório, ninguém escapa)
      ↓ somente se CI verde E branch = master
  CD          (GitHub Actions — deploy automático no VPS)
```

---

### Pre-commit (`.pre-commit-config.yaml`)

Roda automaticamente antes de cada `git commit` local, se instalado.

**Hooks configurados:**
- `ruff --fix` — lint com autocorreção
- `ruff-format` — formatação de código
- `bandit` — scan de vulnerabilidades comuns

**Instalar uma vez no projeto:**
```bash
pip install pre-commit
pre-commit install
```

**Rodar manualmente em todos os arquivos:**
```bash
pre-commit run --all-files
```

> O pre-commit é opcional por dev. O CI repete as mesmas verificações como garantia obrigatória.

---

### CI — Continuous Integration (`.github/workflows/ci.yml`)

Roda em todo `push` e `pull_request`, em qualquer branch.

**Etapas em ordem:**
1. `ruff check` — lint (sem autocorreção)
2. `bandit` — security scan
3. `python manage.py migrate --check` — falha se houver migração não aplicada
4. `python manage.py test` — suite completa de testes
5. `docker build` — valida que a imagem builda (só roda se etapas anteriores passarem)

**Variáveis de ambiente necessárias no CI:**
```
DJANGO_SETTINGS_MODULE=config.settings.test
SECRET_KEY=qualquer-valor-nao-usado-em-producao
```

---

### CD — Continuous Delivery (`.github/workflows/cd.yml`)

Roda **somente** quando o CI passa com sucesso no branch `master` (via `workflow_run`).

**Etapas:**
1. SSH no VPS
2. `git pull origin master`
3. `docker compose up --build -d`
4. Health check: `GET /cobblemon-returns/health/` — falha o deploy se o app não subir

**Secrets necessários no GitHub (`Settings → Secrets`):**

| Secret | Valor |
|--------|-------|
| `VPS_HOST` | IP ou domínio do servidor |
| `VPS_USER` | usuário SSH |
| `VPS_SSH_KEY` | chave privada SSH (conteúdo do arquivo) |
| `VPS_APP_PATH` | caminho absoluto do projeto no VPS |

---

### Adaptando para um novo projeto Django

1. Copiar `.pre-commit-config.yaml`, `.github/workflows/ci.yml` e `.github/workflows/cd.yml`
2. Ajustar em `ci.yml`:
   - `python-version` conforme o projeto
   - `DJANGO_SETTINGS_MODULE` para o settings de teste
3. Ajustar em `cd.yml`:
   - URL do health check para o subpath correto do projeto
4. Cadastrar os 4 secrets no GitHub
5. Garantir que o projeto tem uma rota `/health/` que retorna `200 OK`
6. Rodar `pre-commit install` localmente após clonar

---
