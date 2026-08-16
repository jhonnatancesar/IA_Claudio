"""Configuração compartilhada de testes: garante que `backend/app` seja importável
como pacote `app`, sem precisar instalar o projeto (docs/TESTING.md)."""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
