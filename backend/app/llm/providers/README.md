# Providers de LLM local

Documentação: docs/ARCHITECTURE.md. TASKs: TASK-015.

Implementações concretas de LocalLLMProvider. A V1 traz apenas OllamaProvider; outros runtimes (llama.cpp, vLLM) ficam preparados pela abstração, não implementados agora. Apenas um modelo local fica ativo por vez na V1.

Nenhum código foi criado neste módulo ainda — este README existe apenas para manter
o diretório versionado e documentar seu propósito antes da implementação (ver
AGENTS.md e docs/OPEN_QUESTIONS.md sobre a stack de implementação).
