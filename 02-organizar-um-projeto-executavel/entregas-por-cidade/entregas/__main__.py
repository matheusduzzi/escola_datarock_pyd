"""O comando do projeto. Rode da pasta do projeto: python3 -m entregas --inicio 2026-04 --fim 2026-06"""
import sys

from entregas import config, entrada, saida, transformacao


def main(argumentos=None):
    cfg, so_mostrar = config.ler(argumentos)
    if so_mostrar:
        print(config.descrever(cfg))
        return
    try:
        pedidos, clientes = entrada.ler_base(cfg.pasta_dados)
    except (FileNotFoundError, ValueError) as erro:
        sys.exit(f"erro: {erro}")
    entregues = transformacao.entregues_no_periodo(pedidos, cfg.inicio, cfg.fim)
    if entregues.empty:
        meses = pedidos["data_pedido"].str[:7]
        sys.exit(f"erro: nenhum pedido entregue de {cfg.inicio} a {cfg.fim}. "
                 f"Os pedidos da base vão de {meses.min()} a {meses.max()}.")
    resumo = transformacao.por_cidade(entregues, clientes)
    saida.mostrar(resumo, cfg.inicio, cfg.fim)
    arquivo = saida.gravar(resumo, cfg.pasta_saida, cfg.inicio, cfg.fim)
    try:
        arquivo = arquivo.relative_to(config.RAIZ)
    except ValueError:
        pass
    print(f"Tabela gravada em {arquivo}")


if __name__ == "__main__":
    main()
