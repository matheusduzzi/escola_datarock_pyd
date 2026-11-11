"""Gera os dados FICTÍCIOS da Loja Exemplo para o curso primeiros-passos-dados.

Só stdlib. Seed fixa: rodar duas vezes dá os mesmos arquivos, byte a byte.

    python3 dados/gerar.py                 # escreve em dados/
    python3 dados/gerar.py --saida /tmp/x  # escreve em outra pasta (usado no teste)

Casos de borda plantados de propósito (os exercícios dependem deles):
- clientes sem nenhum pedido, entre eles TODOS os clientes de Bauru (a cidade some no INNER JOIN);
- 11 pedidos com valor vazio (valor não registrado no caixa);
- pedidos caros em 2026-02-28 e 2026-04-01 (fronteira de março) e um cancelado caro em março;
- dois produtos de Esporte com o mesmo preço (empate na ordenação).
"""
import argparse
import csv
import datetime
import pathlib
import random

SEED = 42
N_CLIENTES = 300
N_PEDIDOS = 3000
N_VALOR_NULO = 11
INICIO = datetime.date(2026, 1, 1)
FIM = datetime.date(2026, 6, 30)

CIDADES = [
    ("Campinas", 60), ("Sorocaba", 35), ("Jundiaí", 30), ("Piracicaba", 28),
    ("Ribeirão Preto", 27), ("Santos", 25), ("Limeira", 20), ("Americana", 18),
    ("Indaiatuba", 18), ("Valinhos", 15), ("São Carlos", 21),
]
CLIENTES_BAURU = 3

CATEGORIAS = {
    "Eletro": ["Liquidificador", "Ventilador", "Batedeira", "Torradeira", "Cafeteira",
               "Sanduicheira", "Ferro de passar", "Aspirador"],
    "Casa": ["Jogo de toalhas", "Panela", "Jogo de copos", "Tapete", "Luminária",
             "Organizador", "Lençol", "Cortina"],
    "Papelaria": ["Caderno", "Caneta", "Agenda", "Estojo", "Marca-texto",
                  "Mochila", "Calculadora", "Pasta"],
    "Esporte": ["Bola", "Garrafa térmica", "Tapete de yoga", "Corda de pular", "Halter",
                "Bicicleta ergométrica", "Joelheira", "Luva de treino"],
    "Beleza": ["Secador", "Escova", "Hidratante", "Protetor solar", "Chapinha",
               "Perfume", "Kit de maquiagem", "Sabonete"],
}
FAIXA_PRECO = {
    "Eletro": (60, 400), "Casa": (20, 250), "Papelaria": (5, 120),
    "Esporte": (15, 900), "Beleza": (12, 300),
}


def _data(rng):
    dias = (FIM - INICIO).days
    return INICIO + datetime.timedelta(days=rng.randint(0, dias))


def gerar(saida):
    rng = random.Random(SEED)
    saida.mkdir(parents=True, exist_ok=True)

    # clientes
    nomes_cidade = [c for c, _ in CIDADES]
    pesos = [p for _, p in CIDADES]
    clientes = []
    for i in range(1, N_CLIENTES - CLIENTES_BAURU + 1):
        cidade = rng.choices(nomes_cidade, weights=pesos)[0]
        clientes.append([i, "Cliente %04d" % i, cidade, "SP",
                         (datetime.date(2025, 1, 1) + datetime.timedelta(days=rng.randint(0, 364))).isoformat()])
    for i in range(N_CLIENTES - CLIENTES_BAURU + 1, N_CLIENTES + 1):
        clientes.append([i, "Cliente %04d" % i, "Bauru", "SP", "2025-12-15"])

    ids_bauru = {c[0] for c in clientes if c[2] == "Bauru"}
    outros = [c[0] for c in clientes if c[0] not in ids_bauru]
    sem_pedido = set(rng.sample(outros, 14)) | ids_bauru
    compradores = [i for i in outros if i not in sem_pedido]

    # produtos
    produtos = []
    pid = 0
    for categoria, nomes in CATEGORIAS.items():
        lo, hi = FAIXA_PRECO[categoria]
        for nome in nomes:
            pid += 1
            preco = round(rng.uniform(lo, hi), 2)
            produtos.append([pid, nome, categoria, preco])
    # empate plantado: dois produtos de Esporte com o mesmo preço
    esporte = [p for p in produtos if p[2] == "Esporte"]
    esporte[3][3] = esporte[6][3]
    preco_de = {p[0]: p[3] for p in produtos}
    mais_caro = max(produtos, key=lambda p: p[3])

    # pedidos
    pedidos = []
    for i in range(1, N_PEDIDOS + 1):
        produto = rng.choice(produtos)
        qtd = rng.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]
        status = "cancelado" if rng.random() < 0.1 else "entregue"
        pedidos.append([i, rng.choice(compradores), produto[0], _data(rng).isoformat(),
                        qtd, round(qtd * produto[3], 2), status])

    # fronteira de março e cancelado caro em março
    def plantar(data, status):
        n = len(pedidos) + 1
        pedidos.append([n, rng.choice(compradores), mais_caro[0], data, 5,
                        round(5 * mais_caro[3], 2), status])

    plantar("2026-02-28", "entregue")
    plantar("2026-04-01", "entregue")
    plantar("2026-03-15", "cancelado")

    # valores nulos: 11 pedidos sem valor registrado, ao menos um em março
    marco = [p for p in pedidos if p[3].startswith("2026-03") and p[6] == "entregue"]
    nulos = {rng.choice(marco)[0]}
    while len(nulos) < N_VALOR_NULO:
        nulos.add(rng.randint(1, N_PEDIDOS))
    for p in pedidos:
        if p[0] in nulos:
            p[5] = ""

    def escrever(nome, cabecalho, linhas):
        with open(saida / nome, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(cabecalho)
            w.writerows(linhas)

    escrever("clientes.csv", ["id_cliente", "nome", "cidade", "uf", "data_cadastro"], clientes)
    escrever("produtos.csv", ["id_produto", "nome", "categoria", "preco"], produtos)
    escrever("pedidos.csv", ["id_pedido", "id_cliente", "id_produto", "data_pedido",
                             "quantidade", "valor", "status"], pedidos)
    return {
        "clientes": len(clientes), "produtos": len(produtos), "pedidos": len(pedidos),
        "clientes_sem_pedido": len(sem_pedido), "valor_nulo": len(nulos),
    }


def main():
    parser = argparse.ArgumentParser(description="Gera os CSVs fictícios do curso.")
    parser.add_argument("--saida", default=str(pathlib.Path(__file__).resolve().parent),
                        help="pasta de saída (padrão: dados/)")
    args = parser.parse_args()
    resumo = gerar(pathlib.Path(args.saida))
    print(" ".join("%s=%s" % (k, v) for k, v in resumo.items()))


if __name__ == "__main__":
    main()
