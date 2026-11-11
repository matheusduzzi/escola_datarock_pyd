"""Configuração: o que muda de uma execução para outra e de uma máquina para outra.

- O período muda a cada execução: vem do comando (--inicio, --fim).
- As pastas mudam de uma máquina para outra: vêm do ambiente, ou do arquivo .env.
- As regras do relatório não mudam: ficam em transformacao.py.
"""
import argparse
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

RAIZ = Path(__file__).resolve().parent.parent
MES = re.compile(r"\d{4}-\d{2}")


@dataclass(frozen=True)
class Config:
    inicio: str
    fim: str
    pasta_dados: Path
    pasta_saida: Path
    token_api: str = field(default="", repr=False)


def caminho(valor):
    """Caminho relativo parte da pasta do projeto, não da pasta em que o terminal está."""
    p = Path(valor).expanduser()
    return p if p.is_absolute() else (RAIZ / p).resolve()


def ler(argumentos=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m entregas",
        description="Pedidos entregues e faturamento por cidade, num período de meses.")
    parser.add_argument("--inicio", required=True, help="primeiro mês, AAAA-MM")
    parser.add_argument("--fim", required=True, help="último mês, AAAA-MM")
    parser.add_argument("--mostrar-config", action="store_true",
                        help="mostra a configuração que vai ser usada e para")
    args = parser.parse_args(argumentos)
    for nome in ("inicio", "fim"):
        if not MES.fullmatch(getattr(args, nome)):
            parser.error(f"--{nome} precisa ser AAAA-MM, por exemplo 2026-04")
    if args.inicio > args.fim:
        parser.error("--inicio vem depois de --fim")

    arquivo_env = RAIZ / ".env"
    if load_dotenv is not None:
        load_dotenv(arquivo_env)
    elif arquivo_env.is_file():
        parser.exit(1, "erro: achei o .env, mas falta o python-dotenv para ler o arquivo. "
                       "Rode: python3 -m pip install -r requirements.txt\n")

    dados = os.getenv("LOJA_DADOS")
    if not dados:
        parser.exit(1, "erro: LOJA_DADOS não está definida. Copie .env.exemplo para .env "
                       "(veja o README) ou defina a variável no terminal.\n")
    cfg = Config(inicio=args.inicio, fim=args.fim,
                 pasta_dados=caminho(dados),
                 pasta_saida=caminho(os.getenv("LOJA_SAIDA", "saida")),
                 token_api=os.getenv("LOJA_TOKEN_API", ""))
    return cfg, args.mostrar_config


def relativo(pasta):
    """Caminho a partir da pasta do projeto, igual em qualquer máquina, e se a pasta existe."""
    existe = "pasta encontrada" if pasta.is_dir() else "pasta ainda não existe"
    return f"{os.path.relpath(pasta, RAIZ)} ({existe})"


def descrever(cfg):
    """Texto da configuração para olhar antes de rodar. O token nunca aparece."""
    token = "definido (o valor não aparece)" if cfg.token_api else "vazio"
    return "\n".join([
        f"período: {cfg.inicio} a {cfg.fim}",
        f"dados: {relativo(cfg.pasta_dados)}",
        f"saída: {relativo(cfg.pasta_saida)}",
        f"token da API: {token}",
    ])
