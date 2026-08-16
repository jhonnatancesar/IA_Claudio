# Fora de escopo (V1 → candidato a V2)

Fonte: seção 49 da especificação mestre.

Os itens abaixo são **explicitamente** deixados de fora da V1 e são candidatos a uma
V2 futura. Nenhum deles deve ser implementado, mesmo parcialmente, durante a execução
das TASKs da V1 — se uma TASK parecer exigir um destes itens, isso é sinal de que o
escopo da TASK está sendo extrapolado.

- System/Automation Tools para execução de comandos e automações locais.
- Retomada de execução interrompida.
- Painel para usuários comuns gerarem suas próprias API keys e acompanharem
  aplicações.
- Planos pagos completos.
- Paralelismo de ferramentas (a V1 executa ferramentas de forma sequencial — ver
  `TOOLS.md`).
- Ferramentas específicas por aplicação (na V1 todas as ferramentas são globais — ver
  `TOOLS.md`).
- Busca semântica/embeddings para memória.
- Possíveis múltiplos runtimes de LLM simultâneos.
- Acesso remoto público.
- HTTPS obrigatório **para o acesso de clientes à API do Claudião** (a V1 usa HTTP
  interno; isso não afeta a exigência, já vigente na V1, de HTTPS para chamadas que o
  Claudião faz a destinos externos — ver `SECURITY.md` e a nota em
  `ARCHITECTURE.md`).

## Relação com o backlog

Nenhuma destas TASKs de 001 a 147 implementa os itens acima. Caso uma V2 seja
planejada, ela deve começar com sua própria numeração de TASKs e seu próprio
documento de escopo, sem misturar com o backlog da V1.
