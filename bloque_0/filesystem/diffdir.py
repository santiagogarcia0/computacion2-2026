import argparse
import sys
from pathlib import Path
import hashlib


# ------------------ UTIL ------------------

def hash_archivo(path):
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(4096):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None


def listar_archivos(base, recursive):
    archivos = {}

    if recursive:
        items = base.rglob("*")
    else:
        items = base.iterdir()

    for item in items:
        if item.is_file():
            # clave relativa (IMPORTANTE)
            rel = item.relative_to(base)
            archivos[str(rel)] = item

    return archivos


# ------------------ MAIN ------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compara dos directorios."
    )

    parser.add_argument("dir1")
    parser.add_argument("dir2")

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Comparar subdirectorios"
    )

    parser.add_argument(
        "--checksum",
        action="store_true",
        help="Comparar contenido (hash)"
    )

    args = parser.parse_args()

    dir1 = Path(args.dir1)
    dir2 = Path(args.dir2)

    if not dir1.exists() or not dir2.exists():
        print("Error: uno de los directorios no existe.")
        sys.exit(1)

    print(f"Comparando {dir1} con {dir2}...\n")

    archivos1 = listar_archivos(dir1, args.recursive)
    archivos2 = listar_archivos(dir2, args.recursive)

    set1 = set(archivos1.keys())
    set2 = set(archivos2.keys())

    solo1 = set1 - set2
    solo2 = set2 - set1
    comunes = set1 & set2

    # ------------------ SOLO EN DIR1 ------------------
    if solo1:
        print(f"Solo en {dir1}:")
        for f in sorted(solo1):
            print(f"  {f}")
        print()

    # ------------------ SOLO EN DIR2 ------------------
    if solo2:
        print(f"Solo en {dir2}:")
        for f in sorted(solo2):
            print(f"  {f}")
        print()

    mod_tamaño = []
    mod_fecha = []
    identicos = 0

    for f in comunes:
        p1 = archivos1[f]
        p2 = archivos2[f]

        stat1 = p1.stat()
        stat2 = p2.stat()

        # Comparar tamaño
        if stat1.st_size != stat2.st_size:
            mod_tamaño.append((f, stat1.st_size, stat2.st_size))
            continue

        # Comparar checksum (si se pide)
        if args.checksum:
            h1 = hash_archivo(p1)
            h2 = hash_archivo(p2)

            if h1 != h2:
                mod_tamaño.append((f, stat1.st_size, stat2.st_size))
                continue

        # Comparar fecha
        if int(stat1.st_mtime) != int(stat2.st_mtime):
            mod_fecha.append((f, stat1.st_mtime, stat2.st_mtime))
        else:
            identicos += 1

    # ------------------ RESULTADOS ------------------

    if mod_tamaño:
        print("Modificados (tamaño diferente):")
        for f, s1, s2 in mod_tamaño:
            print(f"  {f} ({s1} -> {s2} bytes)")
        print()

    if mod_fecha:
        print("Modificados (fecha diferente):")
        for f, t1, t2 in mod_fecha:
            print(f"  {f} ({int(t1)} -> {int(t2)})")
        print()

    print(f"Idénticos: {identicos} archivos")

    sys.exit(0)


if __name__ == "__main__":
    main()