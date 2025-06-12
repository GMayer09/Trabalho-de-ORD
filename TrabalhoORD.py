from sys import argv
from dataclasses import dataclass
import traceback
import os

@dataclass
class Register:
    id: int | None # Identificador do registro
    raw: bytes # Registro inteiro, sem modificações, em bytes
    byteOffset: int # Byte-offset do registro
    length: int # Tamanho do registro
    isDeleted: bool = False # Indica se o registro está deletado
    ledPointer: int = -1 # Ponteiro para o proximo registro da LED


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
                compact(data)
            case "-d":
                print(data.read())
    except Exception as err:
        traceback.print_exc()
    finally:
        if data: # Caso o arquivo ainda esteja aberto
            data.close() # Fecha o arquivo


def execute(dataBase, arqName: str):

    with open(arqName, "r") as arq:
        instructions: list = arq.read().split('\n') # Quebra o arquivo de instruções em uma lista

        for i in instructions:
            dataBase.seek(0)

            header = int.from_bytes(dataBase.read(4), signed=True)

            strInstruction: str = i.strip() # Limpa possíveis espaços no inicio e fim da linha
            instructionFlag: str = strInstruction[0] # Primeiro caracter da linha de instrução
            instructionData: str = strInstruction[2:] # Resto da linha de instrução (pulando o espaço)
            
            match instructionFlag:
                case "b": # Busca
                    search(instructionData, dataBase)
                case "i": # Inserção
                    insert(instructionData, header, dataBase)
                case "r": # Remoção
                    remove(instructionData, header, dataBase)
            print('')
        
    print(f'As operações do arquivo dados/{arqName} foram executadas com sucesso!\n')


def search(regKey, dataBase) -> None: # A função faz a busca de um registro pela chave
    searchId = int(regKey)
    print(f'Busca pelo registro de chave "{regKey}"')

    reg = read_reg(dataBase)
    while reg != None:

        if reg.id == searchId:

            strReg = reg.raw.decode()
            lstReg = strReg.split('|')
            regLength = reg.length

            # Remove espaço vazio no fim do arquivo caso ele exista
            if lstReg[-1].startswith('*'):
                emptySpace = len(lstReg[-1])
                regLength -= emptySpace
                strReg = strReg[:-emptySpace]

            print(f'{strReg} ({regLength} bytes)')
            print(f'Local: offset = {reg.byteOffset} bytes ({hex(reg.byteOffset)})')
            return # Quebra o loop de busca pois achou o registro que estava procurando
        
        reg = read_reg(dataBase)

    print('Erro: registro nao encontrado!')


def read_reg(data) -> Register | None:

    byteOffset = data.tell()
    regLength = int.from_bytes(data.read(2))
    
    if regLength <= 0: return None
    
    byteReg = data.read(regLength)

    if byteReg.startswith(b'*'): # Caso o registro esteja marcado como removido
        
        pointer = int.from_bytes(byteReg[1:5]) # Ponteiro para o proximo registro da LED

        return Register(
            id= None,
            raw= byteReg,
            byteOffset= byteOffset,
            length= regLength,
            isDeleted= True,
            ledPointer= pointer
        ) # Estrutura do registro removido
    
    reg = byteReg.decode().split('|')
    return Register(
        id= int(reg[0]),
        raw= byteReg,
        byteOffset= byteOffset,
        length= regLength
    ) # Estrutura do registro


def insert(data, header, dataBase): # A função faz a inserção de um dado ou chave.
    newReg = data.encode()
    regLength = len(newReg)

    regKey = newReg.decode().split('|')[0]
    print(f'Inserção do registro de chave "{regKey}" ({regLength} bytes)')

    offset = None
    lengthDiff = 0
    LED = read_led(header, dataBase)

    # Encontra a posição certa para inserir o registro
    i = 0
    while i < len(LED) - 1:
        if LED[i][1] >= regLength:
            offset = LED[i][0]
            lengthDiff = LED[i][1] - regLength
            break
        i+=1
    # Salva os offsets dos registros da LED que precisarão ser atualizados (caso eles existam)
    previous = LED[i - 1] if i > 0 else None
    next = LED[i + 1] if i < len(LED)-1 else -1
    
    if offset == None:
        print('Local: fim do arquivo')
        dataBase.seek(0, 2) # Seek para o fim do arquivo
        dataBase.write(regLength.to_bytes(2))
        dataBase.write(newReg)
        return
    
    if previous != None:
        dataBase.seek(previous[0] + 3) # Move o ponteiro para o registro "anterior" ao best-fit, pulando tamanho e *
        dataBase.write(next[0].to_bytes(4, signed=True))
    else:
        dataBase.seek(0) # Move o ponteiro para o cabeçalho do arquivo
        dataBase.write(next[0].to_bytes(4, signed=True))

    print(f'Local: offset = {offset} bytes ({hex(offset)})')
    dataBase.seek(offset + 2)
    dataBase.write(newReg + b'*'*lengthDiff) # Insere o novo registro na posição encontrada


def remove(regKey, header, dataBase) -> tuple[int, int] | None: # A função faz a remoção de um dado ou chave.
    rId = int(regKey)
    print(f'Remoção do registro de chave "{rId}"')

    # encontrar registro
    reg = read_reg(dataBase)
    while reg != None:

        if reg.id == rId:
            break

        reg = read_reg(dataBase)

    if reg == None:
        print('Erro: registro nao encontrado!')
        return None


    LED: list[tuple[int, int]] = read_led(header, dataBase)
    (previous, next) = best_fit(reg, LED)

    # Marca o registro como removido
    dataBase.seek(reg.byteOffset + 2)
    dataBase.write(b'*' + next.to_bytes(4, signed=True))

    # Atualiza a LED
    if previous != None:
        dataBase.seek(previous + 3)
    else :
        dataBase.seek(0)
    dataBase.write(reg.byteOffset.to_bytes(4, signed=True))
    
    print(f'Registro removido! ({reg.length} bytes)')
    print(f'Local: offset = {reg.byteOffset} bytes ({hex(reg.byteOffset)})')


def best_fit(reg: Register, LED: list[int | None, int]): # Encontra a posição certa para inserir um registro na LED e retorna o anterior e sucessor dele

    # Caso a LED esteja vazia ou a posição certa do registro seja a cabeça da LED
    if len(LED) == 1 or LED[0][0] == -1 or LED[0][1] > reg.length:

        previous = None
        next = LED[0][0]

        return (previous , next)
    
    # Caso contrário, itera pela LED procurando o melhor espaço
    i = 1
    while i < len(LED):
        if LED[i][0] == -1 or LED[i][1] > reg.length:

            previous = LED[i - 1][0]
            next = LED[i][0]

            return (previous, next)
        i += 1


def read_led(header, dataBase) -> list[tuple[int, int]]: # Lê a LED do arquivo em formato de lista de tuplas [offset, tamanho]
    LED: list[tuple[int, int]] = [] # Define a LED como uma lista vazia

    if header == -1: # Caso o cabeçalho seja -1, a LED está vazia
        return [(-1, -1)]

    dataBase.seek(header)

    reg = read_reg(dataBase)
    while reg != None and reg.isDeleted:

        if reg.ledPointer == -1: # Caso estivermos no final da LED
            LED.append((reg.byteOffset, reg.length)) # Concatena o ultimmo elemento
            break # Quebra o loop

        LED.append((reg.byteOffset, reg.length))
        dataBase.seek(reg.ledPointer)
        reg = read_reg(dataBase)

    LED.append((-1, -1)) # Final padrão da LED
    return LED


def print_led(dataBase) -> None: # Imprime a LED
    header = int.from_bytes(dataBase.read(4), signed=True)
    LED: list[tuple[int, int]] = read_led(header, dataBase)

    strLED = 'LED'
    for i in LED:
        if i[0] != -1:
            strLED += f' -> [offset: {i[0]}, tam: {i[1]}]'
        else:
            strLED += ' -> [offset: -1]'

    print(strLED)
    print(f'Total: {len(LED) - 1} espaços disponíveis')
    print('A LED foi impressa com sucesso!\n')

def compact(dataBase) -> None:
    with open("aux.dat", "wb") as arq:

        header = dataBase.read(4) # Pula o cabeçalho
        arq.write((-1).to_bytes(4, signed=True)) # Grava um cabeçalho padrão

        reg = read_reg(dataBase)
        while reg is not None:
            
            if not reg.isDeleted:

                arq.write(reg.length.to_bytes(2))
                arq.write(reg.raw)
                
            reg = read_reg(dataBase)
        dataBase.close() # Fecha o arquivo principal
        os.rename("aux.dat", "filmes.dat") # Renomeia o arquivo auxiliar para "filmes.dat"

if __name__ == "__main__":
    main()