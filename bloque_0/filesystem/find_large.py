import argparse
import sys
from pathlib import Path


# ------------------ UTIL ------------------

def parse_size(size_str):
    try:
        unidad = size_str[-1].upper()
        valor = float(size_str[:-1])

        if unidad == "K":
            return int(valor * 1024)
        elif unidad == "M":
            return int(valor * 1024**2)
        elif unidad == "G":
            return int(valor * 1024**3)
        else:
            return int(size_str)
    except:
        raise argparse.ArgumentTypeError("Formato de tamaño inválido (ej: 100K, 1M, 2G)")


def format_size(bytes_size):
    if bytes_size >= 1024**3:
        return f"{bytes_size / 1024**3:.1f} GB"
    elif bytes_size >= 1024**2:
        return f"{bytes_size / 1024**2:.1f} MB"
    elif bytes_size >= 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size} B"


# ------------------ MAIN ------------------

def main():
    parser = argparse.ArgumentParser(
        description="Busca archivos grandes en un directorio."
    )

    parser.add_argument("directorio", help="Directorio a buscar")

    parser.add_argument(
        "--min-size",
        type=parse_size,
        default=0,
        help="Tamaño mínimo (ej: 100K, 1M, 2G)"
    )

    parser.add_argument(
        "--type",
        choices=["f", "d"],
        help="Filtrar por tipo (f=archivo, d=directorio)"
    )

    parser.add_argument(
        "--top",
        type=int,
        help="Mostrar solo los N más grandes"
    )

    args = parser.parse_args()

    ruta = Path(args.directorio)

    if not ruta.exists():
        print(f"Error: '{ruta}' no existe.")
        sys.exit(1)

    resultados = []

    try:
        for item in ruta.rglob("*"):
            try:
                if args.type == "f" and not item.is_file():
                    continue
                if args.type == "d" and not item.is_dir():
                    continue

                tamaño = item.stat().st_size

                if tamaño >= args.min_size:
                    resultados.append((item, tamaño))

            except PermissionError:
                continue

        if not resultados:
            print("No se encontraron resultados.")
            sys.exit(0)

        # Ordenar por tamaño descendente
        resultados.sort(key=lambda x: x[1], reverse=True)

        total_bytes = sum(t for _, t in resultados)

        # TOP N
        if args.top:
            print(f"Los {args.top} archivos más grandes:")
            resultados = resultados[:args.top]

        for i, (path, size) in enumerate(resultados, start=1):
            if args.top:
                print(f"  {i}. {path} ({format_size(size)})")
            else:
                print(f"{path} ({format_size(size)})")

        print(f"Total: {len(resultados)} archivos, {format_size(total_bytes)}")

        sys.exit(0)

    except Exception:
        print("Error durante la búsqueda.")
        sys.exit(1)


if __name__ == "__main__":
    main()