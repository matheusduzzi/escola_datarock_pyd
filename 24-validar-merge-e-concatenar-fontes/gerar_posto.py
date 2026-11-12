"""Gera as planilhas do posto de chegada: posto/posto_2025.csv e posto/posto_2024.csv.

    python3 gerar_posto.py

Só usa a biblioteca padrão e sempre escreve os mesmos arquivos. As linhas estão escritas abaixo,
na ordem em que os fiscais anotaram. O posto anota o peito, não o id da inscrição.
"""
import csv
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COLUNAS = ['edicao', 'peito', 'status', 'tempo']

POSTO = {
    2025: [
        (110, 'concluiu', '12:23:31'),
        (334, 'concluiu', '12:41:07'),
        (117, 'concluiu', '10:18:14'),
        (115, 'concluiu', '11:55:08'),
        (562, 'concluiu', '12:05:44'),
        (125, 'concluiu', '10:29:27'),
        (334, 'concluiu', '12:41:07'),
        (483, 'concluiu', '13:18:52'),
        (140, 'concluiu', '11:18:51'),
        (168, 'concluiu', '14:21:36'),
        (335, 'DNF', ''),
        (159, 'concluiu', '10:15:22'),
    ],
    2024: [
        (103, 'concluiu', '12:05:28'),
        (280, 'concluiu', '11:58:40'),
        (120, 'concluiu', '10:22:43'),
        (226, 'concluiu', '12:10:33'),
        (129, 'concluiu', '11:47:52'),
        (525, 'concluiu', '11:02:09'),
        (120, 'concluiu', '10:22:43'),
        (136, 'concluiu', '12:05:00'),
        (137, 'concluiu', '13:40:18'),
        (280, 'concluiu', '11:53:40'),
        (268, 'DNF', ''),
        (152, 'concluiu', '10:17:45'),
    ],
}


def main():
    pasta = AQUI / 'posto'
    pasta.mkdir(exist_ok=True)
    for edicao, linhas in POSTO.items():
        with open(pasta / f'posto_{edicao}.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(COLUNAS)
            for peito, status, tempo in linhas:
                w.writerow([edicao, peito, status, tempo])
        print(f'gravei posto/posto_{edicao}.csv: {len(linhas)} linhas')


if __name__ == '__main__':
    main()
