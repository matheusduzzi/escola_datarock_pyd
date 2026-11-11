# Roteiro de investigação

Os passos que a aula «Depurar e tratar exceções» segue quando um programa falha. Use na ordem.

1. **Rode de novo e guarde a saída inteira.** Copie o traceback todo, não só a última linha. Anote o comando que você rodou e o arquivo de entrada.
2. **Leia a última linha.** Ela tem o tipo do erro e a mensagem: `TypeError`, `ValueError`, `KeyError`, `ZeroDivisionError`. O tipo diz que tipo de coisa deu errado. A mensagem diz com que valor.
3. **Suba no traceback até a primeira linha do seu código.** A linha mais de baixo é onde o erro estourou. Pode ser dentro de uma função sua chamada por outra. Leia a sequência de baixo para cima até entender quem chamou quem.
4. **Veja o valor que chegou ali.** Ponha um `print` com o dado da linha, ou um `breakpoint()`, logo antes da linha que falhou. Se o erro acontece no meio de um loop, descubra em qual linha do arquivo de entrada.
5. **Faça a pergunta que separa os dois casos.** Com um dado válido, que segue o combinado (o LEIA-ME, o cadastro, o formato do arquivo), o código faria isso?
   - Faria: é um **defeito**. O código está errado. Conserte o código. Não ponha um `except` para o erro sumir.
   - Não faria, o dado é que está fora do combinado: é um **erro esperado**. O código precisa avisar, com o arquivo, a linha, o campo e o valor, e parar ou separar a linha de um jeito que dê para ver.
6. **Conserte uma coisa de cada vez e rode de novo.** O próximo erro só aparece depois que o primeiro sai da frente.
7. **Veja se o resultado bate.** O programa rodou até o fim? Compare o total com outra fonte e conte as linhas que ficaram de fora.
8. **Anote o que achou.** O que falhou, onde, por que, se era defeito ou erro esperado, o que você mudou e a saída depois da mudança.
