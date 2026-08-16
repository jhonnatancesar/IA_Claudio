# Segurança

Fonte: seções 20 e 32 da especificação mestre.

## Segurança de APIs (chamadas do Claudião para fora)

- **HTTPS obrigatório para destinos externos.**
- HTTP permitido apenas para serviços locais explicitamente autorizados.
- Validação de endpoint e destino antes da chamada.
- Cada ferramenta possui contrato explícito de capacidades; ações fora do contrato são
  bloqueadas pelo orquestrador.

> Esta exigência de HTTPS é sobre chamadas de **saída** (Web Search Tool, API Tool,
> outros agentes). Não confundir com o acesso de **entrada** de clientes à API do
> Claudião, que é HTTP interno na V1 (ver `ARCHITECTURE.md` → Ambiente da V1, e
> `OUT_OF_SCOPE.md`). As duas coisas usam a expressão "HTTPS obrigatório" na
> especificação mestre em contextos diferentes — ver também `OPEN_QUESTIONS.md`.

## Segredos

- API keys, tokens e segredos externos são **criptografados em repouso**.
- A **chave mestra** fica fora do PostgreSQL, em variável de ambiente ou arquivo
  protegido na máquina — nunca versionada (ver `.gitignore`).

## TASKs relacionadas

TASK-012 e TASK-013: criptografia de segredos, chave mestra externa ao banco.
TASK-096: política HTTPS para o API Tool.
