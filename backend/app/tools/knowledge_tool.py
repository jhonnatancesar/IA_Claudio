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
TASK-057, não desta TASK.

TASK-054 acrescenta `"NEW_VERSION"`, expondo `create_new_version`: cria
uma versão nova de um fato sem apagar a anterior.

TASK-055 acrescenta `scope_type`/`scope_id` opcionais em `"SAVE"` e a
operação `"LIST_SCOPE"`, expondo `list_knowledge_for_scope`.

TASK-056 acrescenta `"SET_CONFIDENCE"`/`"SET_VOLATILITY"` (expondo
`set_knowledge_confidence`/`set_knowledge_volatility`) e
`"ADD_EVIDENCE"`/`"LIST_EVIDENCE"` (expondo `add_evidence`/
`list_evidence`) — evidências como texto livre; vincular a uma fonte
cadastrada de verdade é TASK-059 em diante.
"""

from __future__ import annotations

from app.confidence.volatility import Volatility
from app.knowledge.knowledge_model import (
    KnowledgeScope,
    KnowledgeStatus,
    add_evidence,
    advance_knowledge_status,
    create_new_version,
    get_knowledge,
    list_evidence,
    list_knowledge_for_scope,
    save_knowledge,
    set_knowledge_confidence,
    set_knowledge_volatility,
)
from app.llm.protocol import Confidence, ModelStep

KNOWLEDGE_TOOL_NAME = "KNOWLEDGE"


class UnknownKnowledgeOperationError(ValueError):
    """Levantado quando `parameters["operation"]` não é uma das operações
    conhecidas (`SAVE`, `GET`, `ADVANCE`, `NEW_VERSION`, `LIST_SCOPE`,
    `SET_CONFIDENCE`, `SET_VOLATILITY`, `ADD_EVIDENCE`,
    `LIST_EVIDENCE`)."""


class MissingToolParameterError(ValueError):
    """Levantado quando falta um parâmetro obrigatório para a operação
    pedida."""


class InvalidKnowledgeStatusParameterError(ValueError):
    """Levantado quando `parameters["new_status"]` não é um valor válido de
    `KnowledgeStatus`."""


class InvalidKnowledgeScopeParameterError(ValueError):
    """Levantado quando `parameters["scope_type"]` não é um valor válido de
    `KnowledgeScope`."""


class InvalidConfidenceParameterError(ValueError):
    """Levantado quando `parameters["confidence"]` não é um valor válido
    de `Confidence`."""


class InvalidVolatilityParameterError(ValueError):
    """Levantado quando `parameters["volatility"]` não é um valor válido
    de `Volatility`."""


def _require(parameters: dict, key: str) -> str:
    value = parameters.get(key)
    if not value:
        raise MissingToolParameterError(f"parâmetro obrigatório ausente: {key}")
    return value


def execute_knowledge_tool(step: ModelStep) -> str:
    """Executa a Knowledge Tool para `step`. `parameters["operation"]`
    decide o que fazer:

    - `"SAVE"`: exige `content`; aceita `scope_type`/`scope_id` opcionais
      (padrão `GLOBAL`); persiste um conhecimento novo em `RAW`
      (`save_knowledge`) e devolve confirmação com o `id` gerado.
    - `"GET"`: exige `knowledge_id`; devolve o conteúdo e o status do
      conhecimento (`get_knowledge`), ou uma mensagem se não existir.
    - `"ADVANCE"`: exige `knowledge_id`, `new_status`; aplica a transição
      mecânica de status (`advance_knowledge_status`) e devolve
      confirmação com o novo status.
    - `"NEW_VERSION"`: exige `knowledge_id` (a versão atual da linhagem),
      `new_content`, `reason`; cria uma versão nova (`create_new_version`)
      e devolve confirmação com o `id`/número da nova versão.
    - `"LIST_SCOPE"`: exige `scope_type` (`GLOBAL` ou `APPLICATION`;
      `APPLICATION` exige também `scope_id`); devolve os conhecimentos
      atuais desse escopo (`list_knowledge_for_scope`), um por linha.
    - `"SET_CONFIDENCE"`: exige `knowledge_id`, `confidence`
      (`LOW`/`MEDIUM`/`HIGH`); define a confiança
      (`set_knowledge_confidence`) e devolve confirmação.
    - `"SET_VOLATILITY"`: exige `knowledge_id`, `volatility`
      (`VOLATILE`/`NON_VOLATILE`); define a volatilidade
      (`set_knowledge_volatility`) e devolve confirmação.
    - `"ADD_EVIDENCE"`: exige `knowledge_id`, `description`; registra uma
      evidência (`add_evidence`) e devolve confirmação com o `id` gerado.
    - `"LIST_EVIDENCE"`: exige `knowledge_id`; devolve as evidências
      registradas (`list_evidence`), uma por linha.

    Levanta `MissingToolParameterError` para parâmetro obrigatório
    ausente, `InvalidKnowledgeStatusParameterError`/
    `InvalidKnowledgeScopeParameterError`/`InvalidConfidenceParameterError`/
    `InvalidVolatilityParameterError` para valores desconhecidos de
    `new_status`/`scope_type`/`confidence`/`volatility`, e
    `UnknownKnowledgeOperationError` para `operation` desconhecida.
    """
    operation = _require(step.parameters, "operation")

    if operation == "SAVE":
        content = _require(step.parameters, "content")
        scope_type_raw = step.parameters.get("scope_type", KnowledgeScope.GLOBAL.value)
        try:
            scope_type = KnowledgeScope(scope_type_raw)
        except ValueError as exc:
            raise InvalidKnowledgeScopeParameterError(
                f"scope_type inválido: {scope_type_raw!r}"
            ) from exc
        scope_id = step.parameters.get("scope_id")
        knowledge = save_knowledge(content, scope_type=scope_type, scope_id=scope_id)
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

    if operation == "NEW_VERSION":
        knowledge_id = _require(step.parameters, "knowledge_id")
        new_content = _require(step.parameters, "new_content")
        reason = _require(step.parameters, "reason")
        knowledge = create_new_version(knowledge_id, new_content, reason)
        return (
            f"Nova versão criada: v{knowledge.version} (id={knowledge.id})."
        )

    if operation == "LIST_SCOPE":
        scope_type_raw = _require(step.parameters, "scope_type")
        try:
            scope_type = KnowledgeScope(scope_type_raw)
        except ValueError as exc:
            raise InvalidKnowledgeScopeParameterError(
                f"scope_type inválido: {scope_type_raw!r}"
            ) from exc
        scope_id = step.parameters.get("scope_id")
        knowledge_list = list_knowledge_for_scope(scope_type, scope_id)
        if not knowledge_list:
            return "Nenhum conhecimento encontrado para este escopo."
        return "\n".join(f"- [{k.status.value}] {k.content}" for k in knowledge_list)

    if operation == "SET_CONFIDENCE":
        knowledge_id = _require(step.parameters, "knowledge_id")
        confidence_raw = _require(step.parameters, "confidence")
        try:
            confidence = Confidence(confidence_raw)
        except ValueError as exc:
            raise InvalidConfidenceParameterError(
                f"confidence inválida: {confidence_raw!r}"
            ) from exc
        knowledge = set_knowledge_confidence(knowledge_id, confidence)
        return f"Confiança definida como {knowledge.confidence.value} (id={knowledge.id})."

    if operation == "SET_VOLATILITY":
        knowledge_id = _require(step.parameters, "knowledge_id")
        volatility_raw = _require(step.parameters, "volatility")
        try:
            volatility = Volatility(volatility_raw)
        except ValueError as exc:
            raise InvalidVolatilityParameterError(
                f"volatility inválida: {volatility_raw!r}"
            ) from exc
        knowledge = set_knowledge_volatility(knowledge_id, volatility)
        return f"Volatilidade definida como {knowledge.volatility.value} (id={knowledge.id})."

    if operation == "ADD_EVIDENCE":
        knowledge_id = _require(step.parameters, "knowledge_id")
        description = _require(step.parameters, "description")
        evidence = add_evidence(knowledge_id, description)
        return f"Evidência registrada (id={evidence.id})."

    if operation == "LIST_EVIDENCE":
        knowledge_id = _require(step.parameters, "knowledge_id")
        evidence_list = list_evidence(knowledge_id)
        if not evidence_list:
            return "Nenhuma evidência encontrada para este conhecimento."
        return "\n".join(f"- {evidence.description}" for evidence in evidence_list)

    raise UnknownKnowledgeOperationError(
        f"operação de conhecimento desconhecida: {operation!r}"
    )
