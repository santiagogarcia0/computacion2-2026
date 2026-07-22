#!/usr/bin/env python3

from multiprocessing import Process, Pipe


def hijo(conn):
    for i in range(5):
        # Recibe mensaje del padre
        mensaje = conn.recv()
        print(f"Hijo recibió: {mensaje}")

        # Responde al padre
        respuesta = f"Pong {i}"
        conn.send(respuesta)

    conn.close()


if __name__ == "__main__":
    padre_conn, hijo_conn = Pipe()

    p = Process(target=hijo, args=(hijo_conn,))
    p.start()

    for i in range(5):
        # Envía mensaje al hijo
        mensaje = f"Ping {i}"
        print(f"Padre envía: {mensaje}")
        padre_conn.send(mensaje)

        # Espera la respuesta
        respuesta = padre_conn.recv()
        print(f"Padre recibió: {respuesta}")

    padre_conn.close()

    p.join()

    print("Comunicación finalizada.")