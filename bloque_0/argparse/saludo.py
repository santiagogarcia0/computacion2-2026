import sys

def mostrar_ayuda():
    print("Uso: saludo.py <nombre>")
    print()
    print("Descripción:")
    print("  Muestra un saludo con el nombre proporcionado.")
    print()
    print("Ejemplos:")
    print("  python saludo.py Juan")
    print("  python saludo.py María Elena")


def main():
    args = sys.argv

    # Caso: pedir ayuda
    if len(args) == 2 and args[1] in ("-h", "--help"):
        mostrar_ayuda()
        sys.exit(0)

    # Caso: sin argumentos
    if len(args) < 2:
        print("Uso: saludo.py <nombre>")
        print("Usá --help para más información.")
        sys.exit(1)

    # Tomar todos los argumentos como nombre (para nombres compuestos)
    nombre = " ".join(args[1:])

    print(f"Hola, {nombre}!")
    sys.exit(0)


if __name__ == "__main__":
    main()