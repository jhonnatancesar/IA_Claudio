# Erros

Documentação: docs/ERROR_CATALOG.md. TASKs: TASK-007, TASK-008.

Catálogo interno de erros e (a partir da TASK-008) o formato de resposta JSON
padrão que os usa. Módulo transversal — não fazia parte da lista original de
componentes esboçados na organização inicial, criado quando a TASK-007 precisou
de um lugar para o código do catálogo.

- `catalog.py` (TASK-007) — `ErrorDomain` (as 9 faixas de 1000 em 1000, seção 36
  da especificação), `ErrorDefinition`, `register_error()`/`get_error()`/
  `domain_for_code()`. Catálogo nasce pequeno: só os erros que a fundação já
  precisa (`MISSING_REQUIRED_FIELD`, `INVALID_FIELD_VALUE`,
  `UNKNOWN_INTERNAL_ERROR`) — cada TASK futura registra os códigos que precisar
  quando chegar sua vez.
- `response.py` (TASK-008) — formato JSON padrão de erro
  (`{"success": false, "error": {...}}`, seção 36 da especificação):
  `build_error_response(definition, details=None)`, `ClaudiaoError` (exceção que
  carrega a definição + details) e `error_response_from_exception()`. Só o
  formato de erro — resposta de sucesso é escopo de outra TASK (TASK-072).

Testes em `tests/unit/test_error_catalog.py` e `tests/unit/test_error_response.py`.
