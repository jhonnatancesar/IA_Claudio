# Dúvidas e pontos em aberto

Pontos que a especificação mestre não resolve, ou que podem gerar confusão, registrados
aqui em vez de decididos silenciosamente. Nenhum destes deve ser resolvido por um
agente sem aprovação explícita do usuário — ver `AGENTS.md`.

## 1. Linguagem/stack de implementação

A especificação mestre define arquitetura, componentes e contratos, mas não escolhe
linguagem de programação, framework web, ORM nem ferramenta de migration para o
PostgreSQL. O AIShoppingAgent usa Python/FastAPI, mas isso é o projeto de referência
de **organização**, não uma decisão de stack herdada automaticamente pelo Claudião
(ver `docs/DECISION_LOG.md`, DEC-001 e DEC-004).

**Status:** aberto. Nenhuma TASK de fundação (TASK-001 a TASK-008) deve escolher a
stack sem essa decisão ser tomada explicitamente pelo usuário primeiro.

## 2. Hardware definitivo

Seção 3 da especificação: "Hardware ainda não definido: PC ou Orange Pi." Isso afeta
decisões de runtime (ex.: viabilidade de rodar certos modelos Ollama) mas não bloqueia
a organização do repositório.

**Status:** aberto, sem impacto na estrutura atual.

## 3. Modelo LLM definitivo

Seção 4: "O modelo definitivo será escolhido por testes, não por chute." Nenhum modelo
foi escolhido, baixado ou testado nesta sessão, por instrução explícita do usuário.

**Status:** aberto, intencionalmente adiado.

## 4. Valor exato do limite fixo de memória por usuário/aplicação

Seção 11.3: "O limite máximo de memória por usuário/aplicação será fixo na V1", mas o
valor numérico não é especificado. Fica para a implementação de TASK-050.

**Status:** aberto, não bloqueante — a definição do valor é parte do escopo de
TASK-050, não uma inconsistência da especificação.

## 5. Duplo sentido de "HTTPS obrigatório" — esclarecido, não é contradição

A especificação usa "HTTPS obrigatório" em dois contextos diferentes:

- Seção 20 (Segurança de APIs): HTTPS obrigatório para **chamadas de saída** do
  Claudião a destinos externos (Web Search Tool, API Tool). Isso já vale na V1.
- Seção 49 (Fora da V1/V2): "HTTPS obrigatório" listado como item futuro, referindo-se
  ao **acesso de entrada** de clientes à API do Claudião — a V1 usa HTTP interno
  (seção 3).

Não há conflito real: são dois perímetros diferentes (saída vs. entrada). Documentado
separadamente em `docs/SECURITY.md` e `docs/ARCHITECTURE.md` para evitar confusão
futura durante a implementação de TASK-096 (política HTTPS do API Tool) e do bloco de
API (TASK-067 em diante).

**Status:** resolvido por leitura cuidadosa da especificação; registrado aqui apenas
para rastreabilidade, sem necessidade de decisão do usuário.

## Como adicionar um novo item

Ao encontrar uma nova ambiguidade ou decisão impossível durante uma TASK: adicionar
uma seção numerada aqui, com o trecho da especificação envolvido, por que é ambíguo/
impossível, e o que está bloqueado até a resposta do usuário. Não remover itens
resolvidos — marcar como "resolvido" e manter o histórico.
