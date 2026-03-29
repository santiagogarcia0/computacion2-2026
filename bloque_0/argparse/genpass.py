import argparse
import sys
import string
import secrets

def main():
    parser = argparse.ArgumentParser(
        description="Genera contraseñas seguras."
    )

    parser.add_argument(
        "-n", "--length",
        type=int,
        default=12,
        help="Longitud de la contraseña (default: 12)"
    )

    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Excluir símbolos especiales"
    )

    parser.add_argument(
        "--no-numbers",
        action="store_true",
        help="Excluir números"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Cantidad de contraseñas a generar (default: 1)"
    )

    args = parser.parse_args()

    length = args.length
    count = args.count

    # Validaciones
    if length <= 0:
        print("Error: la longitud debe ser mayor a 0.")
        sys.exit(1)

    if count <= 0:
        print("Error: la cantidad debe ser mayor a 0.")
        sys.exit(1)

    # Construir pool de caracteres
    caracteres = string.ascii_letters  # letras siempre

    if not args.no_numbers:
        caracteres += string.digits

    if not args.no_symbols:
        caracteres += "!@#$%&"

    if not caracteres:
        print("Error: no hay caracteres disponibles para generar la contraseña.")
        sys.exit(1)

    # Generar contraseñas
    for _ in range(count):
        password = "".join(secrets.choice(caracteres) for _ in range(length))
        print(password)

    sys.exit(0)


if __name__ == "__main__":
    main()