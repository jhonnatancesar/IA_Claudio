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
