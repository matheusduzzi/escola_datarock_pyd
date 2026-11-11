# Os resultados recuperados

A mensagem que a cronometragem mandou para a Bia, depois que ela perguntou pelas inscrições sem resultado:

> "Achamos mais alguns resultados nos registros dos tapetes de chip e no papel dos fiscais de prova. Vão no arquivo `recuperados.json`, no mesmo formato da API. Pode ter coisa que vocês já têm, e pode ter coisa repetida."

| Arquivo | O que tem |
|---|---|
| `recuperados.json` | Uma lista de resultados no formato da API: `edicao`, `id_inscricao`, `numero_peito`, `status`, `parciais` e `tempo_oficial`. |
| `gerar.py` | Gera o `recuperados.json` de novo. Só usa a biblioteca padrão e sempre escreve o mesmo arquivo. |

Os campos têm o mesmo significado do LEIA-ME dos dados do triatlo, na pasta `dados/triatlo` do kit: parcial `null` quer dizer que o tempo não existe, e `tempo_oficial` é `null` para quem não concluiu.

Para gerar o arquivo de novo, de dentro dessa pasta:

```bash
python3 gerar.py
```
