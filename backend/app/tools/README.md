# Ferramentas (Tool Registry)

Documentação: docs/TOOLS.md. TASKs: TASK-046, TASK-053, TASK-054, TASK-055, TASK-088 a TASK-100.

Memory Tool, Knowledge Tool, Web Search Tool, File Tool, Database Tool, API Tool. Catálogo fixo, carregado na inicialização, execução sequencial na V1.

- `memory_tool.py` (TASK-046, TASK-047) — `execute_memory_tool(step)`:
  expõe `app.memory.memory_model` (TASK-044/045/047) como ferramenta
  executável pelo orquestrador, assinatura compatível com
  `ExecutionOrchestrator.tool_executor`. `operation` `SAVE`/`LIST`/
  `SEARCH` em `step.parameters`. Cadastro no Tool Registry (catálogo fixo)
  é TASK-088 em diante — não implementado aqui.
- `knowledge_tool.py` (TASK-053, TASK-054, TASK-055) —
  `execute_knowledge_tool(step)`: expõe `app.knowledge.knowledge_model`
  (TASK-052/054/055) como ferramenta executável pelo orquestrador, mesmo
  padrão de `memory_tool.py`. `operation`
  `SAVE`/`GET`/`ADVANCE`/`NEW_VERSION`/`LIST_SCOPE` em `step.parameters`.
  `ADVANCE` só aplica a transição mecânica de status — a regra de quando
  promover é TASK-057. `NEW_VERSION` cria uma versão nova do fato
  (`create_new_version`). `SAVE` aceita `scope_type`/`scope_id`
  opcionais; `LIST_SCOPE` lista o conhecimento atual de um escopo
  (`list_knowledge_for_scope`).

Testes em `tests/unit/test_memory_tool.py`/`tests/unit/test_knowledge_tool.py`
(validação de parâmetros) e
`tests/integration/test_memory_tool_integration.py`/
`tests/integration/test_knowledge_tool_integration.py` (persistência real).
