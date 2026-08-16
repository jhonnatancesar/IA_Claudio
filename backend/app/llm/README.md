# LLM — abstração de raciocínio local

Documentação: docs/ARCHITECTURE.md. TASKs: TASK-014, TASK-016 a TASK-019.

Interface LocalLLMProvider, protocolo JSON modelo ↔ orquestrador, validação dos JSONs internos, prompt-base e composição dinâmica de prompt/contexto. Ollama é apenas o runtime inicial (ver llm/providers/).

Nenhum código foi criado neste módulo ainda — este README existe apenas para manter
o diretório versionado e documentar seu propósito antes da implementação (ver
AGENTS.md e docs/OPEN_QUESTIONS.md sobre a stack de implementação).
