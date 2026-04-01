import argparse
import json
import sys
from pathlib import Path

# Archivo donde se guardan las tareas
RUTA = Path.home() / ".tareas.json"


# ------------------ UTILIDADES ------------------

def cargar_tareas():
    if not RUTA.exists():
        return []

    try:
        with open(RUTA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print("Error al leer el archivo de tareas.")
        sys.exit(1)


def guardar_tareas(tareas):
    try:
        with open(RUTA, "w", encoding="utf-8") as f:
            json.dump(tareas, f, indent=2, ensure_ascii=False)
    except Exception:
        print("Error al guardar las tareas.")
        sys.exit(1)


def siguiente_id(tareas):
    if not tareas:
        return 1
    return max(t["id"] for t in tareas) + 1


# ------------------ COMANDOS ------------------

def cmd_add(args):
    tareas = cargar_tareas()

    nueva = {
        "id": siguiente_id(tareas),
        "descripcion": args.descripcion,
        "done": False,
        "priority": args.priority
    }

    tareas.append(nueva)
    guardar_tareas(tareas)

    msg = f"Tarea #{nueva['id']} agregada"
    if args.priority:
        msg += f" (prioridad: {args.priority})"

    print(msg)
    sys.exit(0)


def cmd_list(args):
    tareas = cargar_tareas()

    for t in tareas:
        # filtros
        if args.pending and t["done"]:
            continue
        if args.done and not t["done"]:
            continue
        if args.priority and t["priority"] != args.priority:
            continue

        estado = "x" if t["done"] else " "
        linea = f"#{t['id']} [{estado}] {t['descripcion']}"

        if t["priority"]:
            linea += f" [{t['priority'].upper()}]"

        print(linea)

    sys.exit(0)


def cmd_done(args):
    tareas = cargar_tareas()

    for t in tareas:
        if t["id"] == args.id:
            t["done"] = True
            guardar_tareas(tareas)
            print(f"Tarea #{args.id} completada")
            sys.exit(0)

    print(f"Error: tarea #{args.id} no encontrada.")
    sys.exit(1)


def cmd_remove(args):
    tareas = cargar_tareas()

    for t in tareas:
        if t["id"] == args.id:
            confirm = input(f'¿Eliminar "{t["descripcion"]}"? [s/N] ')
            if confirm.lower() != "s":
                print("Cancelado.")
                sys.exit(0)

            tareas.remove(t)
            guardar_tareas(tareas)
            print(f"Tarea #{args.id} eliminada")
            sys.exit(0)

    print(f"Error: tarea #{args.id} no encontrada.")
    sys.exit(1)


# ------------------ MAIN ------------------

def main():
    parser = argparse.ArgumentParser(
        description="Gestor de tareas con subcomandos."
    )

    subparsers = parser.add_subparsers(dest="comando", required=True)

    # ----- add -----
    p_add = subparsers.add_parser("add", help="Agregar tarea")
    p_add.add_argument("descripcion", help="Descripción de la tarea")
    p_add.add_argument(
        "--priority",
        choices=["baja", "media", "alta"],
        help="Prioridad de la tarea"
    )
    p_add.set_defaults(func=cmd_add)

    # ----- list -----
    p_list = subparsers.add_parser("list", help="Listar tareas")
    p_list.add_argument("--pending", action="store_true", help="Solo pendientes")
    p_list.add_argument("--done", action="store_true", help="Solo completadas")
    p_list.add_argument(
        "--priority",
        choices=["baja", "media", "alta"],
        help="Filtrar por prioridad"
    )
    p_list.set_defaults(func=cmd_list)

    # ----- done -----
    p_done = subparsers.add_parser("done", help="Marcar tarea como completada")
    p_done.add_argument("id", type=int, help="ID de la tarea")
    p_done.set_defaults(func=cmd_done)

    # ----- remove -----
    p_remove = subparsers.add_parser("remove", help="Eliminar tarea")
    p_remove.add_argument("id", type=int, help="ID de la tarea")
    p_remove.set_defaults(func=cmd_remove)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception:
        print("Error inesperado.")
        sys.exit(1)


if __name__ == "__main__":
    main()