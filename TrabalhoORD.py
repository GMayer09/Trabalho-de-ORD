from sys import argv

def abre_arquivo() -> None:
    nome_arq = 'filmes.dat' # Arquivo a ser aberto.
    arq = open(nome_arq, 'rb+')  # Arquivo a ser lido e escrito.

    arq.close()