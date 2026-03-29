import argparse
import sys

def procesar_stream(stream, nombre, args, multiple_archivos):
    coincidencias = 0

    for i, linea in enumerate(stream, start=1):
        linea = linea.rstrip("\n")

        texto = linea
        patron = args.patron

        if args.ignore_case:
            texto = texto.lower()
            patron = patron.lower()

        match = patron in texto

        if args.invert:
            match = not match

        if match:
            coincidencias += 1

            if not args.count:
                salida = ""

                # Prefijo con nombre de archivo si hay varios
                if multiple_archivos and nombre:
                    salida += f"{nombre}:"

                # Número de línea si corresponde
                if args.line_number or multiple_archivos:
                    salida += f"{i}: "

                salida += linea
                print(salida)

    return coincidencias


def main():
    parser = argparse.ArgumentParser(
        description="Busca un patrón en archivos o stdin."
    )

    parser.add_argument(
        "patron",
        help="Texto a buscar"
    )

    parser.add_argument(
        "archivos",
        nargs="*",
        help="Archivos donde buscar (default: stdin)"
    )

    parser.add_argument(
        "-i", "--ignore-case",
        action="store_true",
        help="Ignorar mayúsculas/minúsculas"
    )

    parser.add_argument(
        "-n", "--line-number",
        action="store_true",
        help="Mostrar número de línea"
    )

    parser.add_argument(
        "-c", "--count",
        action="store_true",
        help="Mostrar solo cantidad de coincidencias"
    )

    parser.add_argument(
        "-v", "--invert",
        action="store_true",
        help="Mostrar líneas que NO coinciden"
    )

    args = parser.parse_args()

    total = 0

    try:
        # Caso: stdin
        if not args.archivos:
            if not sys.stdin.isatty():
                total = procesar_stream(sys.stdin, None, args, False)

                if args.count:
                    print(f"Total: {total} coincidencias")

                sys.exit(0)
            else:
                print("Error: no se especificaron archivos ni entrada por stdin.")
                sys.exit(1)

        # Caso: archivos
        multiple_archivos = len(args.archivos) > 1

        for archivo in args.archivos:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    count = procesar_stream(f, archivo, args, multiple_archivos)

                    if args.count:
                        print(f"{archivo}: {count} coincidencias")

                    total += count

            except FileNotFoundError:
                print(f"Error: archivo '{archivo}' no encontrado.")
                sys.exit(1)

        if args.count and multiple_archivos:
            print(f"Total: {total} coincidencias")

        sys.exit(0)

    except Exception:
        print("Error inesperado durante la búsqueda.")
        sys.exit(1)


if __name__ == "__main__":
    main()