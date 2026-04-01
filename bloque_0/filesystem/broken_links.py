import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Detecta enlaces simbólicos rotos."
    )

    parser.add_argument(
        "directorio",
        help="Directorio a analizar"
    )

    parser.add_argument(
        "--delete",
        action="store_true",
        help="Eliminar enlaces rotos (con confirmación)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mostrar solo el conteo"
    )

    args = parser.parse_args()

    base = Path(args.directorio)

    if not base.exists():
        print(f"Error: '{base}' no existe.")
        sys.exit(1)

    broken = []

    try:
        for path in base.rglob("*"):
            try:
                # Detectar symlink roto
                if path.is_symlink() and not path.exists():
                    broken.append(path)
            except PermissionError:
                continue

        # Modo quiet
        if args.quiet:
            print(len(broken))
            sys.exit(0)

        print(f"Buscando enlaces simbólicos rotos en {base}...\n")

        if not broken:
            print("No se encontraron enlaces rotos.")
            sys.exit(0)

        print("Enlaces rotos encontrados:")

        for path in broken:
            try:
                destino = os.readlink(path)
            except:
                destino = "desconocido"

            print(f"  {path} -> {destino} (no existe)")

        print(f"\nTotal: {len(broken)} enlaces rotos")

        # Opción delete
        if args.delete:
            for path in broken:
                confirm = input(f'¿Eliminar "{path}"? [s/N] ')
                if confirm.lower() == "s":
                    try:
                        path.unlink()
                        print(f"Eliminado: {path}")
                    except Exception:
                        print(f"Error al eliminar: {path}")

        sys.exit(0)

    except Exception:
        print("Error durante la búsqueda.")
        sys.exit(1)


if __name__ == "__main__":
    main()