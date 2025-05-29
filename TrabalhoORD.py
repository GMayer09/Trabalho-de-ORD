from sys import argv
from dataclasses import dataclass

# @dataclass
# class Movie:
#     title: str # Título
#     director: str # Diretor
#     year: int # Ano de lançamento
#     genres: list[str] # Gêneros do filme
#     time: int # Duração do filme em minutos
#     actors: list[str] # Atores do filme


@dataclass
class Register:
    id: int | None # Identificador do registro
    raw: str # Registro inteiro, sem modigficações, em string
    byteOffset: int # Byte-offset do registro
    length: int # Tamanho do registro
    isDeleted: bool = False # Indica se o registro está deletado
    ledPointer: int = -1
    # movie: Movie # Dados do filme extraídos do registro

def main() -> None:
    data = None
    try:
        data = open("filmes.dat", "rb+")
        flag: str = argv[1]
        match flag:
            case "-e": # A execução do arquivo de operações será acionada pela linha de comando.
                execute(data, argv[2])
            case "-p": # A funcionalidade de impressão da LED também será acessada via linha de comando.
                print_led(data)
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
            dataBase.seek(0) # Volta o ponteiro para o início da base de dados

            header = int.from_bytes(dataBase.read(4), signed=True)  # Cabeçalho da base de dados

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
            
def search(regKey, dataBase) -> Register | None: # A função faz a pesquisa de um dado ou chave
    searchId = int(regKey)
    print(f'Busca pelo registro de chave "{regKey}"')

    reg = read_reg(dataBase)
    while reg != None:

        if reg.id == searchId:
            print(f'{reg.raw} ({reg.length} bytes)')
            print(f'Local: offset = {reg.byteOffset} bytes ({''})')
            return reg # Quebra o loop de busca pois achou o registro que estava procurando
        
        reg = read_reg(dataBase)

    print('Erro: registro não encontrado!')
        

def read_reg(data) -> Register | None:

    byteOffset = data.tell() # Lê a posição do ponteiro para salvar o byte-offset do registro
    regLength = int.from_bytes(data.read(2)) # Lê o tamanho do registro
    
    if regLength <= 0: return None # Caso o registro tenha tamanho <= 0 retorna None
    
    checkRemove = data.read(1).decode()

    if checkRemove == '*':
        pointer = int.from_bytes(data.read(4), signed=True)
        data.seek(byteOffset + regLength + 2)

        return Register(
            id= None,
            raw= f'*{pointer}',
            byteOffset= byteOffset,
            length= regLength,
            isDeleted= True,
            ledPointer= pointer
        )

    data.seek(byteOffset + 2)
    buffer = data.read(regLength).decode() # Lê o registro
    reg = buffer.split('|') # Quebra o registro em uma lista
    
    # Grava os dados lidos em formato de dataclasses
    # movie = Movie(
    #     title= reg[1],
    #     director= reg[2],
    #     year= int(reg[3]),
    #     genres= reg[4].split(','),
    #     time= int(reg[5]),
    #     actors= reg[6].split(',')
    # )

    return Register(
        id= int(reg[0]),
        raw= buffer,
        byteOffset= byteOffset,
        length= regLength,
        # movie= movie
    )

def insert(data, header, dataBase): # A função faz a inserção de um dado ou chave. Com a utilização da estratégia de Best fit.
    regLength = 0
    regKey = 0
    print(f'Inserção do registro de chave "{regKey}" ({regLength} bytes)')

def remove(regKey, header, dataBase) -> tuple[int, int] | None: # A função faz a remoção de um dado ou chave.
    # Registro removido deve conter: <tamanho>*<byteOffset do proximo>
    rId = int(regKey)
    print(f'Remoção do registro de chave "{rId}"')
    # encontrar registro
    reg = read_reg(dataBase)
    while reg != None:

        if reg.id == rId:
            break

        reg = read_reg(dataBase)
    # salvar offset e id do registro
    if reg == None:
        print('Erro: registro não encontrado!')
        return None
    
    print(f'Registro removido! ({reg.length} bytes)')
    print(f'Local: offset = {reg.byteOffset} bytes ({''})')

    rOffset = reg.byteOffset
    # marcar registro como removido e adicionar o offset da cabeça da led
    dataBase.seek(rOffset + 2)
    dataBase.write('*'.encode())
    dataBase.write(header.to_bytes(4, signed=True))
    # atualizar cabeça da led
    dataBase.seek(0)
    dataBase.write(rOffset.to_bytes(4, signed=True))
    #ordenar cabeçalho
    order_led(dataBase)


def order_led(dataBase) -> None:
    pass

def print_led(dataBase) -> None:
    LED: list[tuple[int, int]] = []

    header = int.from_bytes(dataBase.read(4), signed=True)

    if header != -1:
        dataBase.seek(header)

        reg = read_reg(dataBase)
        while reg != None and reg.isDeleted and reg.ledPointer != -1:

            LED.append((reg.byteOffset, reg.length))
            dataBase.seek(reg.ledPointer)
            reg = read_reg(dataBase)

    strLED = 'LED'
    for i in LED:
        strLED += f' -> [offset: {i[0]}, tam: {i[1]}]'
    strLED += ' -> [offset: -1]'

    print(strLED)
    print(f'Total: {len(LED)} espaços disponíveis')
    print('A LED foi impressa com sucesso!')

if __name__ == "__main__":
    main()