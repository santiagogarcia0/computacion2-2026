import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Lista archivos de un directorio."
    )

    # Argumento posicional opcional
    parser.add_argument(
        "directorio",
        nargs="?",
        default=".",
        help="Directorio a listar (default: actual)"
    )

    # Flag -a / --all
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Incluye archivos ocultos"
    )

    # Opción --extension
    parser.add_argument(
        "--extension",
        help="Filtrar por extensión (ej: .py, .txt)"
    )

    args = parser.parse_args()

    directorio = args.directorio
    mostrar_ocultos = args.all
    extension = args.extension

    # Validar directorio
    if not os.path.isdir(directorio):
        print(f"Error: '{directorio}' no es un directorio válido.")
        sys.exit(1)

    try:
        archivos = os.listdir(directorio)

        for nombre in archivos:

            # Ocultar archivos ocultos si no se pidió -a
            if not mostrar_ocultos and nombre.startswith("."):
                continue

            # Filtrar por extensión
            if extension and not nombre.endswith(extension):
                continue

            ruta_completa = os.path.join(directorio, nombre)

            # Si es directorio, agregar /
            if os.path.isdir(ruta_completa):
                print(nombre + "/")
            else:
                print(nombre)

        sys.exit(0)

    except Exception:
        print("Error al listar el directorio.")
        sys.exit(1)


if __name__ == "__main__":
    main()