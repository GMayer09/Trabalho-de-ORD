from sys import argv

def main() -> None:
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
    except:
        print('Erro')
    finally: #Roda depois de tudo, mesmo se cair no except
        if data: #Caso o arquivo ainda esteja aberto
            print('Fechando arquivo')
            data.close() #Fecha o arquivo

def execute(dataBase, arqName: str):
    with open(arqName, "r") as arq:
        instructions: list = arq.read().split('\n')
        for i in instructions:
            [flag, *reg] = i.split()
            strReg = "".join(reg)
            match flag:
                case "b":
                    search(int(strReg), dataBase)
                case "i":
                    insert(strReg, dataBase)
                case "r":
                    remove(strReg, dataBase)
            
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