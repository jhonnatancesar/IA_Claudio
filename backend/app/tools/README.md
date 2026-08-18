# Ferramentas (Tool Registry)

Documentação: docs/TOOLS.md. TASKs: TASK-046, TASK-053, TASK-088 a TASK-100.

Memory Tool, Knowledge Tool, Web Search Tool, File Tool, Database Tool, API Tool. Catálogo fixo, carregado na inicialização, execução sequencial na V1.

- `memory_tool.py` (TASK-046, TASK-047) — `execute_memory_tool(step)`:
  expõe `app.memory.memory_model` (TASK-044/045/047) como ferramenta
  executável pelo orquestrador, assinatura compatível com
  `ExecutionOrchestrator.tool_executor`. `operation` `SAVE`/`LIST`/
  `SEARCH` em `step.parameters`. Cadastro no Tool Registry (catálogo fixo)
  é TASK-088 em diante — não implementado aqui.
- `knowledge_tool.py` (TASK-053) — `execute_knowledge_tool(step)`: expõe
  `app.knowledge.knowledge_model` (TASK-052) como ferramenta executável
  pelo orquestrador, mesmo padrão de `memory_tool.py`. `operation`
  `SAVE`/`GET`/`ADVANCE` em `step.parameters`. `ADVANCE` só aplica a
  transição mecânica de status — a regra de quando promover é TASK-057.

Testes em `tests/unit/test_memory_tool.py` (validação de parâmetros) e
`tests/integration/test_memory_tool_integration.py` (persistência real).
