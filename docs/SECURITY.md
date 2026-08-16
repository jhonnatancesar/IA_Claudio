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

### Criptografia de segredos (TASK-012)

Implementado em `backend/app/auth/crypto.py`, usando `Fernet`
(`cryptography.fernet` — DEC-007): `generate_key()`, `encrypt_secret(plaintext,
key)` (levanta `ValueError` para texto vazio; token inclui timestamp e
autenticação, nunca determinístico) e `decrypt_secret(token, key)` (levanta
`InvalidSecretError` para chave errada ou token adulterado/inválido). Recebe a
chave já pronta — **não decide de onde ela vem**; isso é escopo da TASK-013
(chave mestra externa ao banco), que ainda vai definir como `generate_key()` é
persistida e carregada na prática (arquivo protegido vs. variável de
ambiente).

## TASKs relacionadas

TASK-012 e TASK-013: criptografia de segredos, chave mestra externa ao banco.
TASK-096: política HTTPS para o API Tool.
