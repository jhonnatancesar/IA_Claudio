# Configuração

Configuração central do agente (TASK-002) e exemplos de variáveis de ambiente.

- Segredos e configuração local nunca são versionados (ver `.gitignore`) — apenas
  arquivos `*.example` ficam no Git.
- A chave mestra de criptografia (`docs/SECURITY.md`) fica fora do PostgreSQL, em
  variável de ambiente ou arquivo protegido na máquina — nunca neste diretório
  versionado.

Nenhum arquivo de configuração real foi criado ainda; ver `docs/tasks/TASK-002.md`.
