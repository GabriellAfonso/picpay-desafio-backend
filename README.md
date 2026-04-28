# PicPay Clone — Desafio Back-end

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0.3-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red?logo=django&logoColor=white)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)

Solução para o [Desafio Back-end PicPay](https://github.com/PicPay/picpay-desafio-backend): plataforma de pagamentos simplificada com cadastro de usuários (CPF/CNPJ), autenticação por e-mail e transferências entre contas com autorização externa.

---

## Tecnologias

- **Python 3.13** + **Django 6.0.3** + **Django REST Framework**
- **PostgreSQL 17** — banco de dados principal
- **Autenticação por sessão** — login via e-mail e senha
- **drf-spectacular** — documentação OpenAPI/Swagger
- **validate-docbr** — validação de CPF e CNPJ
- **django-role-permissions** — controle de permissões por papel
- **Docker / Docker Compose** — containerização

---

## Como Rodar

**Pré-requisito:** Docker Compose

```bash
git clone https://github.com/GabriellAfonso/picpay-desafio-backend.git
cd picpay-desafio-backend

cp dotenv_files/.env.example dotenv_files/.env

docker compose up --build
```

A API sobe em `http://localhost:8000`.

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET/POST` | `/` | Login por e-mail |
| `GET/POST` | `/cadastro/` | Cadastro com CPF ou CNPJ |
| `GET` | `/Seu-perfil/` | Perfil do usuário autenticado |
| `POST` | `/api/transaction/` | Transferência entre contas |
| `GET` | `/api/recipient-preview/` | Consulta destinatário por documento |
| `GET` | `/api/schema/swagger-ui/` | Documentação interativa (Swagger) |
| `GET` | `/health/` | Health check |

---

## Testes

```bash
cd server && pytest
```

---

GNU General Public License v3.0 — veja [LICENSE](./LICENSE) para detalhes.
