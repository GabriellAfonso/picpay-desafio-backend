# 💸 PicPay Simplificado

Este projeto foi desenvolvido como parte do [Desafio Back-end PicPay](https://github.com/PicPay/picpay-desafio-backend), com o objetivo de implementar uma versão simplificada da plataforma de pagamentos.


A aplicação permite a realização de **transferências entre usuários**, seguindo as regras de negócio descritas no desafio, com foco em clareza de código, boas práticas e estrutura escalável.



---

## ⚙️ Tecnologias Utilizadas

- **Django**
- **Django REST Framework**
- **PostgreSQL**
- **Role Permissions**

---

## 🧠 Funcionalidades Principais

- Cadastro de usuários com CPF/CNPJ validado e balance inicial de R$100.
- Distinção entre **usuário comum (personal)** e **lojista (merchant)**.
- Transferência entre usuários com:
  - Verificação de saldo;
  - Verificação de permissões;
  - Validação de não auto-transferência;
  - Autorização externa via API REST;
  - Transação atômica.
- Visualização do perfil com últimas transações.
- Consulta de nome do destinatário via documento.

---

## 🔐 Regras de Negócio Implementadas

- **CPF/CNPJ e e-mail únicos.**
- **Usuários comuns podem transferir valores.**
- **Lojistas apenas recebem, não enviam.**
- **Transferência autorizada apenas se:**
  - O saldo for suficiente;
  - O usuário tiver permissão;
  - O serviço externo autorizar;
- **Rollback automático** em caso de falha (transações atômicas).

---

## 🔁 Exemplo de Endpoint REST

### `POST /api/transaction/`

```json
{
  "value": "100,00",
  "document": "123.456.789-00"
}
```

- O valor será tratado internamente e convertido para `float`.
- O `payer` é o usuário autenticado.
- O `payee` é obtido pelo `document`.

---


## 📌 Diferenciais do Projeto

- Utilização de `@transaction.atomic()` para segurança da operação.
- Separação de responsabilidades com `TransactionValidator`.
- Integração com API externa para autorização.
- Criação dinâmica de permissões com `rolepermissions`.

---

> Este projeto faz parte do meu [Portfólio](https://github.com/GabriellAfonso/portfolio), onde você pode conhecer outros projetos e detalhes do desenvolvedor.
