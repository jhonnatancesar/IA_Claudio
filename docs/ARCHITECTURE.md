# Arquitetura

Fonte: seções 2 a 8 da especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`).

## Princípios fundamentais

### Offline-first

Sem depender de internet, o Claudião deve conseguir: conversar, raciocinar,
interpretar intenção, manter contexto, consultar memória, consultar conhecimento
local, planejar e usar recursos internos.

### Inteligência local

Rodam no modelo local: linguagem natural, interpretação, raciocínio, planejamento,
replanejamento, análise dos resultados das ferramentas e geração da resposta.

### Orquestração controlada

O modelo **não controla livremente o sistema**. Um orquestrador determinístico
controla execução, políticas, limites, cotas, ferramentas, segurança, validação,
confiança, persistência, cancelamento e erros.

## Ambiente da V1

- Máquina única. Hardware ainda não definido: PC ou Orange Pi.
- Sistema operacional de referência: Windows.
- Execução direta no sistema operacional, sem Docker como requisito.
- Serviços iniciam automaticamente com o Windows.
- PostgreSQL na mesma máquina.
- Acesso pela rede local, por nome local em vez de IP digitado.
- HTTP interno na V1; arquitetura preparada para HTTPS e acesso remoto no futuro
  (acesso remoto público fica fora da V1 — ver `OUT_OF_SCOPE.md`). Este HTTP/HTTPS é
  sobre o **acesso de clientes à API do Claudião**; não confundir com a exigência de
  HTTPS para chamadas do Claudião a destinos externos (`SECURITY.md`).

## Configuração central

A configuração do agente vive em um arquivo central de variáveis de ambiente —
exemplo em [`config/.env.example`](../config/.env.example) (TASK-002). Cobre, com
placeholders (sem valores reais versionados — ver `.gitignore`):

- conexão com o PostgreSQL local (`docs/DATABASE.md`);
- caminho da chave mestra de criptografia (`docs/SECURITY.md`);
- runtime de LLM ativo e modelo ativo (`docs/OPEN_QUESTIONS.md`, itens 1 e 3);
- nível de log (`docs/OBSERVABILITY.md`);
- tamanho da janela de contexto e limiar de aviso (`docs/ORCHESTRATOR.md`);
- `max_steps` (`docs/ORCHESTRATOR.md`);
- limite de memória por escopo (`docs/MEMORY.md`);
- ciclo e limiares de cota (`docs/QUOTAS.md`);
- timeout de sessão administrativa (`docs/PANEL.md`);
- janela de atualização noturna (`docs/UPDATER.md`).

O formato exato (variáveis de ambiente vs. arquivo estruturado) e o mecanismo de
carregamento dependem da stack de implementação, ainda não escolhida — ver
`docs/OPEN_QUESTIONS.md`, item 1. Nenhum valor definitivo (modelo ativo, limite de
memória, timeout de sessão) foi atribuído nesta TASK; cada um é decidido na TASK do
bloco funcional correspondente.

## Runtime e modelo local

- Runtime inicial: **Ollama**.
- O núcleo **não** fica acoplado ao Ollama: existe uma abstração `LocalLLMProvider`
  que permite outros runtimes no futuro (ex.: llama.cpp, vLLM).
- Vários modelos podem estar cadastrados, mas apenas **um modelo local fica ativo por
  vez** na V1.
- O modelo ativo pode ser selecionado pelo painel administrativo.
- O modelo definitivo será escolhido por testes, não por chute — nenhuma escolha foi
  feita ainda (ver `OPEN_QUESTIONS.md`).

## Arquitetura de alto nível

```
CLIENTES
├─ Aplicações / API
└─ Chat / Terminal / Web
        │
AUTH / API LAYER
        │
EXECUTION ORCHESTRATOR
├─ Policy Engine
├─ Context Manager
├─ Complexity / Resource Estimator
├─ Planner
├─ Confidence Engine
├─ Guardrails
├─ Queue Manager
├─ Tool Registry
└─ Execution Trace
        │
LOCAL LLM PROVIDER (Ollama na V1)
        │
TOOLS
├─ Memory Tool
├─ Knowledge Tool
├─ Web Search Tool
├─ File Tool
├─ Database Tool
└─ API Tool
        │
PostgreSQL local
```

## Orquestrador

O orquestrador é o núcleo operacional e é determinístico sempre que possível. Ciclo de
uma execução:

1. Recebe requisição.
2. Autentica.
3. Valida entrada.
4. Valida cota e política.
5. Estima complexidade.
6. Carrega contexto necessário.
7. Modelo interpreta o objetivo.
8. Modelo cria plano.
9. Orquestrador valida o plano.
10. Executa uma etapa.
11. Resultado volta para o modelo.
12. Modelo interpreta.
13. Replaneja se necessário.
14. Gera resposta final.

Quando é necessário replanejar, o agente pode descartar o restante do plano anterior e
gerar um plano completo novo, que volta a passar pela validação do orquestrador.

Detalhes de execução (contexto, limites, cancelamento, fila) estão em
`ORCHESTRATOR.md`.

## Protocolo interno

A comunicação entre modelo local e orquestrador é sempre em JSON, um JSON por etapa.
Não há dependência obrigatória de tool calling nativo do modelo.

```json
{
  "execution_id": "uuid",
  "action": "USE_TOOL",
  "tool": "WEB_SEARCH",
  "confidence": "LOW",
  "reason": "Informação atual necessária",
  "parameters": {
    "query": "..."
  }
}
```

## Hierarquia interna de prioridade

1. Segurança e guardrails.
2. Política da execução.
3. Pedido atual do usuário/aplicação.
4. Contexto imediato.
5. Memória persistente.
6. Conhecimento confirmado.
7. Conhecimento provisório.
8. Conhecimento interno do modelo.

## Chat e identidade

- Nome do agente: **Claudião**, com identidade própria visível no chat.
- Personalidade fixa; o tom acompanha naturalmente o contexto. A personalidade do chat
  não interfere nas chamadas de aplicações.
- Entende PT-BR e inglês, mas responde sempre em PT-BR.
- V1: chat simples via terminal/prompt primeiro; depois interface web local com texto,
  streaming, estados resumidos, indicação de uso de ferramentas e fontes. Sem upload
  de arquivos no chat da V1.

## Histórico de conversa

- Persistido por `user_id` e `conversation_id`.
- Conversas antigas podem ser consultadas.
- Ao retomar, usa resumo persistente e contexto recente necessário — não carrega o
  histórico inteiro.
- Resumo atualizado automaticamente em pontos de controle, não a cada mensagem.
