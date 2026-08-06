import sys
from pathlib import Path
from multiprocessing import Queue

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.queue_utils import extraer_pids_de_cola


def test_extraer_pids_de_cola_drena_todos_los_items():
    cola = Queue()
    for pid in (101, 102, 103):
        cola.put(pid)

    assert extraer_pids_de_cola(cola) == [101, 102, 103]
