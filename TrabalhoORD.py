from sys import argv

def main() -> None:
    data = None
    try:
        data = open("filmes.dat", "rb+")
        flag: str = argv[1]
        match flag:
            case "-e": # A execução do arquivo de operações será acionada pela linha de comando.
                execute(data, argv[2])
            case "-p": # A funcionalidade de impressão da LED também será acessada via linha de comando.
                pass
            case "-c": # A funcionalidade de compactação do arquivo filmes.dat também será acessada via linha de comando.
                pass
    except Exception as err:
        print('Erro: ', err)
    finally: # Roda depois de tudo, mesmo se cair no except
        if data: # Caso o arquivo ainda esteja aberto
            print('Fechando arquivo')
            data.close() # Fecha o arquivo

def execute(dataBase, arqName: str):
    with open(arqName, "r") as arq: # Abre o arquivo de instruções
        instructions: list = arq.read().split('\n') # Quebra o arquivo de instruções em uma lista
        for i in instructions:
            dataBase.seek(0)
            header = int.from_bytes(dataBase.read(4), signed=True)
            strInstruction: str = i.strip() # Limpa possíveis espaços no inicio e fim da linha
            instructionFlag: str = strInstruction[0] # Primeiro caracter da linha de instrução
            instructionData: str = strInstruction[1:] # Resto da linha de instrução
            match instructionFlag:
                case "b": # Busca
                    search(instructionData, dataBase)
                case "i": # Inserção
                    insert(instructionData, header, dataBase)
                case "r": # Remoção
                    remove(instructionData, header, dataBase)
            print('')
            
def search(regKey, dataBase): # A função faz a pesquisa de um dado ou chave
    regKey = regKey.strip()
    print(f'Busca pelo registro de chave "{regKey}"')
    byteOffset: int = dataBase.tell()
    buffer = read_reg(dataBase)
    while buffer:
        reg: list = buffer.split("|")
        id = reg[0]
        if id == regKey:
            print(f'{buffer} ({len(buffer)} bytes)')
            print(f'Local: offset = {byteOffset} bytes ({''})')
            return # Quebra o loop de busca pois achou o registro que estava procurando
        byteOffset = dataBase.tell()
        buffer = read_reg(dataBase)
    print('Erro: registro não encontrado!')
        

def read_reg(data):
    regLength = int.from_bytes(data.read(2)) # Lê o tamanho do registro
    if regLength <= 0: return '' # Caso o registro tenha tamanho <= 0 retorna uma string vazia
    
    reg = data.read(regLength) # Lê o registro
    return reg.decode()

def insert(data, header, dataBase): # A função faz a inserção de um dado ou chave. Com a utilização da estratégia de Best fit.
    regLength = 0
    regKey = 0
    print(f'Inserção do registro de chave "{regKey}" ({regLength} bytes)')

def remove(data, header, dataBase): # A função faz a remoção de um dado ou chave.
    # Registro removido deve conter: <tamanho>*<byteOffset do proximo>
    regKey = 0
    print(f'Remoção do registro de chave "{regKey}"')

if __name__ == "__main__":
    main()