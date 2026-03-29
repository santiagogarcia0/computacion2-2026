import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Convierte temperaturas entre Celsius y Fahrenheit."
    )

    # Argumento posicional
    parser.add_argument(
        "valor",
        type=float,
        help="Temperatura a convertir"
    )

    # Opción obligatoria
    parser.add_argument(
        "-t", "--to",
        choices=["celsius", "fahrenheit"],
        required=True,
        help="Unidad de destino"
    )

    args = parser.parse_args()

    valor = args.valor
    destino = args.to

    try:
        if destino == "fahrenheit":
            resultado = (valor * 9/5) + 32
            print(f"{valor}°C = {resultado:.1f}°F")

        elif destino == "celsius":
            resultado = (valor - 32) * 5/9
            print(f"{valor}°F = {resultado:.2f}°C")

        sys.exit(0)

    except Exception:
        print("Error al convertir la temperatura.")
        sys.exit(1)


if __name__ == "__main__":
    main()