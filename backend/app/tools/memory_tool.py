"""Memory Tool (TASK-046).

Expõe `app.memory.memory_model` (TASK-044/TASK-045) como uma ferramenta que
o orquestrador pode executar: traduz os `parameters` de uma etapa
`USE_TOOL` (`ModelStep`, TASK-016) em chamadas a `save_memory`/
`list_memories_for_owner` e devolve o resultado como texto — mesma
assinatura que `ExecutionOrchestrator.tool_executor` espera
(`Callable[[ModelStep], str]`, TASK-026).

O Tool Registry (catálogo fixo de ferramentas, validação de que `"MEMORY"`
é um nome de ferramenta conhecido/autorizado) é TASK-088 em diante — esta
TASK só cria a função que executa a ferramenta quando chamada diretamente,
sem se cadastrar em lugar nenhum ainda.

TASK-047 acrescenta a operação `"SEARCH"`, expondo `search_memories`
(busca estruturada por conteúdo, dentro do escopo do dono). Ranking por
relevância (TASK-048) não é desta TASK.
"""

from __future__ import annotations

from app.llm.protocol import ModelStep
from app.memory.memory_model import list_memories_for_owner, save_memory, search_memories

MEMORY_TOOL_NAME = "MEMORY"


class UnknownMemoryOperationError(ValueError):
    """Levantado quando `parameters["operation"]` não é `SAVE` nem `LIST`."""


class MissingToolParameterError(ValueError):
    """Levantado quando falta um parâmetro obrigatório para a operação
    pedida."""


def _require(parameters: dict, key: str) -> str:
    value = parameters.get(key)
    if not value:
        raise MissingToolParameterError(f"parâmetro obrigatório ausente: {key}")
    return value


def execute_memory_tool(step: ModelStep) -> str:
    """Executa a Memory Tool para `step`. `parameters["operation"]` decide o
    que fazer:

    - `"SAVE"`: exige `owner_type`, `owner_id`, `content`; persiste uma
      memória nova (`save_memory`) e devolve confirmação com o `id` gerado.
    - `"LIST"`: exige `owner_type`, `owner_id`; devolve todas as memórias
      desse dono (`list_memories_for_owner`), uma por linha.
    - `"SEARCH"`: exige `owner_type`, `owner_id`, `query`; devolve as
      memórias desse dono cujo conteúdo contém `query`
      (`search_memories`, TASK-047), uma por linha.

    Levanta `MissingToolParameterError` para parâmetro obrigatório ausente
    e `UnknownMemoryOperationError` para `operation` diferente de `SAVE`/
    `LIST`/`SEARCH`.
    """
    operation = _require(step.parameters, "operation")

    if operation == "SAVE":
        owner_type = _require(step.parameters, "owner_type")
        owner_id = _require(step.parameters, "owner_id")
        content = _require(step.parameters, "content")
        memory = save_memory(owner_type, owner_id, content)
        return f"Memória salva (id={memory.id})."

    if operation == "LIST":
        owner_type = _require(step.parameters, "owner_type")
        owner_id = _require(step.parameters, "owner_id")
        memories = list_memories_for_owner(owner_type, owner_id)
        if not memories:
            return "Nenhuma memória encontrada para este dono."
        return "\n".join(f"- {memory.content}" for memory in memories)

    if operation == "SEARCH":
        owner_type = _require(step.parameters, "owner_type")
        owner_id = _require(step.parameters, "owner_id")
        query = _require(step.parameters, "query")
        memories = search_memories(owner_type, owner_id, query)
        if not memories:
            return "Nenhuma memória encontrada para esta busca."
        return "\n".join(f"- {memory.content}" for memory in memories)

    raise UnknownMemoryOperationError(f"operação de memória desconhecida: {operation!r}")
