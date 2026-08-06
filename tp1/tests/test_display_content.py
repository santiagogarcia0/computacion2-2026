import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from display import construir_texto_resumen


class DisplayContentTests(unittest.TestCase):
    def test_resumen_incluye_datos_requeridos(self):
        datos_proceso = {
            "pid": 123,
            "ppid": 45,
            "usuario": "1000",
            "estado": "Sleeping",
            "threads": 4,
            "cpu_porc": 12.3,
            "rss": "2048 kB",
            "comando": "python3 app.py",
        }

        texto = construir_texto_resumen("123", datos_proceso)

        self.assertIn("PID 123", texto)
        self.assertIn("PPID", texto)
        self.assertIn("UID", texto)
        self.assertIn("Estado", texto)
        self.assertIn("Threads", texto)
        self.assertIn("CPU", texto)
        self.assertIn("RSS", texto)
        self.assertIn("Comando", texto)


if __name__ == "__main__":
    unittest.main()
