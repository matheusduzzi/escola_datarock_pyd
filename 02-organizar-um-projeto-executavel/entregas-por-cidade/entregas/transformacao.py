"""Transformação: as regras do relatório. Recebe tabelas e retorna tabelas; não lê nem grava arquivo."""


def entregues_no_periodo(pedidos, inicio, fim):
    """Pedidos entregues dos meses de inicio a fim, os dois incluídos (AAAA-MM)."""
    mes = pedidos["data_pedido"].str[:7]
    return pedidos[(pedidos["status"] == "entregue") & (mes >= inicio) & (mes <= fim)]


def por_cidade(pedidos, clientes):
    """Pedidos e faturamento por cidade do cliente, do maior faturamento para o menor."""
    base = pedidos.merge(clientes[["id_cliente", "cidade"]], on="id_cliente")
    resumo = base.groupby("cidade").agg(pedidos=("id_pedido", "count"), faturamento=("valor", "sum"))
    return resumo.sort_values("faturamento", ascending=False).round(2)
