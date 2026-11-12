"""A API do kit servindo os resultados depois da revisão da cronometragem.

    python3 api_revisada.py

É o servidor.py da pasta api/ do kit, com a mesma porta (8765) e o mesmo token, servindo
revisada/api_resultados.json no lugar dos dados do triatlo. Pare a API normal antes de subir esta.
Aceita as mesmas opções do servidor.py, como --falhas.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "api"))
import servidor  # noqa: E402  (o servidor.py da pasta api/ do kit)

if __name__ == "__main__":
    sys.argv[1:1] = ["--pasta", str(AQUI / "revisada")]
    servidor.main()
