# Visão geral do produto

Fonte: seção 1 da especificação mestre.

## Objetivo formal

Criar um agente inteligente **genérico, local e reutilizável**, chamado **Claudião**,
cujo raciocínio principal rode no próprio servidor, sem depender de OpenAI, Gemini,
Claude, Groq, OpenRouter ou outra IA externa para pensar normalmente.

```
USUÁRIO / APLICAÇÃO
        │
     CLAUDIÃO
        │
entende contexto/intenção
        │
     planeja
        │
     consegue?
    ├─ SIM → responde/age localmente
    └─ NÃO → usa ferramenta → recebe dados → interpreta LOCALMENTE → continua o raciocínio
```

Internet, APIs, outros agentes e integrações são **ferramentas**. Não são fallback de
inteligência — o Claudião nunca terceiriza o próprio raciocínio para uma IA externa
quando não sabe algo; ele usa uma ferramenta, interpreta o resultado localmente e
continua raciocinando com o modelo local.

## O que faz o Claudião diferente de "um chatbot com plugins"

- O modelo local decide **quando** usar uma ferramenta, mas o orquestrador
  determinístico decide **se pode**, valida o plano, aplica políticas/cotas/guardrails
  e registra tudo em um `Execution Trace`.
- Conhecimento aprendido é versionado e passa por um ciclo de maturidade
  (RAW → PROVISIONAL → CONFIRMED) antes de ser tratado como fato confiável — ver
  `KNOWLEDGE.md`.
- Toda conclusão carrega um nível de confiança (LOW/MEDIUM/HIGH) e, quando aplicável,
  uma marca de volatilidade — ver `TRUST_GUARDRAILS.md`.
- O mesmo núcleo atende tanto conversas de chat quanto chamadas de aplicações
  externas via API, com políticas de pesquisa diferentes para cada caso.

## Para quem serve

- **Aplicações**, que chamam o Claudião via API com uma política de execução própria
  (contexto, permissões de pesquisa, timeout, limites) — prioridade da V1.
- **Usuários humanos**, via chat (terminal na V1, web depois do marco TASK-087).

## Não-objetivos explícitos

Ver `OUT_OF_SCOPE.md` para a lista completa de itens deliberadamente fora da V1/V2.
