# API para aplicações

Fonte: seções 24, 25 e 26 da especificação mestre.

## Aplicações e autenticação

- Cada aplicação tem sua própria API key/token. Usuários humanos usam usuário e senha
  (ver `AUTHENTICATION.md`).
- A aplicação envia contexto, tipo de uso, política (`ExecutionPolicy`), permissão de
  pesquisa, timeout, limites e dados necessários.
- O agente valida os campos obrigatórios antes de iniciar. **Se faltar campo
  obrigatório, retorna erro imediatamente, sem inferir ou preencher.**
- A comunicação com aplicações usa JSON.

## Execução das aplicações

- Execução **síncrona** na V1: a aplicação envia a requisição e espera o JSON final.
  Sem eventos intermediários para a aplicação.
- Cada requisição recebe um `execution_id` único.
- Reenvios e retries manuais sempre geram **novo** `execution_id`.

## Timeout das aplicações

- O timeout é definido pela própria aplicação.
- Ao estourar, o Claudião cancela a execução, registra etapa atual e ferramenta ativa,
  e retorna erro JSON padronizado com HTTP e código interno próprio (ver
  `ERROR_CATALOG.md`).
- A aplicação deve refazer a solicitação como **nova execução**.

## Resposta

Formato de sucesso e de erro seguem o contrato descrito em `ERROR_CATALOG.md`.

## TASKs relacionadas

TASK-067 a TASK-073: API local, validação de payload, execução síncrona, timeout,
erro de timeout, resposta JSON final, rastreio de consumo.
