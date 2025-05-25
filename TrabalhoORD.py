from sys import argv

def main() -> None:
    data = None
    try:
        data = open("filmes.dat", "rb+")
        flag: str = argv[1]
        match flag:
            case "-e":
                execute(data, argv[2])
            case "-p":
                pass
            case "-c":
                pass
    except Exception as err:
        print('Erro: ', err)
    finally: #Roda depois de tudo, mesmo se cair no except
        if data: #Caso o arquivo ainda esteja aberto
            print('Fechando arquivo')
            data.close() #Fecha o arquivo

def execute(dataBase, arqName: str):
    with open(arqName, "r") as arq: # Abre o arquivo de instruções
        instructions: list = arq.read().split('\n') # Quebra o arquivo de instruções em uma lista
        for i in instructions:
            strReg: str = i.strip() # Limpa possíveis espaços no inicio e fim da linha
            flag: str = strReg[0] # Primeiro caracter da linha de instrução
            regData: str = strReg[1:] # Resto da linha de instrução
            match flag:
                case "b": # Busca
                    search(int(regData), dataBase)
                case "i": # Inserção
                    insert(regData, dataBase)
                case "r": # Remoção
                    remove(regData, dataBase)
            
def search(regKey, dataBase):
    print(f'Busca pelo registro de chave "{regKey}"')

def insert(data, dataBase):
    regLength = 0
    regKey = 0
    print(f'Inserção do registro de chave "{regKey}" ({regLength} bytes)')

def remove(data, dataBase):
    regKey = 0
    print(f'Remoção do registro de chave "{regKey}"')

if __name__ == "__main__":
    main()