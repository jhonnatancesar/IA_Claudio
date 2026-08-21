# Configuração

Configuração central do agente (TASK-002) e exemplos de variáveis de ambiente.

- Segredos e configuração local nunca são versionados (ver `.gitignore`) — apenas
  arquivos `*.example` ficam no Git.
- A chave mestra de criptografia (`docs/SECURITY.md`) fica fora do PostgreSQL, em
  variável de ambiente ou arquivo protegido na máquina — nunca neste diretório
  versionado.

`config/.env` (variáveis do PostgreSQL/chave mestra/modelo ativo, TASK-003
em diante) e `config/master.key` (TASK-013) já existem localmente — não
versionados. `config/searxng/` (TASK-089) segue o mesmo princípio: config
gerada automaticamente pelo container Docker do SearXNG local
(`docker run ... searxng/searxng`), com uma `secret_key` própria da
instância — não versionada.
