"""Monta o repositório Git do tempos-por-etapa com a mudança do Caio para revisar.

Uso, de dentro da pasta desta aula:
    python3 montar_caso.py aula        cria caso-aula/tempos-por-etapa (a mudança da aula)
    python3 montar_caso.py exercicio   cria caso-exercicio/tempos-por-etapa (a segunda rodada)

A branch main tem o projeto que reproduziu na aula anterior. A branch transicoes tem os commits
do Caio, tirados de mudanca-do-caio/. Nomes, e-mails e datas dos commits são fixos: os hashes
saem iguais em qualquer computador. Só usa a biblioteca padrão e o Git, sem internet.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROJETO = AQUI / "tempos-por-etapa"
MUDANCA = AQUI / "mudanca-do-caio"
CAIO = ("Caio Prado", "caio@triatlo.exemplo")
COMMITS = {
    "aula": ["1-transicoes", "2-teste", "3-ajustes"],
    "exercicio": ["1-transicoes", "2-teste", "3-ajustes", "4-revisao"],
}
DATAS = {
    "main": "2026-11-16T10:00:00-03:00",
    "1-transicoes": "2026-11-17T09:12:00-03:00",
    "2-teste": "2026-11-17T09:40:00-03:00",
    "3-ajustes": "2026-11-17T10:05:00-03:00",
    "4-revisao": "2026-11-18T14:30:00-03:00",
}
FORA = {".venv", "__pycache__", ".pytest_cache", "saida"}


def git(pasta, *args, data=None):
    """Roda um comando do Git na pasta e para o script se ele falhar."""
    env = dict(os.environ)
    if data:
        env.update(GIT_AUTHOR_DATE=data, GIT_COMMITTER_DATE=data)
    resultado = subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=pasta,
                               env=env, capture_output=True, text=True)
    if resultado.returncode != 0:
        sys.exit(f"erro no git {' '.join(args)}:\n{resultado.stderr.strip()}")
    return resultado.stdout


def copiar(origem, destino):
    """Copia os arquivos de origem para destino, sem ambiente, cache e saídas."""
    for arquivo in sorted(origem.rglob("*")):
        relativo = arquivo.relative_to(origem)
        if arquivo.is_dir() or FORA & set(relativo.parts):
            continue
        if arquivo.name in ("mensagem.txt", "apagar.txt"):
            continue
        (destino / relativo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arquivo, destino / relativo)


def commit(repo, mensagem, data):
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "-m", mensagem, data=data)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMITS:
        sys.exit("uso: python3 montar_caso.py aula | exercicio")
    if shutil.which("git") is None:
        sys.exit("não achei o git: instale antes (aula «Preparar ambiente e autenticação»)")
    qual = sys.argv[1]
    repo = AQUI / f"caso-{qual}" / "tempos-por-etapa"
    if repo.exists():
        print(f"{repo.relative_to(AQUI)} já existe: apague a pasta caso-{qual} para montar de novo")
        sys.exit(2)
    repo.mkdir(parents=True)
    git(repo, "init", "--quiet", "-b", "main")
    git(repo, "config", "user.name", CAIO[0])
    git(repo, "config", "user.email", CAIO[1])
    git(repo, "config", "core.autocrlf", "false")
    copiar(PROJETO, repo)
    commit(repo, "tempos por etapa: medianas por categoria", DATAS["main"])
    git(repo, "switch", "--quiet", "-c", "transicoes")
    for passo in COMMITS[qual]:
        pasta = MUDANCA / passo
        apagar = pasta / "apagar.txt"
        if apagar.is_file():
            for nome in apagar.read_text(encoding="utf-8").split():
                git(repo, "rm", "--quiet", nome)
        copiar(pasta, repo)
        mensagem = (pasta / "mensagem.txt").read_text(encoding="utf-8").strip()
        commit(repo, mensagem, DATAS[passo])
    print(f"pronto: {repo.relative_to(AQUI)}, na branch transicoes")
    print(git(repo, "log", "--oneline", "main..transicoes").rstrip())


if __name__ == "__main__":
    main()
