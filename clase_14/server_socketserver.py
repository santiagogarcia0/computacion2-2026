#!/usr/bin/env python3
import socketserver
import sys
import time

PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
LENTO = float(sys.argv[sys.argv.index('--lento') + 1]) if '--lento' in sys.argv else 0.0

class EchoHandler(socketserver.StreamRequestHandler):
    def handle(self):
        """Atiende a un cliente usando abstracciones de archivos (rfile/wfile)."""
        if LENTO:
            time.sleep(LENTO)
        
        # self.rfile y self.wfile permiten leer y escribir como si fuera un archivo abierto
        while True:
            # Leemos bloques de datos (emulando el recv de 4096 bytes)
            datos = self.rfile.read(4096)
            if not datos:
                break
            self.wfile.write(datos)
            self.wfile.flush() # Forzamos el envío inmediato del buffer

class Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

def main():
    print(f'[socketserver] escuchando en 0.0.0.0:{PUERTO}'
          f'{f" (lento: {LENTO}s por cliente)" if LENTO else ""}')
    with Servidor(('0.0.0.0', PUERTO), EchoHandler) as servidor:
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print('\nServidor detenido')

if __name__ == '__main__':
    main()
