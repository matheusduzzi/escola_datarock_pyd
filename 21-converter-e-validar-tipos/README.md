# 21. Converter e validar tipos

Os arquivos da aula «Converter e validar tipos». Rode os comandos de dentro desta pasta. Os atletas e os resultados da prova ficam em `../dados/triatlo`. O dicionário está em [../dados/triatlo/LEIA-ME.md](../dados/triatlo/LEIA-ME.md).

Você só precisa do Python com o pandas, como no README da raiz do kit. Para ver se ele está aí:

```bash
python3 -c "import pandas; print(pandas.__version__)"
```

A aula foi rodada com o Python 3.9.6 e o pandas 2.3.3. Se aparecer `No module named 'pandas'`, rode `python3 -m pip install pandas` com o mesmo `python3`.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `gerar.py` | Lê `../dados/triatlo` e monta os três arquivos de entrada da aula. Sempre escreve os mesmos arquivos. |
| `formulario_2026.csv` | As respostas do formulário de inscrição de 2026, como foram digitadas: `id_resposta`, `canal` (`site` ou `app`), `nascimento`, `categoria` e `valor_pago`. |
| `extrato_tesouraria.csv` | O que o banco mostra de cada inscrição paga: `id_resposta` e `valor`. |
| `cronometragem_2025.csv` | A planilha da cronometragem de 2025, para o exercício: `numero_peito`, `status`, `tempo_oficial` e `chegada`. |
| `conversao.py` | As funções da aula: `forma`, `numero_br`, `data`, `categoria`, `rejeicoes` e `relatorio`. Cada uma diz o que converteu e o motivo do que não converteu. |
| `tipos.py` | O formulário convertido de cinco jeitos: o código da IA, o valor pago, o nascimento, a categoria e o jeito certo. |
| `conversoes.csv` e `rejeicoes.csv` | O relatório de conversões e a tabela de rejeições do formulário, escritos pelo `tipos.py --jeito certo`. |
| `checar_conversao.py` | Checa uma conversão: nenhuma linha perdida, nenhum valor sumido sem registro, os tipos certos. Você usa a função `checar` no exercício. |
| `testar_checar.py` | Estraga a conversão do formulário de dez jeitos e vê se o `checar_conversao.py` acusa cada um. |
| `exercicio.py` | O programa do exercício. Você escreve a função `converter_cronometragem`. |
| `minhas-respostas.md` | A folha do exercício. Salve uma cópia com o seu nome. |

## Comandos

```bash
python3 gerar.py
python3 tipos.py --jeito ia
python3 tipos.py --jeito numeros
python3 tipos.py --jeito datas
python3 tipos.py --jeito categorias
python3 tipos.py --jeito certo
python3 testar_checar.py
python3 exercicio.py
```

No Windows, troque `python3` por `py`.

O `exercicio.py` para com o código 1 e a mensagem `falta escrever converter_cronometragem` enquanto você não escrever a função. Depois de escrita, ele grava `conversoes_cronometragem.csv` e `rejeicoes_cronometragem.csv` e sai com 0 se o `checar_conversao` disser `ok`, e com 1 se ele achar algum problema.

O `testar_checar.py` sai com 1 se o `checar_conversao.py` responder errado em algum caso. Se você mexer no `checar_conversao.py`, rode ele de novo.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
