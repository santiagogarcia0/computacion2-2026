import sys

def mostrar_ayuda():
    print("Uso: suma.py [numeros...]")
    print()
    print("Descripción:")
    print("  Suma todos los números proporcionados como argumentos.")
    print("  Si no se pasan números, devuelve 0.")
    print()
    print("Ejemplos:")
    print("  python suma.py 1 2 3 4 5")
    print("  python suma.py 3.14 2.86")
    print("  python suma.py")


def main():
    args = sys.argv

    # --help
    if len(args) == 2 and args[1] in ("-h", "--help"):
        mostrar_ayuda()
        sys.exit(0)

    numeros = args[1:]

    # Caso sin argumentos
    if len(numeros) == 0:
        print("Suma: 0")
        sys.exit(0)

    total = 0

    for valor in numeros:
        try:
            numero = float(valor)
            total += numero
        except ValueError:
            print(f"Error: '{valor}' no es un número válido.")
            sys.exit(1)

    print(f"Suma: {total}")
    sys.exit(0)


if __name__ == "__main__":
    main()