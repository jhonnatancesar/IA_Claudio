"""Knowledge Tool (TASK-053).

Expõe `app.knowledge.knowledge_model` (TASK-052) como uma ferramenta que
o orquestrador pode executar: traduz os `parameters` de uma etapa
`USE_TOOL` (`ModelStep`, TASK-016) em chamadas a `save_knowledge`/
`get_knowledge`/`advance_knowledge_status` e devolve o resultado como
texto — mesma assinatura que `ExecutionOrchestrator.tool_executor` espera
(`Callable[[ModelStep], str]`, TASK-026), mesmo padrão de
`app.tools.memory_tool` (TASK-046).

O Tool Registry (catálogo fixo de ferramentas, validação de que
`"KNOWLEDGE"` é um nome de ferramenta conhecido/autorizado) é TASK-088 em
diante — esta TASK só cria a função que executa a ferramenta quando
chamada diretamente, sem se cadastrar em lugar nenhum ainda.

A operação `"ADVANCE"` só aplica a transição mecânica de status já
validada por `advance_knowledge_status` — decidir *quando* uma transição
deve acontecer (a regra de promoção baseada em evidências/fontes) é
TASK-057, não desta TASK. Busca/versionamento/escopo/evidências
(TASK-054 a TASK-058) também não são desta TASK.
"""

from __future__ import annotations

from app.knowledge.knowledge_model import (
    KnowledgeStatus,
    advance_knowledge_status,
    get_knowledge,
    save_knowledge,
)
from app.llm.protocol import ModelStep

KNOWLEDGE_TOOL_NAME = "KNOWLEDGE"


class UnknownKnowledgeOperationError(ValueError):
    """Levantado quando `parameters["operation"]` não é `SAVE`, `GET` nem
    `ADVANCE`."""


class MissingToolParameterError(ValueError):
    """Levantado quando falta um parâmetro obrigatório para a operação
    pedida."""


class InvalidKnowledgeStatusParameterError(ValueError):
    """Levantado quando `parameters["new_status"]` não é um valor válido de
    `KnowledgeStatus`."""


def _require(parameters: dict, key: str) -> str:
    value = parameters.get(key)
    if not value:
        raise MissingToolParameterError(f"parâmetro obrigatório ausente: {key}")
    return value


def execute_knowledge_tool(step: ModelStep) -> str:
    """Executa a Knowledge Tool para `step`. `parameters["operation"]`
    decide o que fazer:

    - `"SAVE"`: exige `content`; persiste um conhecimento novo em `RAW`
      (`save_knowledge`) e devolve confirmação com o `id` gerado.
    - `"GET"`: exige `knowledge_id`; devolve o conteúdo e o status do
      conhecimento (`get_knowledge`), ou uma mensagem se não existir.
    - `"ADVANCE"`: exige `knowledge_id`, `new_status`; aplica a transição
      mecânica de status (`advance_knowledge_status`) e devolve
      confirmação com o novo status.

    Levanta `MissingToolParameterError` para parâmetro obrigatório
    ausente, `InvalidKnowledgeStatusParameterError` para `new_status`
    desconhecido e `UnknownKnowledgeOperationError` para `operation`
    diferente de `SAVE`/`GET`/`ADVANCE`.
    """
    operation = _require(step.parameters, "operation")

    if operation == "SAVE":
        content = _require(step.parameters, "content")
        knowledge = save_knowledge(content)
        return f"Conhecimento salvo em RAW (id={knowledge.id})."

    if operation == "GET":
        knowledge_id = _require(step.parameters, "knowledge_id")
        knowledge = get_knowledge(knowledge_id)
        if knowledge is None:
            return "Nenhum conhecimento encontrado para este id."
        return f"[{knowledge.status.value}] {knowledge.content}"

    if operation == "ADVANCE":
        knowledge_id = _require(step.parameters, "knowledge_id")
        new_status_raw = _require(step.parameters, "new_status")
        try:
            new_status = KnowledgeStatus(new_status_raw)
        except ValueError as exc:
            raise InvalidKnowledgeStatusParameterError(
                f"new_status inválido: {new_status_raw!r}"
            ) from exc
        knowledge = advance_knowledge_status(knowledge_id, new_status)
        return f"Conhecimento avançado para {knowledge.status.value} (id={knowledge.id})."

    raise UnknownKnowledgeOperationError(
        f"operação de conhecimento desconhecida: {operation!r}"
    )
