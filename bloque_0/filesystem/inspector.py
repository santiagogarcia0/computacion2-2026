import argparse
import os
import sys
import stat
from pathlib import Path
from datetime import datetime
import pwd
import grp


def formato_permisos(modo):
    return stat.filemode(modo)


def permisos_octal(modo):
    return oct(modo & 0o777)[2:]


def tipo_archivo(ruta):
    if ruta.is_symlink():
        return "enlace simbólico"
    elif ruta.is_dir():
        return "directorio"
    elif ruta.is_file():
        return "archivo regular"
    elif stat.S_ISCHR(ruta.stat().st_mode):
        return "dispositivo de caracteres"
    elif stat.S_ISBLK(ruta.stat().st_mode):
        return "dispositivo de bloques"
    else:
        return "otro"


def formatear_tiempo(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(
        description="Muestra información detallada de un archivo."
    )

    parser.add_argument("ruta", help="Ruta del archivo a inspeccionar")

    args = parser.parse_args()

    ruta = Path(args.ruta)

    if not ruta.exists() and not ruta.is_symlink():
        print(f"Error: '{ruta}' no existe.")
        sys.exit(1)

    try:
        info = ruta.lstat()  # importante para symlinks

        print(f"Archivo: {ruta}")

        tipo = tipo_archivo(ruta)
        print(f"Tipo: {tipo}", end="")

        if ruta.is_symlink():
            destino = os.readlink(ruta)
            print(f" -> {destino}")
        else:
            print()

        print(f"Tamaño: {info.st_size} bytes ({info.st_size / 1024:.2f} KB)")

        permisos_str = formato_permisos(info.st_mode)
        permisos_oct = permisos_octal(info.st_mode)
        print(f"Permisos: {permisos_str[1:]} ({permisos_oct})")

        try:
            usuario = pwd.getpwuid(info.st_uid).pw_name
        except KeyError:
            usuario = "desconocido"

        try:
            grupo = grp.getgrgid(info.st_gid).gr_name
        except KeyError:
            grupo = "desconocido"

        print(f"Propietario: {usuario} (uid: {info.st_uid})")
        print(f"Grupo: {grupo} (gid: {info.st_gid})")

        print(f"Inodo: {info.st_ino}")
        print(f"Enlaces duros: {info.st_nlink}")

        print(f"Creación: {formatear_tiempo(info.st_ctime)}")
        print(f"Última modificación: {formatear_tiempo(info.st_mtime)}")
        print(f"Último acceso: {formatear_tiempo(info.st_atime)}")

        if ruta.is_dir():
            try:
                contenido = len(list(ruta.iterdir()))
                print(f"Contenido: {contenido} elementos")
            except PermissionError:
                print("Contenido: acceso denegado")

        sys.exit(0)

    except Exception:
        print("Error al inspeccionar el archivo.")
        sys.exit(1)


if __name__ == "__main__":
    main()