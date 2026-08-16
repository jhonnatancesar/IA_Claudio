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
