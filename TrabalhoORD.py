from sys import argv
from dataclasses import dataclass

@dataclass
class Register:
    id: int | None # Identificador do registro
    raw: bytes # Registro inteiro, sem modigficações, em string
    byteOffset: int # Byte-offset do registro
    length: int # Tamanho do registro
    isDeleted: bool = False # Indica se o registro está deletado
    ledPointer: int = -1

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
            print(f'{reg.raw.decode()} ({reg.length} bytes)')
            print(f'Local: offset = {reg.byteOffset} bytes ({''})')
            return reg # Quebra o loop de busca pois achou o registro que estava procurando
        
        reg = read_reg(dataBase)

    print('Erro: registro não encontrado!')
        

def read_reg(data) -> Register | None:

    byteOffset = data.tell() # Lê a posição do ponteiro para salvar o byte-offset do registro
    regLength = int.from_bytes(data.read(2)) # Lê o tamanho do registro
    
    if regLength <= 0: return None # Caso o registro tenha tamanho <= 0 retorna None
    
    byteReg = data.read(regLength)

    if byteReg.startswith(b'*'):
        
        pointer = int.from_bytes(byteReg[1:5])

        return Register(
            id= None,
            raw= byteReg,
            byteOffset= byteOffset,
            length= regLength,
            isDeleted= True,
            ledPointer= pointer
        )
    
    reg = byteReg.decode().split('|')
    return Register(
        id= int(reg[0]),
        raw= byteReg,
        byteOffset= byteOffset,
        length= regLength
    )


def insert(data, header, dataBase): # A função faz a inserção de um dado ou chave. Com a utilização da estratégia de Best fit.
    regLength = 0
    regKey = 0
    print(f'Inserção do registro de chave "{regKey}" ({regLength} bytes)')

def remove(regKey, header, dataBase) -> tuple[int, int] | None: # A função faz a remoção de um dado ou chave.
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

    # marcar registro como removido e adicionar o offset da cabeça da led
    
    dataBase.seek(reg.byteOffset + 2)
    dataBase.write(b'*' + header.to_bytes(4, signed=True) + reg.raw[5:])

    # atualizar cabeça da led
    
    dataBase.seek(0)
    dataBase.write(reg.byteOffset.to_bytes(4, signed=True))

    print(f'Registro removido! ({reg.length} bytes)')
    print(f'Local: offset = {reg.byteOffset} bytes ({''})')
    
def read_led(header, dataBase) -> list[tuple[int, int]]:
    LED: list[tuple[int, int]] = []

    if header != -1:
        dataBase.seek(header)

        reg = read_reg(dataBase)
        while reg != None and reg.isDeleted:

            if reg.ledPointer == -1:
                LED.append((reg.byteOffset, reg.length))
                LED.append((-1, -1))
                break

            LED.append((reg.byteOffset, reg.length))
            dataBase.seek(reg.ledPointer)
            reg = read_reg(dataBase)

    return LED

def print_led(dataBase) -> None:
    header = int.from_bytes(dataBase.read(4), signed=True)
    LED: list[tuple[int, int]] = read_led(header, dataBase)

    strLED = 'LED'
    for i in LED:
        strOffset = f' -> [offset: {i[0]}'
        strLength = f', tam: {i[1]}' if i[1] != -1 else ''
        strLED +=  strOffset + strLength + ']'

    print(strLED)
    print(f'Total: {len(LED) - 1} espaços disponíveis')
    print('A LED foi impressa com sucesso!')

if __name__ == "__main__":
    main()