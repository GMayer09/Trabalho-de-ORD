from sys import argv

def main() -> None:
    try:
        data = open("filmes.dat", "rb+")
        flag: str = argv[1]
        match flag:
            case "-e":
                pass
            case "-p":
                pass
            case "-c":
                pass
        data.close()
    except:
        pass
    finally:
        pass

if __name__ == "__main__":
    main() 