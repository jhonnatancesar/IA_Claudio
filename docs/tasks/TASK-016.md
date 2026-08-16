# TASK-016 — Criar protocolo JSON modelo ↔ orquestrador

Status: **Concluída em 2026-08-16**

## Objetivo

Criar protocolo JSON modelo ↔ orquestrador, conforme a especificação mestre (`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`, bloco "LLM") e `docs/ARCHITECTURE.md`.

## Escopo

Implementar exatamente o objetivo declarado acima, dentro do bloco funcional "LLM" (ver docs/BACKLOG.md e docs/ROADMAP.md), conforme AGENTS.md, CLAUDE.md e `docs/ARCHITECTURE.md`. Nenhuma funcionalidade de TASK posterior deve ser adiantada.

## Fora de escopo

Qualquer item de TASK posterior no backlog (docs/BACKLOG.md); qualquer item listado em docs/OUT_OF_SCOPE.md; qualquer decisão de arquitetura não presente na especificação mestre ou em docs/DECISION_LOG.md.

## Dependências

TASK-015 concluída.

## Critérios de aceite

Objetivo declarado implementado e verificável; testes esperados (abaixo) escritos e aprovados; `docs/ARCHITECTURE.md` e `docs/tasks/README.md` atualizados; nenhuma regra ou decisão já aprovada foi alterada silenciosamente.

## Testes esperados

Testes unitários do provider e do protocolo JSON (parser/validator contra JSON malformado ou fora do contrato), conforme docs/TESTING.md.

## Documentação afetada

`docs/ARCHITECTURE.md`, `docs/tasks/README.md`, `backend/app/llm/README.md`

## Encerramento

Concluída em 2026-08-16. Criado `backend/app/llm/protocol.py`: `Action`
(`USE_TOOL`/`RESPOND` — conjunto mínimo sustentado pela especificação),
`Confidence` (`LOW`/`MEDIUM`/`HIGH`, reaproveitável por TASK-031/TASK-033),
`ModelStep` (dataclass com `to_dict()`/`to_json()`/`from_dict()`/`from_json()`)
e `ProtocolDecodeError`. Round-trip verificado contra o exemplo exato da
seção 7 da especificação mestre. 13 testes unitários novos (round-trip, campos
obrigatórios ausentes um a um, action/confidence inválidas, `USE_TOOL` sem
`tool`, entrada não-objeto, JSON malformado). Suíte completa: 116/116 testes
aprovados. Validação mais profunda contra entrada adversarial fica para a
TASK-017.
