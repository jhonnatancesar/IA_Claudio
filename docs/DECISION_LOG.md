# Decision Log

Registro **append-only** de decisões tomadas depois da especificação mestre. Nunca
reescrever uma entrada existente — se uma decisão muda, registra-se uma nova entrada
que referencia a anterior. Decisões já presentes na especificação mestre
(`Claudiao_Especificacao_Arquitetura_e_TASKs.docx`) não precisam de entrada aqui; este
log é para o que foi decidido **depois** dela, durante a organização e execução do
projeto.

---

## DEC-001 — Separação total do AIShoppingAgent

**Data:** 2026-08-16

O Claudião é um repositório novo e independente. O AIShoppingAgent
(`C:\AIShoppingAgent\AIShoppingAgent`) foi inspecionado **somente** como referência de
organização de repositório (estrutura de pastas, padrão de documentação, formato de
TASK, ADR/RFC, decision log, backlog/roadmap). Nenhum código, dependência, regra de
negócio ou TASK funcional daquele projeto foi copiado.

## DEC-002 — Raiz do repositório

**Data:** 2026-08-16

O repositório do Claudião foi organizado diretamente em `C:\IA` (diretório de trabalho
fornecido), em vez de criar um subdiretório próprio. `C:\IA` passa a ser a raiz do
projeto.

## DEC-003 — Escopo formal de TASK-001 e critério de conclusão

**Data:** 2026-08-16

A "TASK-001 — Inicializar estrutura do projeto Claudião" tem como escopo formal:
criar a estrutura mínima de diretórios do repositório, inicializar o controle de
versão (Git) e registrar um commit inicial da organização — conforme descrito na
seção "Ponto de partida manual" da especificação mestre. Isso é distinto de
"implementação funcional": é organização estrutural, o mesmo tipo de trabalho
autorizado nesta sessão.

Critério de conclusão: estrutura de diretórios criada, `.gitignore` presente, `git
init` executado e primeiro commit registrado. Se todos esses itens forem realmente
satisfeitos ao final desta sessão de organização, TASK-001 é marcada como concluída
em `docs/tasks/TASK-001.md` e `docs/tasks/README.md`; caso contrário, permanece
pendente com o que falta explicitado.

## DEC-004 — Stack de implementação não escolhida nesta fase

**Data:** 2026-08-16

Linguagem, framework web, ORM e ferramenta de migration não foram escolhidos nesta
organização, porque a especificação mestre não define essa decisão. Ver
`docs/OPEN_QUESTIONS.md`. O esqueleto de código em `backend/`, `frontend/`, `tests/`
e `config/` foi criado de forma agnóstica de linguagem (diretórios com `README.md`
explicando o propósito de cada módulo), para não travar essa decisão futura.

## DEC-005 — Linguagem do backend: Python

**Data:** 2026-08-16

A TASK-005 (logging local) é a primeira TASK que exige código de aplicação real —
não dá para prosseguir sem escolher linguagem (ver DEC-004/`docs/OPEN_QUESTIONS.md`,
item 1). O usuário escolheu **Python** entre as opções apresentadas (Python, Node.js/
TypeScript, Go), pela maturidade do ecossistema de IA local (SDK oficial do Ollama)
e por bibliotecas de logging rotativo na própria biblioteca padrão.

Escopo desta decisão: só a **linguagem**. Framework web, ORM e ferramenta de
migration continuam em aberto — cada um é decidido quando a TASK que precisar dele
chegar (ex.: TASK-067, API local). `requires-python >= 3.11` em
`backend/pyproject.toml`; a máquina de desenvolvimento atual tem Python 3.14.6, mas
o mínimo é deliberadamente mais baixo para não travar em uma versão tão recente.

## DEC-006 — Driver de PostgreSQL: psycopg 3

**Data:** 2026-08-16

A TASK-006 (logging estruturado no PostgreSQL) exigiu a primeira dependência
externa do backend Python. Escolhido `psycopg[binary]` (psycopg 3), driver oficial
recomendado pelo próprio projeto PostgreSQL para Python — sem alternativa razoável
para essa necessidade pontual (conexão direta, sem ORM). Não decidida sem aviso: ao
contrário da escolha de linguagem (DEC-005), essa é uma decisão técnica de baixo
risco, quase inevitável uma vez que a linguagem é Python e a persistência é
PostgreSQL (`docs/DATABASE.md`) — registrada aqui por transparência, sem pausar
para confirmação prévia. Não é uma escolha de ORM (isso continua em aberto,
`docs/OPEN_QUESTIONS.md`, item 1) — psycopg é usado aqui só como driver raw (SQL
direto), como já vinha sendo feito nas migrations (TASK-003/TASK-004).

## DEC-007 — Biblioteca de criptografia: `cryptography` (Fernet)

**Data:** 2026-08-16

A TASK-012 (criptografia de segredos em repouso) exigiu escolher uma biblioteca
de criptografia simétrica. Escolhido o pacote `cryptography` — padrão de fato
do ecossistema Python para isso, mantido pela Python Cryptographic Authority —
usando sua abstração de alto nível `Fernet` (AES-128-CBC + HMAC-SHA256
autenticado). Mesma categoria de decisão que DEC-006: técnica, de baixo risco,
sem alternativa razoável (reimplementar AEAD na mão seria pior, não melhor, e
não há motivo para preferir outra lib) — registrada aqui por transparência, sem
pausar para confirmação prévia. Não decide de onde vem a chave mestra (isso é
TASK-013).

## DEC-008 — Ollama instalado localmente; SDK oficial `ollama`

**Data:** 2026-08-16

A TASK-015 (implementar `OllamaProvider`) pediu confirmação explícita do
usuário (não é uma decisão técnica de baixo risco como DEC-006/DEC-007, porque
envolve instalar software novo no sistema, não só uma biblioteca Python): o
usuário escolheu instalar o runtime **Ollama** de verdade nesta máquina (via
`winget install Ollama.Ollama`, serviço rodando em `http://localhost:11434`),
em vez de só implementar contra mocks. Nenhum modelo foi baixado — isso
continua em aberto (`docs/OPEN_QUESTIONS.md`, item 3).

Para o código do provider, escolhido o **SDK oficial `ollama`** (pacote
`ollama` no PyPI, mantido pela Ollama Inc.) em vez de chamadas HTTP manuais —
mesma categoria de DEC-006/DEC-007: técnica, de baixo risco, sem alternativa
melhor (reimplementar o cliente HTTP à mão não traria vantagem), registrada
por transparência.

## DEC-009 — Framework web: FastAPI

**Data:** 2026-08-19

A TASK-067 (criar API local do Claudião) é o ponto identificado em
`docs/OPEN_QUESTIONS.md` (item 1) onde o framework web precisava ser
escolhido — pedido explicitamente ao usuário via pergunta de múltipla
escolha (não é decisão técnica de baixo risco como DEC-006/007: define a
camada de entrada de todas as aplicações externas). O usuário escolheu
**FastAPI** (com `uvicorn` como servidor ASGI) entre as opções
apresentadas (FastAPI, Flask, só `http.server` da biblioteca padrão) —
tipagem via Pydantic, validação de payload nativa (aproveitada a partir
da TASK-068), documentação automática. Dependências novas: `fastapi` e
`uvicorn` (`backend/pyproject.toml`).

`docs/OPEN_QUESTIONS.md`, item 1, atualizado para refletir a resolução.

## DEC-010 — Persistir Execution Trace no PostgreSQL

**Data:** 2026-08-21

A TASK-082 ("mostrar execuções no painel") esbarrou num ponto que a
especificação mestre não decide: ao contrário da fila ("A V1 tem fila
FIFO **persistida no PostgreSQL**" — texto explícito, seção 27), a seção
que descreve o Execution Trace (35/44) nunca diz que ele deve ser
persistido — e, de fato, `ExecutionTrace` (TASK-078/079) só existe
durante a duração de uma requisição HTTP, nunca gravado em lugar nenhum.
Sem persistência, o painel não tem como mostrar execuções passadas.

Pedido explicitamente ao usuário via pergunta de múltipla escolha (não é
decisão técnica de baixo risco: cria uma tabela nova e passa a gravar
dado a cada execução, decisão de arquitetura fora do que a especificação
mestre define). Duas opções apresentadas: (a) reaproveitar
`usage_records` (TASK-073), já persistido, sem tabela nova, mas só com
`execution_id`/`status`/`quando`/aplicação — sem objetivo, resultado,
etapas ou duração; (b) persistir o `ExecutionTrace` inteiro numa tabela
nova. O usuário escolheu **(b)** — persistir o Execution Trace numa
tabela nova (`execution_traces`), para um painel mais rico (objetivo,
resultado, duração, número de etapas, ferramentas usadas).

## DEC-011 — Primeiro modelo Ollama baixado: `qwen3:8b` (provisório)

**Data:** 2026-08-21

A TASK-087 (marco do primeiro Claudião utilizável) exigia validar o
fluxo completo com uma resposta real de modelo, não só com
`LocalLLMProvider` fake (como todos os testes até aqui). Isso esbarrou
em `docs/OPEN_QUESTIONS.md`, item 3 ("o modelo definitivo será escolhido
por testes, não por chute") — nenhum modelo havia sido baixado.

Pedido explicitamente ao usuário via pergunta de múltipla escolha (não é
decisão técnica de baixo risco: baixar ~5GB e escolher, mesmo que
provisoriamente, qual modelo o `CLAUDIAO_ACTIVE_MODEL` aponta). Duas
opções apresentadas: (a) certificar o marco sem modelo real, validando
só até a fronteira do `LocalLLMProvider`; (b) baixar um modelo agora
para validar com resposta real. O usuário escolheu **(b)**, e ao ser
perguntado qual modelo baixar, escolheu explicitamente **`qwen3:8b`**
(maior que as opções sugeridas de referência, `llama3.2:3b/1b` ou
`qwen2.5:3b`).

Executado `ollama pull qwen3:8b` (5.2GB) e configurado
`CLAUDIAO_ACTIVE_MODEL=qwen3:8b` em `config/.env` (não versionado). Esta
é uma escolha **provisória**, não a decisão definitiva de modelo — a
especificação mestre é explícita que a escolha definitiva vem de testes
sistemáticos, não desta validação pontual. `docs/OPEN_QUESTIONS.md`,
item 3, atualizado para refletir isso sem marcar como resolvido.

## DEC-012 — Primeiro provider de busca: SearXNG local via Docker

**Data:** 2026-08-21

A TASK-089 ("implementar primeiro provider de busca") exigia escolher um
fornecedor real por trás de `WebSearchProvider` (TASK-088) —
`docs/TOOLS.md` deixa a abstração genérica, mas a implementação concreta
precisa de um serviço de verdade. Pedido ao usuário via `AskUserQuestion`,
com quatro opções apresentadas na primeira pergunta: DuckDuckGo (sem API
key), Brave Search API, Google Custom Search JSON API, ou outro. O usuário
escolheu DuckDuckGo.

Antes de implementar, testado de verdade contra o DuckDuckGo: o endpoint
de scraping HTML (`html.duckduckgo.com/html/`) retornou uma página de
desafio anti-bot (`anomaly.js`) em vez de resultados — contornar isso
seria bypass de bot-detection, fora de cogitação por regra de segurança
não negociável. A alternativa oficial sem key, a "Instant Answer API"
(`api.duckduckgo.com`), não tem esse bloqueio, mas devolveu vazio para
três queries genéricas reais testadas ("melhor receita de bolo de
chocolate", "notícias de hoje sobre economia brasil", "claudião agente
ia") — só funciona bem para tópicos tipo enciclopédia (ex.: "python
programming language" retorna um resumo da Wikipédia).

Achado reportado ao usuário, com uma segunda pergunta: manter DuckDuckGo
mesmo com a limitação, trocar para Brave/Google (API paga/com key), ou
outro. O usuário escolheu **SearXNG local (self-hosted)** — metasearch
engine open-source que agrega vários motores de busca de verdade sem
exigir API key paga de terceiro.

Pedida uma terceira confirmação sobre *como* instalar (esta máquina já
exige aprovação prévia para instalar software novo, prática pedida pelo
usuário desde a TASK-058): instalação nativa sem Docker
(alinhada com `CLAUDE.md`: "execução direta no sistema operacional, sem
Docker como requisito") vs. Docker vs. instância já existente. O usuário
escolheu **Docker**. Docker Desktop já estava instalado nesta máquina
(não instalado nesta TASK, só iniciado — estava parado) — rodado
`docker run -d --name claudiao-searxng -p 8888:8080 -v
"C:\IA\config\searxng:/etc/searxng" ... searxng/searxng:latest`, com
`search.formats: [html, json]` habilitado explicitamente em
`config/searxng/settings.yml` (config gerada pelo container, não
versionada — mesmo princípio de `config/.env`). Validado com buscas reais
antes de implementar o provider: resultados genéricos corretos tanto em
inglês quanto nas mesmas queries em português que tinham falhado no
DuckDuckGo.

Isso é uma exceção pontual ao princípio "sem Docker como requisito" da
arquitetura da V1 (que é sobre o **núcleo** do Claudião — PostgreSQL,
backend — não sobre todo serviço auxiliar de terceiro que ele consome);
o núcleo continua rodando direto no SO. Escolha específica de fornecedor
de busca — não uma mudança de arquitetura do próprio Claudião.
